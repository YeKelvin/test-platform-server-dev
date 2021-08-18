#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_service.py
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from typing import Iterable

from app.common.decorators.service import http_service
from app.common.decorators.transaction import transactional
from app.common.exceptions import ServiceError
from app.common.id_generator import new_id
from app.common.validator import check_is_blank
from app.common.validator import check_is_not_blank
from app.extension import db
from app.public.dao import workspace_dao as WorkspaceDao
from app.public.model import TWorkspace
from app.script.dao import element_child_rel_dao as ElementChildRelDao
from app.script.dao import element_property_dao as ElementPropertyDao
from app.script.dao import test_element_dao as TestElementDao
from app.script.enum import ElementStatus
from app.script.model import TElementChildRel
from app.script.model import TElementProperty
from app.script.model import TTestElement
from app.script.model import TWorkspaceCollectionRel
from app.utils.json_util import from_json
from app.utils.json_util import to_json
from app.utils.log_util import get_logger
from app.utils.sqlalchemy_util import QueryCondition


log = get_logger(__name__)


@http_service
def query_element_list(req):
    # 查询条件
    conds = QueryCondition(TTestElement)
    conds.add_fuzzy_match(TTestElement.ELEMENT_NO, req.elementNo)
    conds.add_fuzzy_match(TTestElement.ELEMENT_NAME, req.elementName)
    conds.add_fuzzy_match(TTestElement.ELEMENT_REMARK, req.elementRemark)
    conds.add_fuzzy_match(TTestElement.ELEMENT_TYPE, req.elementType)
    conds.add_fuzzy_match(TTestElement.ENABLED, req.enabled)

    if req.workspaceNo:
        conds.add_table(TWorkspaceCollectionRel)
        conds.add_exact_match(TWorkspaceCollectionRel.DECOLLECTION_NOL_STATE, TTestElement.ELEMENT_NO)
        conds.add_fuzzy_match(TWorkspaceCollectionRel.WORKSPACE_NO, req.workspaceNo)

    if req.workspaceName:
        conds.add_table(TWorkspace)
        conds.add_exact_match(TWorkspaceCollectionRel.DEL_STATE, 0)
        conds.add_exact_match(TWorkspaceCollectionRel.COLLECTION_NO, TTestElement.ELEMENT_NO)
        conds.add_exact_match(TWorkspaceCollectionRel.WORKSPACE_NO, TWorkspace.WORKSPACE_NO)
        conds.add_fuzzy_match(TWorkspace.WORKSPACE_NAME, req.workspaceName)

    # TTestElement，TWorkspace，TWorkspaceCollectionRel连表查询
    pagination = db.session.query(
        TTestElement.ELEMENT_NO, TTestElement.ELEMENT_NAME, TTestElement.ELEMENT_REMARK, TTestElement.ELEMENT_TYPE,
        TTestElement.ENABLED
    ).filter(*conds).order_by(TTestElement.CREATED_TIME.desc()).paginate(req.page, req.pageSize)

    data = []
    for item in pagination.items:
        data.append({
            'elementNo': item.ELEMENT_NO,
            'elementName': item.ELEMENT_NAME,
            'elementType': item.ELEMENT_TYPE,
            'enabled': item.ENABLED
        })
    return {'data': data, 'total': pagination.total}


@http_service
def query_element_all(req):
    # 查询条件
    conds = QueryCondition(TTestElement, TWorkspaceCollectionRel)
    conds.add_exact_match(TWorkspaceCollectionRel.COLLECTION_NO, TTestElement.ELEMENT_NO)
    conds.add_fuzzy_match(TWorkspaceCollectionRel.WORKSPACE_NO, req.workspaceNo)
    conds.add_fuzzy_match(TTestElement.ELEMENT_TYPE, req.elementType)
    conds.add_fuzzy_match(TTestElement.ENABLED, req.enabled)

    # TTestElement，TWorkspaceCollectionRel连表查询
    items = db.session.query(
        TTestElement.ELEMENT_NO,
        TTestElement.ELEMENT_NAME,
        TTestElement.ELEMENT_REMARK,
        TTestElement.ELEMENT_TYPE,
        TTestElement.ELEMENT_CLASS,
        TTestElement.ENABLED
    ).filter(*conds).order_by(TTestElement.CREATED_TIME.desc()).all()

    result = []
    for item in items:
        result.append({
            'elementNo': item.ELEMENT_NO,
            'elementName': item.ELEMENT_NAME,
            'elementType': item.ELEMENT_TYPE,
            'elementClass': item.ELEMENT_CLASS,
            'enabled': item.ENABLED
        })
    return result


