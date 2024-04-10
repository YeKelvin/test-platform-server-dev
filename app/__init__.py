#!/usr/bin/ python3
# @File    : __init__.py
# @Time    : 2019/11/7 9:39
# @Author  : Kelvin.Ye
from inspect import unwrap

import orjson

from apscheduler.events import EVENT_ALL
from apscheduler.events import EVENT_JOB_ADDED
from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.events import EVENT_JOB_MAX_INSTANCES
from apscheduler.events import EVENT_JOB_MODIFIED
from apscheduler.events import EVENT_JOB_REMOVED
from apscheduler.events import EVENT_JOB_SUBMITTED
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import Blueprint
from flask import Flask
from flask.json.provider import JSONProvider

from app import config as CONFIG
from app.extension import apscheduler
from app.extension import db
from app.extension import migrate
from app.extension import socketio


__app__ = None


class ORJSONProvider(JSONProvider):
    def __init__(self, *args, **kwargs):
        self.options = kwargs
        super().__init__(*args, **kwargs)

    def loads(self, s, **kwargs):
        return orjson.loads(s)

    def dumps(self, obj, **kwargs):
        return orjson.dumps(obj, option=orjson.OPT_NON_STR_KEYS).decode('utf-8')


def create_app() -> Flask:
    app = Flask(__name__)
    app.json = ORJSONProvider(app)
    configure_flask(app)
    register_extensions(app)
    register_blueprints(app)
    register_hooks(app)
    register_shell_context(app)
    register_commands(app)
    init_openapi(app)
    init_api_doc(app)
    set_app(app)
    return app


def set_app(app: Flask):
    global __app__

    __app__ = app


def get_app() -> Flask:
    global __app__

    if __app__ is None:
        raise RuntimeError('Please call create_app() first!!!')
    return __app__


def configure_flask(app: Flask):
    # https://viniciuschiele.github.io/flask-apscheduler/rst/api.html
    scheduler_api_enabled = False
    if app.debug:
        scheduler_api_enabled = True
        scheduler_executors = {'default': {'type': 'threadpool', 'max_workers': 10}}
    else:
        scheduler_executors = {'default': {'type': 'gevent'}}

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=CONFIG.DB_URL,
        SQLALCHEMY_COMMIT_ON_TEARDOWN=True,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            # 使用将来版本的特性
            'future': True,
            # 连接池实现类
            # 'poolclass': QueuePool,
            # 连接池大小
            # 'pool_size': 10,
            # 连接回收时间，这个值必须要比数据库自身配置的 interactive_timeout 的值小
            # 'pool_recycle': 1000,
            # 预检测池中连接是否有效，并替换无效连接
            # 'pool_pre_ping': True,
            # 会打印输出连接池的异常信息，帮助排查问题
            # 'echo_pool': True,
            # 最大允许溢出连接池大小的连接数量
            # 'max_overflow': 5,
            # 自定义序列化函数
            'json_serializer': orjson_serializer,
            # 自定义反序列化函数
            'json_deserializer': orjson_deserializer
        },
        SCHEDULER_API_ENABLED=scheduler_api_enabled,
        SCHEDULER_EXECUTORS=scheduler_executors,
        SCHEDULER_JOBSTORES={'default': SQLAlchemyJobStore(url=CONFIG.DB_URL)},
        SCHEDULER_JOB_DEFAULTS={'coalesce': True, 'max_instances': CONFIG.SCHEDULE_JOB_INSTANCES_MAX},
        SCHEDULER_TIMEZONE='Asia/Shanghai'
    )


def register_extensions(app: Flask):
    """Register Flask extensions"""
    from app import signals  # noqa
    from app import socketx  # noqa

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    init_apscheduler(app)


def init_apscheduler(app: Flask):
    from app.modules.schedule import event

    apscheduler.add_listener(event.handle_event_all, EVENT_ALL)
    apscheduler.add_listener(event.handle_job_error, EVENT_JOB_ERROR)
    apscheduler.add_listener(event.handle_job_added, EVENT_JOB_ADDED)
    apscheduler.add_listener(event.handle_job_removed, EVENT_JOB_REMOVED)
    apscheduler.add_listener(event.handle_job_modified, EVENT_JOB_MODIFIED)
    apscheduler.add_listener(event.handle_job_executed, EVENT_JOB_EXECUTED)
    apscheduler.add_listener(event.handle_job_submitted, EVENT_JOB_SUBMITTED)
    apscheduler.add_listener(event.handle_job_max_instances, EVENT_JOB_MAX_INSTANCES)
    apscheduler.init_app(app)
    apscheduler.start()


def register_blueprints(app: Flask):
    """Register Flask blueprints"""
    from app.modules import restapi
    from app.openapi import api as openapi

    app.register_blueprint(restapi)
    app.register_blueprint(openapi)


def register_hooks(app: Flask):
    from app import hook

    app.before_request(hook.inject_traceid)
    app.before_request(hook.inject_ip)

    if app.debug:
        app.after_request(hook.cross_domain_access)


def register_shell_context(app: Flask):
    """Register shell context objects"""

    def shell_context():
        return {'db': db}

    app.shell_context_processor(shell_context)


def register_commands(app: Flask):
    """Register Click commands"""
    from app import command

    app.cli.add_command(command.newid)
    app.cli.add_command(command.initdb)
    app.cli.add_command(command.initdata)
    # app.cli.add_command(command.dropdb)
    app.cli.add_command(command.create_table)


def orjson_serializer(obj):
    """Note that `orjson.dumps()` return byte array, while sqlalchemy expects string, thus `decode()` call."""
    return orjson.dumps(obj, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NAIVE_UTC).decode('utf8')


def orjson_deserializer(val):
    return orjson.loads(val)


def init_openapi(app: Flask):
    """将RestAPI自动注册为OpenAPI"""
    from app.tools.require import require_open_permission

    blueprint = Blueprint('autoapi', __name__, url_prefix='/openapi')
    exclude_modules = ['opencenter', 'usercenter', 'system']
    required_methods = {'GET', 'POST', 'PUT', 'DELETE'}
    for api in app.url_map.iter_rules():
        if not (api.methods & required_methods):
            continue
        if not api.endpoint.startswith('restapi.'):
            continue
        if any(module in api.endpoint for module in exclude_modules):
            continue
        func = unwrap(app.view_functions[api.endpoint])
        endpoint = f'open__{func.__name__}'
        blueprint.add_url_rule(
            rule=api.rule.replace('/restapi', ''),
            methods=[*api.methods],
            endpoint=endpoint,
            view_func=require_open_permission(func),
        )
    app.register_blueprint(blueprint)


def init_api_doc(app: Flask):
    """缓存接口路径和描述，用于记录请求日志"""
    from app.tools.cache import API_DOC_STORAGER

    required_methods = ['GET', 'POST', 'PUT', 'DELETE']
    for api in app.url_map.iter_rules():
        method = None
        for m in api.methods:
            if m in required_methods:
                method = m
        if not method:
            continue
        API_DOC_STORAGER[f'{method}://{api.rule}'] = app.view_functions[api.endpoint].__doc__
