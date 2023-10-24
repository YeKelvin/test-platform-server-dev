#!/usr/bin python3
# @File    : element_reveiver.py
# @Time    : 2023-09-26 16:27:14
# @Author  : Kelvin.Ye
from contextvars import ContextVar

from flask import request
from sqlalchemy import select
from sqlalchemy import union_all

from app.database import db_execute
from app.modules.script.dao import test_element_dao
from app.modules.script.enum import ElementOperationType
from app.modules.script.enum import ElementType
from app.modules.script.model import TElementChangelog
from app.modules.script.model import TElementChildren
from app.modules.script.model import TElementComponents
from app.modules.script.model import TTestElement
from app.signals import element_copied_signal
from app.signals import element_created_signal
from app.signals import element_modified_signal
from app.signals import element_moved_signal
from app.signals import element_removed_signal
from app.signals import element_sorted_signal
from app.signals import element_transferred_signal
from app.tools import localvars
from app.tools.exceptions import ServiceError
from app.utils.time_util import datetime_now_by_utc8


localvar__element_nodes = ContextVar('ELEMENT_NODES', default=None)
localvar__root_no = ContextVar('ROOT_NO', default=None)
localvar__case_no = ContextVar('CASE_NO', default=None)
localvar__parents = ContextVar('PARENTS', default=None)



def get_workspace_no():
    """获取当前空间编号"""
    if workspace_no := request.headers.get('x-workspace-no'):
        return workspace_no
    else:
        raise ServiceError('获取空间编号失败')


def get_node(element_no):
    """没有子代节点也没有组件节点的就是空间组件"""
    child_stmt = (
        select(
            TElementChildren.ROOT_NO,
            TElementChildren.PARENT_NO,
            TTestElement.ELEMENT_TYPE.label('PARENT_TYPE')
        )
        .join(TTestElement, TTestElement.ELEMENT_NO == TElementChildren.PARENT_NO)
        .where(TElementChildren.ELEMENT_NO == element_no)
    )

    compo_stmt = (
        select(
            TElementComponents.ROOT_NO,
            TElementComponents.PARENT_NO,
            TTestElement.ELEMENT_TYPE.label('PARENT_TYPE')
        )
        .join(TTestElement, TTestElement.ELEMENT_NO == TElementComponents.PARENT_NO)
        .where(TElementComponents.ELEMENT_NO == element_no)
    )

    return db_execute(union_all(child_stmt, compo_stmt)).first()


def get_element_node(element_no):
    """获取元素节点信息"""
    nodes = localvar__element_nodes.get()
    if not nodes:
        nodes = {}
        localvar__element_nodes.set(nodes)
    if element_no in nodes:
        return nodes[element_no]

    entity = get_node(element_no)
    nodes[element_no] = entity
    return entity

def get_root_no(element_no):
    """获取根元素编号"""
    root_no = localvar__root_no.get()
    if not root_no:
        node = get_element_node(element_no)
        root_no = node.ROOT_NO if node else None
        localvar__root_no.set(root_no)
    return root_no


def get_worker_no(parent_no):
    stmt = (
        select(
            TElementChildren.ROOT_NO,
            TElementChildren.PARENT_NO,
            TTestElement.ELEMENT_TYPE.label('PARENT_TYPE')
        )
        .join(TTestElement, TTestElement.ELEMENT_NO == TElementChildren.PARENT_NO)
        .where(TElementChildren.ELEMENT_NO == parent_no)
    )
    node = db_execute(stmt).first()
    if node.PARENT_TYPE == ElementType.WORKER.value:
        return node.PARENT_NO
    return get_worker_no(node.PARENT_NO) # 找不到时继续递归往上层找


def get_case_no(element_no):
    """获取用例编号"""
    case_no = localvar__case_no.get()
    if not case_no:
        node = get_element_node(element_no)
        if not node:
            return None
        case_no = node.PARENT_NO if node.PARENT_TYPE == ElementType.COLLECTION.value else get_worker_no(node.PARENT_NO)
        localvar__case_no.set(case_no)
    return case_no


def get_parent_no(element_no):
    """获取父级编号"""
    parents = localvar__parents.get()
    if not parents:
        parents = {}
        localvar__parents.set(parents)
    if element_no in parents:
        return parents[element_no]

    node = get_element_node(element_no)
    parents[element_no] = node.PARENT_NO if node else None
    return node.PARENT_NO


@element_created_signal.connect
def record_create_element(sender, root_no, parent_no, element_no):
    case_no = None
    if parent_no:
        parent = test_element_dao.select_by_no(parent_no)
        case_no = parent_no if parent.ELEMENT_TYPE == ElementType.WORKER.value else get_worker_no(parent_no)
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=root_no,
        CASE_NO=case_no,
        PARENT_NO=parent_no,
        ELEMENT_NO=element_no,
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.INSERT.value
    )


@element_modified_signal.connect
def record_modify_element(sender, element_no, prop_name=None, attr_name=None, old_value=None, new_value=None):
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=get_root_no(element_no),
        CASE_NO=get_case_no(element_no),
        PARENT_NO=get_parent_no(element_no),
        ELEMENT_NO=element_no,
        PROP_NAME=prop_name,
        ATTR_NAME=attr_name,
        OLD_VALUE=old_value,
        NEW_VALUE=new_value,
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.UPDATE.value
    )


@element_removed_signal.connect
def record_remove_element(sender, element_no):
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=get_root_no(element_no),
        CASE_NO=get_case_no(element_no),
        PARENT_NO=get_parent_no(element_no),
        ELEMENT_NO=element_no,
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.DELETE.value
    )


@element_moved_signal.connect
def record_move_element(sender, source_no, target_no):
    """不同父级下叫移动"""
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=get_root_no(source_no),
        CASE_NO=get_case_no(source_no),
        PARENT_NO=get_parent_no(source_no),
        ELEMENT_NO=source_no,
        SOURCE_NO=source_no,
        TARGET_NO=target_no, # target的父级
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.MOVE.value
    )


@element_sorted_signal.connect
def record_order_element(sender, element_no, source_index, target_index):
    """相同父级下叫排序"""
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=get_root_no(element_no),
        CASE_NO=get_case_no(element_no),
        PARENT_NO=get_parent_no(element_no),
        ELEMENT_NO=element_no,
        SOURCE_INDEX=source_index,
        TARGET_INDEX=target_index,
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.ORDER.value
    )


@element_copied_signal.connect
def record_copy_element(sender, element_no, source_no):
    TElementChangelog.insert(
        WORKSPACE_NO=get_workspace_no(),
        ROOT_NO=get_root_no(element_no),
        CASE_NO=get_case_no(element_no),
        PARENT_NO=get_parent_no(element_no),
        ELEMENT_NO=element_no,
        SOURCE_NO=source_no,
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.COPY.value
    )


@element_transferred_signal.connect
def record_transfer_element(sender, collection_no, source_workspace_no, target_workspace_no):
    """集合转移空间"""
    TElementChangelog.insert(
        ROOT_NO=collection_no,
        ELEMENT_NO=collection_no,
        SOURCE_NO=source_workspace_no,
        TARGET_NO=target_workspace_no,
        OPERATION_BY=localvars.get_user_no(),
        OPERATION_TIME=datetime_now_by_utc8(),
        OPERATION_TYPE=ElementOperationType.TRANSFER.value
    )