@http_service
def query_element_info(req):
    # 查询元素
    element = TestElementDao.select_by_elementno(req.elementNo)
    check_is_not_blank(element, '元素不存在')

    # 查询元素属性
    property = query_element_property(req.elementNo)
    # 查询元素是否有子代
    has_children = ElementChildRelDao.count_by_parentno(req.elementNo) > 0

    return {
        'elementNo': element.ELEMENT_NO,
        'elementName': element.ELEMENT_NAME,
        'elementRemark': element.ELEMENT_REMARK,
        'elementType': element.ELEMENT_TYPE,
        'elementClass': element.ELEMENT_CLASS,
        'enabled': element.ENABLED,
        'property': property,
        'hasChildren': has_children
    }


def query_element_property(element_no):
    """查询元素属性"""
    property = {}
    props = ElementPropertyDao.select_all_by_elementno(element_no)
    for prop in props:
        if prop.PROPERTY_TYPE == 'STR':
            property[prop.PROPERTY_NAME] = prop.PROPERTY_VALUE
            continue
        if prop.PROPERTY_TYPE == 'DICT':
            property[prop.PROPERTY_NAME] = from_json(prop.PROPERTY_VALUE)
            continue
        if prop.PROPERTY_TYPE == 'LIST':
            property[prop.PROPERTY_NAME] = from_json(prop.PROPERTY_VALUE)
            continue
    return property


@http_service
def query_element_children(req):
    return get_element_children(req.elementNo, req.depth)


def get_element_children(parent_no, depth):
    """递归查询元素子代"""
    result = []

    # 查询元素所有子代关系
    el_child_rel_list = ElementChildRelDao.select_all_by_parentno(parent_no)
    if not el_child_rel_list:
        return result

    # 根据child-order排序
    el_child_rel_list.sort(key=lambda k: k.CHILD_ORDER)
    for el_child_rel in el_child_rel_list:
        # 查询子代元素信息
        element = TestElementDao.select_by_elementno(el_child_rel.CHILD_NO)
        if element:
            # 递归查询子代
            children = depth and get_element_children(el_child_rel.CHILD_NO, depth) or []
            result.append({
                'elementNo': element.ELEMENT_NO,
                'elementName': element.ELEMENT_NAME,
                'elementType': element.ELEMENT_TYPE,
                'elementClass': element.ELEMENT_CLASS,
                'enabled': element.ENABLED,
                'order': el_child_rel.CHILD_ORDER,
                'children': children
            })

    return result


@http_service
@transactional
def create_element(req):
    # TODO: Type==TestCollection时，workspaceNo不允许为空

    # 创建元素
    element_no = add_element(
        element_name=req.elementName,
        element_remark=req.elementRemark,
        element_type=req.elementType,
        element_class=req.elementClass,
        property=req.property,
        children=req.children
    )

    # 如果元素类型为TestCollection时，需要绑定WorkspaceNo
    if req.workspaceNo:
        workspace = WorkspaceDao.select_by_workspaceno(req.workspaceNo)
        check_is_not_blank(workspace, '测试项目不存在')

        TWorkspaceCollectionRel.insert(WORKSPACE_NO=req.workspaceNo, COLLECTION_NO=element_no)

    return {'elementNo': element_no}


def add_element(
    element_name, element_remark, element_type, element_class, property: dict = None, children: Iterable[dict] = None
):
    """创建元素并递归创建元素属性和元素子代"""
    # 创建元素
    element_no = new_id()
    TTestElement.insert(
        ELEMENT_NO=element_no,
        ELEMENT_NAME=element_name,
        ELEMENT_REMARK=element_remark,
        ELEMENT_TYPE=element_type,
        ELEMENT_CLASS=element_class,
        ENABLED=ElementStatus.ENABLE.value
    )

    if property:
        # 创建元素属性
        add_element_property(element_no, property)

    if children:
        # 创建元素子代
        add_element_children(element_no, children)

    return element_no


