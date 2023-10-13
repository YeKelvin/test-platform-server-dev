#!/usr/bin/ python3
# @File    : model.py
# @Time    : 2019/11/14 9:50
# @Author  : Kelvin.Ye
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from app.database import BaseColumn
from app.database import TableModel
from app.database import db


class TWorkspaceCollection(TableModel, BaseColumn):
    """空间集合表"""
    __tablename__ = 'WORKSPACE_COLLECTION'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    COLLECTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='测试集合编号')


class TWorkspaceComponent(TableModel, BaseColumn):
    """空间组件表"""
    __tablename__ = 'WORKSPACE_COMPONENT'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    COMPONENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='组件编号')
    COMPONENT_TYPE = db.Column(db.String(64), nullable=False, comment='组件类型')
    COMPONENT_SORT = db.Column(db.Integer(), nullable=False, comment='组件序号')


class TTestElement(TableModel, BaseColumn):
    """测试元素表"""
    __tablename__ = 'TEST_ELEMENT'
    ELEMENT_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='元素编号')
    ELEMENT_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    ELEMENT_DESC = db.Column(db.String(512), comment='元素描述')
    ELEMENT_TYPE = db.Column(db.String(64), nullable=False, comment='元素类型')
    ELEMENT_CLASS = db.Column(db.String(64), nullable=False, comment='元素实现类')
    ELEMENT_ATTRS = db.Column(JSONB, comment='元素属性，与元素本身相关但不属于ElementProperty')
    ELEMENT_METADATA = db.Column(db.String(512), comment='元素的元数据')
    ENABLED = db.Column(JSONB, nullable=False, default=True, comment='是否启用')


class TElementProperty(TableModel, BaseColumn):
    """元素属性表"""
    __tablename__ = 'ELEMENT_PROPERTY'
    ELEMENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='元素编号')
    PROPERTY_TYPE = db.Column(db.String(32), nullable=False, default='STR', comment='属性类型')
    PROPERTY_NAME = db.Column(db.String(256), nullable=False, comment='属性名称')
    PROPERTY_VALUE = db.Column(db.Text(), comment='属性值')
    ENABLED = db.Column(db.Boolean(), nullable=False, default=True, comment='是否启用')
    UniqueConstraint('ELEMENT_NO', 'PROPERTY_NAME', 'DELETED', name='unique_element_property')


class TElementChildren(TableModel, BaseColumn):
    """元素子代表"""
    __tablename__ = 'ELEMENT_CHILDREN'
    ROOT_NO = db.Column(db.String(32), index=True, nullable=False, comment='根元素编号')
    PARENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='父元素编号')
    ELEMENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='子元素编号')
    ELEMENT_SORT = db.Column(db.Integer(), nullable=False, comment='子元素序号')


class TElementComponents(TableModel, BaseColumn):
    """元素组件表"""
    __tablename__ = 'ELEMENT_COMPONENTS'
    ROOT_NO = db.Column(db.String(32), index=True, nullable=False, comment='根元素编号')
    PARENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='父元素编号')
    ELEMENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='子元素编号')
    ELEMENT_TYPE = db.Column(db.String(64), nullable=False, comment='子元素类型')
    ELEMENT_SORT = db.Column(db.Integer(), nullable=False, comment='子元素序号')


class TElementChangelog(TableModel, BaseColumn):
    """元素变更日志表"""
    __tablename__ = 'ELEMENT_CHANGELOG'
    WORKSPACE_NO = db.Column(db.String(32), index=True, comment='空间编号')
    ROOT_NO = db.Column(db.String(32), index=True, comment='根元素编号')
    PARENT_NO = db.Column(db.String(32), index=True, comment='父元素编号')
    ELEMENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='元素编号')
    PROP_NAME = db.Column(db.String(256), comment='属性名称')
    ATTR_NAME = db.Column(db.String(256), comment='属性名称')
    OLD_VALUE = db.Column(db.Text(), comment='旧值')
    NEW_VALUE = db.Column(db.Text(), comment='新值')
    SOURCE_NO = db.Column(db.String(32), comment='来源编号')
    TARGET_NO = db.Column(db.String(32), comment='目标编号')
    SOURCE_INDEX = db.Column(db.Integer(), comment='来源序号')
    TARGET_INDEX = db.Column(db.Integer(), comment='目标序号')
    OPERATION_BY = db.Column(db.String(64), nullable=False, comment='操作人')
    OPERATION_TIME = db.Column(db.DateTime(), nullable=False, comment='操作时间')
    OPERATION_TYPE = db.Column(
        db.String(32),
        nullable=False,
        comment='操作类型: INSERT,UPDATE,DELETE,COPY,MOVE,ORDER,TRANSFER'
    )


