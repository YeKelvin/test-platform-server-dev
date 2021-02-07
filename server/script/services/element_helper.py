#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_helper.py
# @Time    : 2021/1/22 23:41
# @Author  : Kelvin.Ye
from typing import Iterable

from server.common.exceptions import ServiceError
from server.common.id_generator import new_id
from server.common.utils.log_util import get_logger
from server.common.validator import assert_not_blank
from server.extension import db
from server.script.enums import ElementStatus
from server.script.models import TElementChildRel, TElementProperty, TTestElement

log = get_logger(__name__)


def create_element(element_name, element_comments, element_type, element_class,
                   propertys: dict = None, children: Iterable[dict] = None):
    """递归创建元素
    """
    element_no = new_id()
    TTestElement.create(
        commit=False,
        ELEMENT_NO=element_no,
        ELEMENT_NAME=element_name,
        ELEMENT_COMMENTS=element_comments,
        ELEMENT_TYPE=element_type,
        ELEMENT_CLASS=element_class,
        ENABLED=ElementStatus.ENABLE.value
    )
    db.session.flush()

    if propertys:
        add_element_property(element_no, propertys)
    if children:
        add_element_child(element_no, children)

    return element_no


def add_element_property(element_no, propertys: dict):
    for prop_name, prop_value in propertys.items():
        TElementProperty.create(
            commit=False,
            ELEMENT_NO=element_no,
            PROPERTY_NAME=prop_name,
            PROPERTY_VALUE=prop_value
        )

    db.session.flush()


def add_element_child(parent_no, children: Iterable[dict]):
    """遍历添加元素子代
    """
    for child in children:
        child_no = create_element(
            element_name=child.get('elementName'),
            element_comments=child.get('elementComments'),
            element_type=child.get('elementType'),
            element_class=child.get('elementClass'),
            propertys=child.get('propertys'),
            children=child.get('children')
        )
        TElementChildRel.create(
            commit=False,
            PARENT_NO=parent_no,
            CHILD_NO=child_no,
            CHILD_ORDER=next_child_order(parent_no)
        )

    db.session.flush()


def modify_element(element_no, element_name, element_comments, propertys, children):
    """递归修改元素
    """
    element = TTestElement.query_by(ELEMENT_NO=element_no).first()
    assert_not_blank(element, '测试元素不存在')

    if element_name is not None:
        element.ELEMENT_NAME = element_name
    if element_comments is not None:
        element.ELEMENT_COMMENTS = element_comments

    element.save(commit=False)
    db.session.flush()

    if propertys is not None:
        modify_element_property(element_no, propertys)
    if children is not None:
        modify_element_child(children)


def modify_element_property(element_no, propertys: dict):
    """遍历修改元素属性
    """
    for prop_name, prop_value in propertys.items():
        el_prop = TElementProperty.query_by(ELEMENT_NO=element_no, PROPERTY_NAME=prop_name).first()
        el_prop.PROPERTY_VALUE = prop_value
        el_prop.save(commit=False)

    db.session.flush()


def modify_element_child(children: Iterable[dict]):
    """遍历修改元素子代
    """
    for child in children:
        if 'elementNo' not in child:
            raise ServiceError('子代元素编号不能为空')

        modify_element(
            element_no=child.get('elementNo'),
            element_name=child.get('elementName'),
            element_comments=child.get('elementComments'),
            element_type=child.get('elementType'),
            propertys=child.get('propertys'),
            children=child.get('children')
        )


def delete_element(element_no):
    """递归删除元素
    """
    element = TTestElement.query_by(ELEMENT_NO=element_no).first()
    assert_not_blank(element, '测试元素不存在')

    result = [{
        'elementNo': element.ELEMENT_NO,
        'elementName': element.ELEMENT_NAME
    }]

    # 递归删除元素子代和关联关系
    result.extend(delete_child(element_no))
    # 如存在父辈关联关系，则删除关联并重新排序父辈子代
    child_rel = TElementChildRel.query_by(CHILD_NO=element_no).first()
    if child_rel:
        # 重新排序父辈子代
        TElementChildRel.query.filter(
            TElementChildRel.PARENT_NO == child_rel.PARENT_NO,
            TElementChildRel.CHILD_ORDER > child_rel.CHILD_ORDER
        ).update({TElementChildRel.CHILD_ORDER: TElementChildRel.CHILD_ORDER - 1})
        # 删除父辈关联
        child_rel.update(commit=False, DEL_STATE=1)

    # 删除元素属性
    delete_property(element_no)
    # 删除元素
    element.update(commit=False, DEL_STATE=1)

    db.session.flush()
    return result


def delete_child(element_no):
    child_rels = TElementChildRel.query_by(PARENT_NO=element_no).all()
    result = []
    for child_rel in child_rels:
        # 查询子代元素信息
        child = TTestElement.query_by(ELEMENT_NO=child_rel.child_no).first()
        if child:
            result.append({'elementNo': child.ELEMENT_NO, 'elementName': child.ELEMENT_NAME})

        result.extend(delete_child(child_rel.child_no))  # 递归删除子代元素的子代和关联关系
        # 删除父子关联关系
        child_rel.update(commit=False, DEL_STATE=1)
        # 删除子代元素属性
        delete_property(child_rel.child_no)
        # 删除子代元素
        child.update(commit=False, DEL_STATE=1)

    db.session.flush()
    return result


def delete_property(element_no):
    props = TElementProperty.query_by(ELEMENT_NO=element_no).all()
    for prop in props:
        prop.update(commit=False, DEL_STATE=1)

    db.session.flush()


def next_child_order(parent_no):
    return TElementChildRel.query_by(PARENT_NO=parent_no).count() + 1
