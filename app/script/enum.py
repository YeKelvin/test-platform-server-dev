#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : enum.py
# @Time    : 2020/7/3 15:23
# @Author  : Kelvin.Ye
from enum import unique

from common.enums import BaseEnum


@unique
class ElementType(BaseEnum):

    # 测试集合
    COLLECTION = 'COLLECTION'

    # 测试组
    GROUP = 'GROUP'

    # 取样器
    SAMPLER = 'SAMPLER'

    # 逻辑控制器
    CONTROLLER = 'CONTROLLER'

    # 配置器
    CONFIG = 'CONFIG'

    # 时间控制器
    TIMER = 'TIMER'

    # 前置处理器
    PRE_PROCESSOR = 'PRE_PROCESSOR'

    # 后置处理器
    POST_PROCESSOR = 'POST_PROCESSOR'

    # 断言器
    ASSERTION = 'ASSERTION'

    # 监听器
    LISTENER = 'LISTENER'


@unique
class ElementClass(BaseEnum):

    # 测试集合
    TEST_COLLECTION = 'TestCollection'

    # 片段集合
    TEST_SNIPPETS = 'TestSnippets'

    # 测试组
    TEST_GROUP = 'TestGroup'

    # 前置分组
    SETUP_GROUP = 'SetupGroup'

    # 后置分组
    TEARDOWN_GROUP = 'TeardownGroup'

    # HTTP取样器
    HTTP_SAMPLER = 'HTTPSampler'

    # Python取样器
    PYTHON_SAMPLER = 'PythonSampler'

    # Snippet取样器
    SNIPPET_SAMPLER = 'SnippetSampler'

    # SQL取样器
    SQL_SAMPLER = 'SQLSampler'

    # HTTP头部配置器
    HTTP_HEADER_MANAGER = 'HTTPHeaderManager'

    # Loop控制器
    LOOP_CONTROLLER = 'LoopController'

    # If控制器
    IF_CONTROLLER = 'IfController'

    # While控制器
    WHILE_CONTROLLER = 'WhileController'

    # Transaction控制器
    TRANSACTION_CONTROLLER = 'TransactionController'

    # Python前置处理器
    PYTHON_PRE_PROCESSOR = 'PythonPreProcessor'

    # Python后置处理器
    PYTHON_POST_PROCESSOR = 'PythonPostProcessor'

    # JsonPath提取器
    JSON_PATH_EXTRACTOR = 'JsonPathExtractor'

    # Python断言器
    PYTHON_ASSERTION = 'PythonAssertion'

    # JsonPath断言器
    JSON_PATH_ASSERTION = 'JsonPathAssertion'


@unique
class ElementStatus(BaseEnum):

    # 启用
    ENABLE = True

    # 禁用
    DISABLE = False


@unique
class VariableDatasetType(BaseEnum):

    # 全局变量：与环境无关，与工作空间无关
    GLOBAL = 'GLOBAL'

    # 环境变量：与环境相关，与工作空间相关
    ENVIRONMENT = 'ENVIRONMENT'

    # 自定义变量：与环境无关，与工作空间相关
    CUSTOM = 'CUSTOM'


@unique
class VariableDatasetWeight(BaseEnum):

    # 全局变量
    GLOBAL = 1

    # 环境变量
    ENVIRONMENT = 2

    # 自定义变量
    CUSTOM = 3


@unique
class RunningState(BaseEnum):

    # 待运行
    WAITING = 'WAITING'

    # 运行中
    RUNNING = 'RUNNING'

    # 已完成
    COMPLETED = 'COMPLETED'

    # 异常
    ERROR = 'ERROR'


@unique
class TestplanState(BaseEnum):

    # 待开始
    INITIAL = 'INITIAL'

    # 测试中
    TESTING = 'TESTING'

    # 已完成
    COMPLETED = 'COMPLETED'


@unique
class TestPhase(BaseEnum):

    # 待测试
    INITIAL = 'INITIAL'

    # 调试
    DEBUG = 'DEBUG'

    # 冒烟测试
    SMOKE_TESTING = 'SMOKE_TESTING'

    # 系统测试
    SYSTEM_TESTING = 'SYSTEM_TESTING'

    # 回归测试
    REGRESSION_TESTING = 'REGRESSION_TESTING'

    # 验收测试
    ACCEPTANCE_TESTING = 'ACCEPTANCE_TESTING'

    # 已完成
    COMPLETED = 'COMPLETED'


@unique
class PasteType(BaseEnum):

    # 复制
    COPY = 'COPY'

    # 剪切
    CUT = 'CUT'


# def is_collection(element):
#     return element.ELEMENT_TYPE == ElementType.COLLECTION
#
#
# def is_group(element):
#     return element.ELEMENT_TYPE == ElementType.GROUP
#
#
# def is_sampler(element):
#     return element.ELEMENT_TYPE == ElementType.SAMPLER
#
#
# def is_config(element):
#     return element.ELEMENT_TYPE == ElementType.CONFIG
#
#
# def is_controller(element):
#     return element.ELEMENT_TYPE == ElementType.CONTROLLER
#
#
# def is_timer(element):
#     return element.ELEMENT_TYPE == ElementType.TIMER
#
#
# def is_pre_processor(element):
#     return element.ELEMENT_TYPE == ElementType.PRE_PROCESSOR
#
#
# def is_post_processor(element):
#     return element.ELEMENT_TYPE == ElementType.POST_PROCESSOR
#
#
# def is_assertion(element):
#     return element.ELEMENT_TYPE == ElementType.ASSERTION
#
#
# def is_listener(element):
#     return element.ELEMENT_TYPE == ElementType.LISTENER