class TVariableDataset(TableModel, BaseColumn):
    """变量集表"""
    __tablename__ = 'VARIABLE_DATASET'
    WORKSPACE_NO = db.Column(db.String(32), index=True, comment='空间编号')
    DATASET_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='变量集编号')
    DATASET_NAME = db.Column(db.String(128), nullable=False, comment='变量集名称')
    DATASET_TYPE = db.Column(
        db.String(128),
        nullable=False,
        comment=('变量集类型: GLOBAL(全局), WORKSPACE(空间), ENVIRONMENT(环境), CUSTOM(自定义)')
    )
    DATASET_DESC = db.Column(db.String(256), comment='变量集描述')
    DATASET_WEIGHT = db.Column(db.Integer(), nullable=False, comment='权重')
    DATASET_BINDING = db.Column(db.String(32), comment='环境绑定，用于限制自定义变量')
    UniqueConstraint('WORKSPACE_NO', 'DATASET_NAME', 'DATASET_TYPE', 'DELETED', name='unique_workspace_dataset')


class TVariable(TableModel, BaseColumn):
    """变量表"""
    __tablename__ = 'VARIABLE'
    DATASET_NO = db.Column(db.String(32), index=True, nullable=False, comment='变量集编号')
    VAR_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='变量编号')
    VAR_NAME = db.Column(db.Text(), nullable=False, comment='变量名称')
    VAR_DESC = db.Column(db.String(256), comment='变量描述')
    INITIAL_VALUE = db.Column(db.String(2048), comment='变量值')
    CURRENT_VALUE = db.Column(db.String(2048), comment='当前值')
    ENABLED = db.Column(db.Boolean(), nullable=False, default=True, comment='是否启用')
    UniqueConstraint('DATASET_NO', 'VAR_NAME', 'DELETED', name='unique_dataset_variable')


class THttpHeaderTemplate(TableModel, BaseColumn):
    """请求头模板表"""
    __tablename__ = 'HTTP_HEADER_TEMPLATE'
    WORKSPACE_NO = db.Column(db.String(32), index=True, comment='空间编号')
    TEMPLATE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='模板编号')
    TEMPLATE_NAME = db.Column(db.String(128), nullable=False, comment='模板名称')
    TEMPLATE_DESC = db.Column(db.String(256), comment='模板描述')
    UniqueConstraint('WORKSPACE_NO', 'TEMPLATE_NAME', 'DELETED', name='unique_workspace_template')


class THttpHeader(TableModel, BaseColumn):
    """HTTP头部表"""
    __tablename__ = 'HTTP_HEADER'
    TEMPLATE_NO = db.Column(db.String(32), index=True, nullable=False, comment='模板编号')
    HEADER_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='请求头编号')
    HEADER_NAME = db.Column(db.String(256), nullable=False, comment='请求头名称')
    HEADER_VALUE = db.Column(db.Text(), nullable=False, comment='请求头值')
    HEADER_DESC = db.Column(db.String(256), comment='请求头描述')
    ENABLED = db.Column(db.Boolean(), nullable=False, default=True, comment='是否启用')
    UniqueConstraint('TEMPLATE_NO', 'HEADER_NAME', 'DELETED', name='unique_template_header')


