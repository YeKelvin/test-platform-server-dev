#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : model.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from datetime import datetime

from sqlalchemy import UniqueConstraint

from app.database import DBModel
from app.database import db
from app.utils.log_util import get_logger


log = get_logger(__name__)


class TWorkspaceCollectionRel(DBModel):
    """空间集合关联表"""
    __tablename__ = 'WORKSPACE_COLLECTION_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    COLLECTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='测试集合编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TTestElement(DBModel):
    """测试元素表"""
    __tablename__ = 'TEST_ELEMENT'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ELEMENT_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='元素编号')
    ELEMENT_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    ELEMENT_REMARK = db.Column(db.String(512), comment='元素描述')
    ELEMENT_TYPE = db.Column(db.String(64), nullable=False, comment='元素类型')
    ELEMENT_CLASS = db.Column(db.String(64), nullable=False, comment='元素实现类')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    META_DATA = db.Column(db.String(512), comment='元数据')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TElementProperty(DBModel):
    """测试元素属性表"""
    __tablename__ = 'ELEMENT_PROPERTY'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ELEMENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='元素编号')
    PROPERTY_NAME = db.Column(db.String(256), nullable=False, comment='属性名称')
    PROPERTY_VALUE = db.Column(db.String(4096), comment='属性值')
    PROPERTY_TYPE = db.Column(db.String(32), nullable=False, default='STR', comment='属性类型')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    UniqueConstraint('ELEMENT_NO', 'PROPERTY_NAME', name='unique_elementno_propertyno')


class TElementChildRel(DBModel):
    """元素子代关联表"""
    __tablename__ = 'ELEMENT_CHILD_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ROOT_NO = db.Column(db.String(32), index=True, nullable=False, comment='根元素编号')
    PARENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='父元素编号')
    CHILD_NO = db.Column(db.String(32), index=True, nullable=False, comment='子元素编号')
    SERIAL_NO = db.Column(db.Integer, nullable=False, comment='子元素序号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TElementBuiltinChildRel(DBModel):
    """内置元素关联表"""
    __tablename__ = 'ELEMENT_BUILTIN_CHILD_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ROOT_NO = db.Column(db.String(32), index=True, nullable=False, comment='根元素编号')
    PARENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='父元素编号')
    CHILD_NO = db.Column(db.String(32), index=True, nullable=False, comment='子元素编号')
    CHILD_TYPE = db.Column(db.String(64), nullable=False, comment='子元素类型')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TVariableSet(DBModel):
    """变量集表"""
    __tablename__ = 'VARIABLE_SET'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), comment='空间编号')
    SET_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='变量集编号')
    SET_NAME = db.Column(db.String(128), nullable=False, comment='变量集名称')
    SET_TYPE = db.Column(db.String(128), nullable=False, comment='变量集类型: GLOBAL(全局), ENVIRONMENT(环境), CUSTOM(自定义)')
    SET_DESC = db.Column(db.String(256), comment='变量集描述')
    WEIGHT = db.Column(db.Integer, nullable=False, comment='权重')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    UniqueConstraint('WORKSPACE_NO', 'SET_NAME', 'SET_TYPE', name='unique_workspaceno_setname_settype')


class TVariable(DBModel):
    """变量表"""
    __tablename__ = 'VARIABLE'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    SET_NO = db.Column(db.String(32), index=True, nullable=False, comment='变量集编号')
    VAR_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='变量编号')
    VAR_NAME = db.Column(db.String(256), nullable=False, comment='变量名称')
    VAR_DESC = db.Column(db.String(256), comment='变量描述')
    INITIAL_VALUE = db.Column(db.String(2048), comment='变量值')
    CURRENT_VALUE = db.Column(db.String(2048), comment='当前值')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    UniqueConstraint('SET_NO', 'VAR_NAME', name='unique_setno_varname')


