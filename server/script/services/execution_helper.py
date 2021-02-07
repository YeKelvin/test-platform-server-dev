#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : execution_helper.py
# @Time    : 2021/1/22 23:41
# @Author  : Kelvin.Ye
from server.common.utils.log_util import get_logger
from server.common.validator import assert_not_blank
from server.script.models import TElementChildRel, TTestElement, TElementProperty

log = get_logger(__name__)


def element_to_dict(element_no):
    # 查询元素
    element = TTestElement.query_by(ELEMENT_NO=element_no).first()
    assert_not_blank(element, '测试元素不存在')

    # 递归查询元素子代
    element_child_rels = TElementChildRel.query_by(PARENT_NO=element_no).all()
    children = []
    if element_child_rels:
        for element_child_rel in element_child_rels:
            children.append(element_to_dict(element_child_rel.CHILD_NO))

    # 包装为字典返回
    el_dict = {
        'name': element.ELEMENT_NAME,
        'comments': element.ELEMENT_COMMENTS,
        'class': element.ELEMENT_CLASS,
        'enabled': element.ENABLED,
        'property': property_to_dict(element_no),
        'child': children
    }
    return el_dict


def property_to_dict(element_no):
    # 查询元素属性，只查询enabled的属性
    props = TElementProperty.query_by(ELEMENT_NO=element_no, ENABLED=True).all()

    # 包装为字典返回
    prop_dict = {}
    for prop in props:
        prop_dict[prop.PROPERTY_NAME] = prop.PROPERTY_VALUE

    return prop_dict