@http_service
@transactional
def modify_element(req):
    update_element(
        element_no=req.elementNo,
        element_name=req.elementName,
        element_remark=req.elementRemark,
        property=req.property,
        children=req.children
    )


def update_element(element_no, element_name, element_remark, property: dict = None, children: Iterable[dict] = None):
    """递归修改元素"""
    # 查询元素
    element = TestElementDao.select_by_elementno(element_no)
    check_is_not_blank(element, '元素不存在')

    # 更新元素信息
    element.update(ELEMENT_NAME=element_name, ELEMENT_REMARK=element_remark)

    if property:
        # 更新元素属性信息
        update_element_property(element_no, property)

    if children:
        # 更新元素子代
        update_element_children(children)


@http_service
@transactional
def delete_element(req):
    return remove_element(req.elementNo)


def remove_element(element_no):
    """递归删除元素"""
    # 查询元素
    element = TestElementDao.select_by_elementno(element_no)
    check_is_not_blank(element, '元素不存在')

    # 递归删除元素子代和关联关系
    remove_element_children(element_no)
    # 如存在父辈关联关系，则删除关联并重新排序父辈子代
    child_rel = ElementChildRelDao.select_by_childno(element_no)
    if child_rel:
        # 重新排序父辈子代
        TElementChildRel.query.filter(
            TElementChildRel.PARENT_NO == child_rel.PARENT_NO, TElementChildRel.CHILD_ORDER > child_rel.CHILD_ORDER
        ).update({TElementChildRel.CHILD_ORDER: TElementChildRel.CHILD_ORDER - 1})
        # 删除父辈关联
        child_rel.delete()

    # 删除元素属性
    remove_element_property(element_no)
    # 删除元素
    element.delete()


def remove_element_children(parent_no):
    """递归删除子代元素"""
    # 查询所有子代关联关系列表
    child_rel_list = ElementChildRelDao.select_all_by_parentno(parent_no)
    for child_rel in child_rel_list:
        # 查询子代元素信息
        child = TestElementDao.select_by_elementno(child_rel.child_no)
        # 递归删除子代元素的子代和关联关系
        remove_element_children(child_rel.child_no)
        # 删除子代元素属性
        remove_element_property(child_rel.child_no)
        # 删除父子关联关系
        child_rel.delete()
        # 删除子代元素
        child.delete()


def remove_element_property(element_no):
    """遍历删除元素属性"""
    # 查询元素所有属性
    props = ElementPropertyDao.select_all_by_elementno(element_no)
    for prop in props:
        prop.delete()


@http_service
def enable_element(req):
    # 查询元素
    element = TestElementDao.select_by_elementno(req.elementNo)
    check_is_not_blank(element, '元素不存在')

    # 更新元素状态为启用
    element.update(ENABLED=ElementStatus.ENABLE.value)


@http_service
def disable_element(req):
    # 查询元素
    element = TestElementDao.select_by_elementno(req.elementNo)
    check_is_not_blank(element, '元素不存在')

    # 更新元素状态为禁用
    element.update(ENABLED=ElementStatus.DISABLE.value)


@http_service
def create_element_property(req):
    # 查询元素属性
    el_prop = ElementPropertyDao.select_by_elementno_and_propname(req.elementNo, req.propertyName)
    check_is_blank(el_prop, '元素属性已存在')

    # 创建元素属性
    TElementProperty.insert(ELEMENT_NO=req.elementNo, PROPERTY_NAME=req.propertyName, PROPERTY_VALUE=req.propertyValue)


def add_element_property(element_no, property: dict):
    """遍历添加元素属性"""
    for name, value in property.items():
        value_type = 'STR'

        if isinstance(value, dict):
            value_type = 'DICT'
            value = to_json(value)
        if isinstance(value, list):
            value_type = 'LIST'
            value = to_json(value)

        TElementProperty.insert(
            ELEMENT_NO=element_no, PROPERTY_NAME=name, PROPERTY_VALUE=value, PROPERTY_TYPE=value_type
        )