class TDatabaseConfig(TableModel, BaseColumn):
    """数据库配置表"""
    __tablename__ = 'DATABASE_CONFIG'
    WORKSPACE_NO = db.Column(db.String(32), index=True, comment='空间编号')
    DB_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='数据库编号')
    DB_NAME = db.Column(db.String(256), nullable=False, comment='数据库名称')
    DB_DESC = db.Column(db.String(256), comment='数据库描述')
    DB_TYPE = db.Column(db.String(64), nullable=False, comment='数据库类型')
    USERNAME = db.Column(db.String(256), nullable=False, comment='数据库用户名称')
    PASSWORD = db.Column(db.String(256), nullable=False, comment='数据库用户密码')
    HOST = db.Column(db.String(128), nullable=False, comment='数据库主机')
    PORT = db.Column(db.String(32), nullable=False, comment='数据库端口')
    QUERY = db.Column(db.String(256), comment='数据库主机地址')
    DATABASE = db.Column(db.String(256), nullable=False, comment='数据库库名')
    VARIABLE_NAME = db.Column(db.String(256), nullable=False, comment='存储数据库对象的变量名称')
    CONNECT_TIMEOUT = db.Column(db.String(128), nullable=False, comment='连接超时时间')


class TElementTag(TableModel, BaseColumn):
    """元素标签表"""
    __tablename__ = 'ELEMENT_TAG'
    ELEMENT_NO = db.Column(db.String(32), index=True, nullable=False, comment='元素编号')
    TAG_NO = db.Column(db.String(32), index=True, nullable=False, comment='标签编号')


class TTestplan(TableModel, BaseColumn):
    """测试计划表"""
    __tablename__ = 'TESTPLAN'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    PLAN_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='计划编号')
    PLAN_NAME = db.Column(db.String(256), nullable=False, comment='计划名称')
    PLAN_DESC = db.Column(db.String(512), comment='计划描述')
    PLAN_STATE = db.Column(db.String(64), comment='计划状态，待开始/进行中/已完成')
    SCRUM_SPRINT = db.Column(db.String(128), comment='迭代')
    SCRUM_VERSION = db.Column(db.String(128), comment='版本')
    COLLECTIONS = db.Column(JSONB, comment='计划脚本列表')
    COLLECTION_TOTAL = db.Column(db.Integer(), nullable=False, default=0, comment='脚本总数')
    TEST_PHASE = db.Column(db.String(64), comment='测试阶段，待测试/冒烟测试/系统测试/回归测试/已完成')
    START_TIME = db.Column(db.DateTime(), comment='开始时间')
    END_TIME = db.Column(db.DateTime(), comment='结束时间')
    SETTINGS = db.Column(JSONB, comment='计划设置')


class TTestplanExecution(TableModel, BaseColumn):
    """测试计划执行记录表"""
    __tablename__ = 'TESTPLAN_EXECUTION'
    PLAN_NO = db.Column(db.String(32), index=True, nullable=False, comment='计划编号')
    EXECUTION_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='执行编号')
    EXECUTION_STATE = db.Column(db.String(64), comment='运行状态，待运行/运行中/迭代中/已完成/已中断')
    ITER_COUNT = db.Column(db.Integer(), nullable=False, default=0, comment='执行次数')
    TEST_PHASE = db.Column(db.String(64), comment='测试阶段')
    ENVIRONMENT = db.Column(db.String(128), comment='测试环境')
    START_TIME = db.Column(db.DateTime(), comment='开始时间')
    END_TIME = db.Column(db.DateTime(), comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer(), comment='执行耗时')
    SETTINGS = db.Column(JSONB, comment='执行设置')
    INTERRUPT = db.Column(db.Boolean, nullable=False, default=False, comment='是否中断运行')
    INTERRUPT_BY = db.Column(db.String(64), comment='中断人')
    INTERRUPT_TIME = db.Column(db.DateTime(), comment='中断时间')


class TTestplanExecutionCollection(TableModel, BaseColumn):
    """测试计划执行脚本表"""
    __tablename__ = 'TESTPLAN_EXECUTION_COLLECTION'
    EXECUTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='执行编号')
    COLLECTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='集合编号')
    RUNNING_STATE = db.Column(db.String(64), comment='运行状态，待运行/运行中/已完成')
    ITER_COUNT = db.Column(db.Integer(), nullable=False, default=0, comment='迭代次数')
    ERROR_COUNT = db.Column(db.Integer(), nullable=False, default=0, comment='异常次数')
    SUCCESS_COUNT = db.Column(db.Integer(), nullable=False, default=0, comment='成功次数')
    FAILURE_COUNT = db.Column(db.Integer(), nullable=False, default=0, comment='失败次数')