class THttpSamplerHeadersRel(DBModel):
    """元素请求头模板关联表"""
    __tablename__ = 'HTTP_SAMPLER_TEMPLATE_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    SAMPLER_NO = db.Column(db.String(32), index=True, nullable=False, comment='元素编号')
    TEMPLATE_NO = db.Column(db.String(32), index=True, nullable=False, comment='模板编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class THttpHeadersTemplate(DBModel):
    """请求头模板表"""
    __tablename__ = 'HTTP_HEADERS_TEMPLATE'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), comment='空间编号')
    TEMPLATE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='模板编号')
    TEMPLATE_NAME = db.Column(db.String(128), nullable=False, comment='模板名称')
    TEMPLATE_DESC = db.Column(db.String(256), comment='模板描述')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class THttpHeader(DBModel):
    """HTTP头部表"""
    __tablename__ = 'HTTP_HEADER'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    TEMPLATE_NO = db.Column(db.String(32), index=True, nullable=False, comment='模板编号')
    HEADER_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='请求头编号')
    HEADER_NAME = db.Column(db.String(256), nullable=False, comment='请求头名称')
    HEADER_VALUE = db.Column(db.String(1024), nullable=False, comment='请求头值')
    HEADER_DESC = db.Column(db.String(256), comment='请求头描述')
    ENABLED = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TSQLConfiguration(DBModel):
    """SQL配置表"""
    __tablename__ = 'SQL_CONFIGURATION'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    CONFIG_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='配置编号')
    CONFIG_NAME = db.Column(db.String(256), nullable=False, comment='配置名称')
    CONFIG_DESC = db.Column(db.String(256), nullable=False, comment='配置描述')
    CONNECTION_VARIABLE_NAME = db.Column(db.String(256), nullable=False, comment='数据库连接变量')
    DB_TYPE = db.Column(db.String(64), nullable=False, comment='数据库类型')
    DB_URL = db.Column(db.String(256), nullable=False, comment='数据库地址')
    USER_NAME = db.Column(db.String(256), nullable=False, comment='数据库用户名称')
    PASSWORD = db.Column(db.String(256), nullable=False, comment='数据库密码')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TElementTagRel(DBModel):
    """元素标签关联表"""
    __tablename__ = 'ELEMENT_TAG_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    ELEMENT_NO = db.Column(db.String(32), comment='元素编号')
    TAG_NO = db.Column(db.String(32), index=True, nullable=False, comment='标签编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TTestPlan(DBModel):
    """测试计划表"""
    __tablename__ = 'TESTPLAN'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), nullable=False, comment='空间编号')
    VERSION_NO = db.Column(db.String(128), comment='需求版本号')
    PLAN_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='计划编号')
    PLAN_NAME = db.Column(db.String(256), nullable=False, comment='计划名称')
    PLAN_DESC = db.Column(db.String(512), comment='计划描述')
    TOTAL = db.Column(db.Integer, nullable=False, default=0, comment='脚本总数')
    RUNNING_STATE = db.Column(db.String(64), comment='运行状态，待运行/运行中/已完成')
    SUCCESS_COUNT = db.Column(db.Integer, nullable=False, default=0, comment='成功脚本数')
    FAILURE_COUNT = db.Column(db.Integer, nullable=False, default=0, comment='失败脚本数')
    START_TIME = db.Column(db.DateTime, comment='开始时间')
    END_TIME = db.Column(db.DateTime, comment='结束时间')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TTestPlanSettings(DBModel):
    """测试计划设置表"""
    __tablename__ = 'TestPlanSettings'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    PLAN_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='计划编号')
    CONCURRENCY = db.Column(db.Integer, nullable=False, default=1, comment='并发数')
    ITERATIONS = db.Column(db.Integer, nullable=False, default=0, comment='计划迭代次数')
    DELAY = db.Column(db.Integer, nullable=False, default=0, comment='运行脚本的间隔时间，单位ms')
    SAVE = db.Column(db.Boolean, nullable=False, default=True, comment='是否保存数据至报告中')
    SAVE_ON_ERROR = db.Column(db.Boolean, nullable=False, default=True, comment='是否只保存失败的数据至报告中')
    STOP_TEST_ON_ERROR_COUNT = db.Column(db.Integer, default=0, comment='错误指定的错误后停止测试计划')
    USE_CURRENT_VALUE = db.Column(db.Boolean, nullable=False, default=False, comment='是否使用变量的当前值')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TTestPlanVariableSetRel(DBModel):
    """测试计划变量集关联表"""
    __tablename__ = 'TESTPLAN_VARIABLE_SET_REL'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    PLAN_NO = db.Column(db.String(32), index=True, nullable=False, comment='计划编号')
    SET_NO = db.Column(db.String(32), index=True, nullable=False, comment='变量集编号')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TTestPlanItem(DBModel):
    """测试计划项目明细表"""
    __tablename__ = 'TESTPLAN_ITEM'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    PLAN_NO = db.Column(db.String(32), index=True, nullable=False, comment='计划编号')
    COLLECTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='集合编号')
    SERIAL_NO = db.Column(db.Integer, nullable=False, comment='序号')
    RUNNING_STATE = db.Column(db.String(64), comment='运行状态，待运行/运行中/已完成')
    SUCCESS = db.Column(db.Boolean, comment='是否成功')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TTestReport(DBModel):
    """测试报告表"""
    __tablename__ = 'TEST_REPORT'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    WORKSPACE_NO = db.Column(db.String(32), nullable=False, comment='空间编号')
    PLAN_NO = db.Column(db.String(32), nullable=False, comment='计划编号')
    REPORT_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='报告编号')
    REPORT_NAME = db.Column(db.String(256), nullable=False, comment='报告名称')
    REPORT_DESC = db.Column(db.String(512), comment='报告描述')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TTestCollectionResult(DBModel):
    """测试集合结果表"""
    __tablename__ = 'TEST_COLLECTION_RESULT'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    REPORT_NO = db.Column(db.String(32), index=True, nullable=False, comment='报告编号')
    COLLECTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='集合编号')
    COLLECTION_ID = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='运行时集合的对象id')
    COLLECTION_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    COLLECTION_REMARK = db.Column(db.String(512), comment='元素描述')
    START_TIME = db.Column(db.DateTime, comment='开始时间')
    END_TIME = db.Column(db.DateTime, comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer, comment='耗时')
    SUCCESS = db.Column(db.Boolean, comment='是否成功')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TTestGroupResult(DBModel):
    """测试分组结果表"""
    __tablename__ = 'TEST_GROUP_RESULT'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    REPORT_NO = db.Column(db.String(32), index=True, nullable=False, comment='报告编号')
    COLLECTION_ID = db.Column(db.String(32), index=True, nullable=False, comment='运行时集合的对象id')
    GROUP_ID = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='运行时分组的对象id')
    GROUP_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    GROUP_REMARK = db.Column(db.String(512), comment='元素描述')
    START_TIME = db.Column(db.DateTime, comment='开始时间')
    END_TIME = db.Column(db.DateTime, comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer, comment='耗时')
    SUCCESS = db.Column(db.Boolean, comment='是否成功')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TTestSamplerResult(DBModel):
    """测试取样器结果表"""
    __tablename__ = 'TEST_SAMPLER_RESULT'
    ID = db.Column(db.Integer, primary_key=True)
    DEL_STATE = db.Column(db.Integer, nullable=False, default=0, comment='数据状态')
    REPORT_NO = db.Column(db.String(32), index=True, nullable=False, comment='报告编号')
    GROUP_ID = db.Column(db.String(32), index=True, nullable=False, comment='运行时分组的对象id')
    PARENT_ID = db.Column(db.String(32), comment='运行时子代取样器的父级的对象id')
    SAMPLER_ID = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='运行时取样器的对象id')
    SAMPLER_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    SAMPLER_REMARK = db.Column(db.String(512), comment='元素描述')
    START_TIME = db.Column(db.DateTime, comment='开始时间')
    END_TIME = db.Column(db.DateTime, comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer, comment='耗时')
    SUCCESS = db.Column(db.Boolean, comment='是否成功')
    REQUEST_URL = db.Column(db.String(4096), comment='请求地址')
    REQUEST_DATA = db.Column(db.String(4096), comment='请求数据')
    REQUEST_HEADERS = db.Column(db.String(4096), comment='请求头')
    RESPONSE_DATA = db.Column(db.String(4096), comment='响应数据')
    RESPONSE_HEADERS = db.Column(db.String(4096), comment='响应头')
    ERROR_ASSERTION = db.Column(db.String(4096), comment='失败断言数据')
    REMARK = db.Column(db.String(64), comment='备注')
    CREATED_BY = db.Column(db.String(64), comment='创建人')
    CREATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    UPDATED_BY = db.Column(db.String(64), comment='更新人')
    UPDATED_TIME = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