@http_service
def modify_element_property(req):
    # 查询元素属性
    el_prop = ElementPropertyDao.select_by_elementno_and_propname(req.elementNo, req.propertyName)
    check_is_not_blank(el_prop, '元素属性不存在')

    # 更新元素属性值
    el_prop.update(property_value=req.propertyValue)


def update_element_property(element_no, property: dict):
    """遍历修改元素属性"""
    for name, value in property.items():
        # 查询元素属性
        prop = ElementPropertyDao.select_by_elementno_and_name(element_no, name)
        # 更新元素属性值
        if isinstance(value, str):
            prop.update(PROPERTY_VALUE=value, PROPERTY_TYPE='STR')
            continue
        if isinstance(value, dict):
            prop.update(PROPERTY_VALUE=to_json(value), PROPERTY_TYPE='DICT')
            continue
        if isinstance(value, list):
            prop.update(PROPERTY_VALUE=to_json(value), PROPERTY_TYPE='LIST')
            continue


@http_service
@transactional
def create_element_children(req):
    add_element_children(parent_no=req.parentNo, children=req.children)


def add_element_children(parent_no, children: Iterable[dict]):
    """添加元素子代"""
    for child in children:
        child_no = add_element(
            element_name=child.get('elementName'),
            element_remark=child.get('elementRemark'),
            element_type=child.get('elementType'),
            element_class=child.get('elementClass'),
            property=child.get('property', None),
            children=child.get('children', None)
        )
        TElementChildRel.insert(
            PARENT_NO=parent_no,
            CHILD_NO=child_no,
            CHILD_ORDER=ElementChildRelDao.next_order_by_parentno(parent_no)
        )


@http_service
@transactional
def modify_element_children(req):
    update_element_children(children=req.children)


def update_element_children(children: Iterable[dict]):
    """遍历修改元素子代"""
    for child in children:
        if 'elementNo' not in child:
            raise ServiceError('子代元素编号不能为空')

        update_element(
            element_no=child.get('elementNo'),
            element_name=child.get('elementName'),
            element_remark=child.get('elementRemark'),
            element_type=child.get('elementType'),
            property=child.get('property', None),
            children=child.get('children', None)
        )


@http_service
def move_up_child_order(req):
    # 查询元素子代关联关系
    child_rel = ElementChildRelDao.select_by_parentno_and_childno(req.parentNo, req.childNo)
    check_is_not_blank(child_rel, '子元素不存在')

    # 统计元素子代个数
    children_length = ElementChildRelDao.count_by_parentno(req.parentNo)
    child_order = child_rel.CHILD_ORDER

    # 如果元素只有一个子代或该子代元素排第一位则无需上移
    if children_length == 1 or child_order == 1:
        return

    upper_child_rel = ElementChildRelDao.select_by_parentno_and_childorder(req.parentNo, child_order - 1)
    upper_child_rel.update(CHILD_ORDER=upper_child_rel.CHILD_ORDER + 1)
    child_rel.update(CHILD_ORDER=child_rel.CHILD_ORDER - 1)


@http_service
def move_down_child_order(req):
    # 查询元素子代关联关系
    child_rel = ElementChildRelDao.select_by_parentno_and_childno(req.parentNo, req.childNo)
    check_is_not_blank(child_rel, '子元素不存在')

    # 统计元素子代个数
    children_length = ElementChildRelDao.count_by_parentno(req.parentNo)
    child_order = child_rel.CHILD_ORDER

    # 如果元素只有一个子代或该子代元素排最后一位则无需下移
    if children_length == 1 or children_length == child_order:
        return

    lower_child_rel = ElementChildRelDao.select_by_parentno_and_childorder(req.parentNo, child_order + 1)
    lower_child_rel.update(CHILD_ORDER=lower_child_rel.CHILD_ORDER - 1)
    child_rel.update(CHILD_ORDER=child_rel.CHILD_ORDER + 1)


@http_service
def duplicate_element(req):
    # 查询元素
    element = TestElementDao.select_by_elementno(req.elementNo)
    check_is_not_blank(element, '元素不存在')
    # todo 复制元素