class TTestReport(TableModel, BaseColumn):
    """测试报告表"""
    __tablename__ = 'TEST_REPORT'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    PLAN_NO = db.Column(db.String(32), index=True, nullable=False, comment='计划编号')
    EXECUTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='执行编号')
    REPORT_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='报告编号')
    REPORT_NAME = db.Column(db.String(256), nullable=False, comment='报告名称')
    REPORT_DESC = db.Column(db.String(512), comment='报告描述')
    START_TIME = db.Column(db.DateTime(), comment='开始时间')
    END_TIME = db.Column(db.DateTime(), comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer(), comment='耗时')


class TTestCollectionResult(TableModel, BaseColumn):
    """测试集合结果表"""
    __tablename__ = 'TEST_COLLECTION_RESULT'
    REPORT_NO = db.Column(db.String(32), index=True, nullable=False, comment='报告编号')
    COLLECTION_NO = db.Column(db.String(32), index=True, nullable=False, comment='集合编号')
    COLLECTION_ID = db.Column(db.String(32), index=True, nullable=False, comment='集合ID')
    COLLECTION_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    COLLECTION_DESC = db.Column(db.String(512), comment='元素描述')
    START_TIME = db.Column(db.DateTime(), comment='开始时间')
    END_TIME = db.Column(db.DateTime(), comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer(), comment='耗时')
    SUCCESS = db.Column(db.Boolean(), comment='是否成功')


class TTestWorkerResult(TableModel, BaseColumn):
    """测试工作者结果表"""
    __tablename__ = 'TEST_WORKER_RESULT'
    REPORT_NO = db.Column(db.String(32), index=True, nullable=False, comment='报告编号')
    COLLECTION_ID = db.Column(db.String(32), index=True, nullable=False, comment='集合ID')
    WORKER_ID = db.Column(db.String(32), index=True, nullable=False, comment='工作者ID')
    WORKER_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    WORKER_DESC = db.Column(db.String(512), comment='元素描述')
    START_TIME = db.Column(db.DateTime(), comment='开始时间')
    END_TIME = db.Column(db.DateTime(), comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer(), comment='耗时')
    SUCCESS = db.Column(db.Boolean(), comment='是否成功')


class TTestSamplerResult(TableModel, BaseColumn):
    """测试取样器结果表"""
    __tablename__ = 'TEST_SAMPLER_RESULT'
    REPORT_NO = db.Column(db.String(32), index=True, nullable=False, comment='报告编号')
    COLLECTION_ID = db.Column(db.String(32), index=True, nullable=False, comment='集合ID')
    WORKER_ID = db.Column(db.String(32), index=True, nullable=False, comment='工作者ID')
    PARENT_ID = db.Column(db.String(32), index=True, comment='父级取样器ID')
    SAMPLER_ID = db.Column(db.String(32), index=True, nullable=False, comment='运行时取样器的对象id')
    SAMPLER_NAME = db.Column(db.String(256), nullable=False, comment='元素名称')
    SAMPLER_DESC = db.Column(db.String(512), comment='元素描述')
    START_TIME = db.Column(db.DateTime(), comment='开始时间')
    END_TIME = db.Column(db.DateTime(), comment='结束时间')
    ELAPSED_TIME = db.Column(db.Integer(), comment='耗时')
    SUCCESS = db.Column(db.Boolean(), comment='是否成功')
    RETRYING = db.Column(db.Boolean(), comment='重试中')
    REQUEST_URL = db.Column(db.Text(), comment='请求地址')
    REQUEST_HEADERS = db.Column(db.Text(), comment='请求头')
    REQUEST_DATA = db.Column(db.Text(), comment='请求数据')
    REQUEST_DECODED = db.Column(db.Text(), comment='解码后的请求数据')
    RESPONSE_CODE = db.Column(db.Text(), comment='响应码')
    RESPONSE_HEADERS = db.Column(db.Text(), comment='响应头')
    RESPONSE_DATA = db.Column(db.Text(), comment='响应数据')
    RESPONSE_DECODED = db.Column(db.Text(), comment='解码后的响应数据')
    # ASSERTIONS = db.Column(db.Text(), comment='断言数据')
    FAILED_ASSERTION = db.Column(db.Text(), comment='失败断言数据') # TODO: delete
