#!/usr/bin/ python3
# @File    : execution_controller.py
# @Time    : 2020/3/20 15:00
# @Author  : Kelvin.Ye
from app.modules.script.controller import blueprint
from app.modules.script.service import execution_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.post('/collection/execute')
@require_login
@require_permission('RUN_ELEMENT')
def execute_collection():
    """运行测试集合"""
    req = JsonParser(
        Argument('socketId', required=True, nullable=False, help='sid 不能为空'),
        Argument('collectionNo', required=True, nullable=False, help='Collection 编号不能为空'),
        Argument('datasetNos', type=list, default=[]),
        Argument('useCurrentValue', type=bool, default=False)
    ).parse()
    return service.execute_collection(req)


@blueprint.post('/worker/execute')
@require_login
@require_permission('RUN_ELEMENT')
def execute_worker():
    """运行测试用例"""
    req = JsonParser(
        Argument('socketId', required=True, nullable=False, help='socketId不能为空'),
        Argument('workerNo', required=True, nullable=False, help='workerNo不能为空'),
        Argument('datasetNos', type=list, default=[]),
        Argument('useCurrentValue', type=bool, default=False),
        Argument('selfonly', type=bool, default=False)
    ).parse()
    return service.execute_worker(req)


@blueprint.post('/sampler/execute')
@require_login
@require_permission('RUN_ELEMENT')
def execute_sampler():
    """运行取样器"""
    req = JsonParser(
        Argument('socketId', required=True, nullable=False, help='sid不能为空'),
        Argument('samplerNo', required=True, nullable=False, help='Sampler 编号不能为空'),
        Argument('datasetNos', type=list, default=[]),
        Argument('useCurrentValue', type=bool, default=False),
        Argument('selfonly', type=bool, default=False)
    ).parse()
    return service.execute_sampler(req)


@blueprint.post('/snippets/execute')
@require_login
@require_permission('RUN_ELEMENT')
def execute_snippets():
    """运行片段集合"""
    req = JsonParser(
        Argument('socketId', required=True, nullable=False, help='sid 不能为空'),
        Argument('collectionNo', required=True, nullable=False, help='Collection 编号不能为空'),
        Argument('datasetNos', type=list, default=[]),
        Argument('variables', type=dict, default={}),
        Argument('useCurrentValue', type=bool, default=False)
    ).parse()
    return service.execute_snippets(req)


@blueprint.post('/testplan/execute')
@require_login
@require_permission('RUN_TESTPLAN')
def execute_testplan():
    """运行测试计划"""
    req = JsonParser(
        Argument('planNo', required=True, nullable=False, help='计划编号不能为空'),
        Argument('datasetNos', type=list, default=[]),
        Argument('useCurrentValue', type=bool, default=False)
    ).parse()
    return service.execute_testplan(req)


@blueprint.post('/testplan/execution/interrupt')
@require_login
@require_permission('INTERRUPT_TESTPLAN')
def interrupt_testplan():
    """中断运行测试计划"""
    req = JsonParser(
        Argument('executionNo', required=True, nullable=False, help='执行编号不能为空')
    ).parse()
    return service.interrupt_testplan(req)
