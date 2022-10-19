#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : element_controller.py
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from app.script.controller import blueprint
from app.script.enum import PasteType
from app.script.service import element_service as service
from app.tools.decorators.require import require_login
from app.tools.decorators.require import require_permission
from app.tools.logger import get_logger
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.parser import ListParser


log = get_logger(__name__)


@blueprint.get('/element/list')
@require_login
@require_permission
def query_element_list():
    """分页查询元素列表"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('workspaceName'),
        Argument('elementNo'),
        Argument('elementName'),
        Argument('elementRemark'),
        Argument('elementType'),
        Argument('elementClass'),
        Argument('enabled'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空'),
    ).parse()
    return service.query_element_list(req)


@blueprint.get('/element/all')
@require_login
@require_permission
def query_element_all():
    """查询所有元素"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('elementType'),
        Argument('elementClass'),
        Argument('enabled')
    ).parse()
    return service.query_element_all(req)


@blueprint.get('/element/all/in/private')
@require_login
@require_permission
def query_element_all_in_private():
    """查询用户所有空间下的所有元素（用于私人空间）"""
    req = JsonParser(
        Argument('elementType'),
        Argument('elementClass'),
        Argument('enabled')
    ).parse()
    return service.query_element_all_in_private(req)


@blueprint.get('/element/all/with/children')
@require_login
@require_permission
def query_element_all_with_children():
    """查询所有元素及其子代"""
    req = JsonParser(
        Argument('workspaceNo'),
        Argument('elementType'),
        Argument('elementClass'),
        Argument('childType'),
        Argument('childClass'),
        Argument('enabled')
    ).parse()
    return service.query_element_all_with_children(req)


@blueprint.get('/element/info')
@require_login
@require_permission
def query_element_info():
    """查询元素信息"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.query_element_info(req)


@blueprint.get('/element/children')
@require_login
@require_permission
def query_element_children():
    """查询元素子代"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('depth', type=bool, required=True, default=True),
    ).parse()
    return service.query_element_children(req)


@blueprint.get('/elements/children')
@require_login
@require_permission
def query_elements_children():
    """根据元素编号列表查询子代元素"""
    req = JsonParser(
        Argument('elementNos', type=list, required=True, nullable=False, help='元素编号列表不能为空'),
        Argument('depth', type=bool, required=True, default=True),
    ).parse()
    return service.query_elements_children(req)


@blueprint.post('/collection')
@require_login
@require_permission
def create_collection():
    """新增集合元素"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('elementName', required=True, nullable=False, help='元素名称不能为空'),
        Argument('elementRemark'),
        Argument('elementType', required=True, nullable=False, help='元素类型不能为空'),
        Argument('elementClass', required=True, nullable=False, help='元素类不能为空'),
        Argument('property', required=True, nullable=False, help='元素属性不能为空'),
        Argument('options', type=dict),
        Argument('builtins', type=list)
    ).parse()
    return service.create_collection(req)


@blueprint.post('/element/child')
@require_login
@require_permission
def create_element_child():
    """
    新增子代元素
    request:
    {
        "rootNo": "",
        "parentNo": "",
        "child": {
            "elementName": "",
            "elementRemark": "",
            "elementType": "",
            "elementClass": "",
            "property": { ... },
            "options": { ... },
            "builtins": [ ... ]
        }
    }
    """
    req = JsonParser(
        Argument('rootNo', required=True, nullable=False, help='根元素编号不能为空'),
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('child', type=dict, required=True, nullable=False, help='子元素不能为空')
    ).parse()
    return service.create_element_child(req)


@blueprint.post('/element/children')
@require_login
@require_permission
def create_element_children():
    """
    根据列表新增子代元素
    request:
    {
        "rootNo": "",
        "parentNo": "",
        "children": [
            {
                "elementName": "",
                "elementRemark": "",
                "elementType": "",
                "elementClass": "",
                "property": { ... },
                "options": { ... },
                "builtins": [ ... ]
            }
            ...
        ]
    }
    """
    req = JsonParser(
        Argument('rootNo', required=True, nullable=False, help='根元素编号不能为空'),
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('children', type=list, required=True, nullable=False, help='子元素列表不能为空')
    ).parse()
    return service.create_element_children(req)


@blueprint.put('/element')
@require_login
@require_permission
def modify_element():
    """修改元素"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('elementName'),
        Argument('elementRemark'),
        Argument('enabled'),
        Argument('property'),
        Argument('options', type=dict),
        Argument('builtins', type=list),
    ).parse()
    return service.modify_element(req)


@blueprint.delete('/element')
@require_login
@require_permission
def remove_element():
    """删除元素"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.remove_element(req)


@blueprint.patch('/element/enable')
@require_login
@require_permission
def enable_element():
    """启用元素"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.enable_element(req)


@blueprint.patch('/element/disable')
@require_login
@require_permission
def disable_element():
    """禁用元素"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.disable_element(req)


@blueprint.post('/element/move')
@require_login
@require_permission
def move_element():
    """移动元素"""
    req = JsonParser(
        Argument('sourceNo', required=True, nullable=False, help='source元素编号不能为空'),
        Argument('targetRootNo', required=True, nullable=False, help='target根元素编号不能为空'),
        Argument('targetParentNo', required=True, nullable=False, help='target父元素编号不能为空'),
        Argument('targetSortNo', type=int, required=True, nullable=False, help='target元素序号不能为空')
    ).parse()
    return service.move_element(req)


@blueprint.post('/element/duplicate')
@require_login
@require_permission
def duplicate_element():
    """复制元素及其子代"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.duplicate_element(req)


@blueprint.post('/element/paste')
@require_login
@require_permission
def paste_element():
    """剪贴元素"""
    req = JsonParser(
        Argument('sourceNo', required=True, nullable=False, help='source元素编号不能为空'),
        Argument('targetNo', required=True, nullable=False, help='target元素编号不能为空'),
        Argument('pasteType', required=True, nullable=False, enum=PasteType, help='剪贴类型不能为空')
    ).parse()
    return service.paste_element(req)


@blueprint.get('/element/httpheader/template/refs')
@require_login
@require_permission
def query_element_httpheader_template_refs():
    """查询元素关联的HTTP请求头模板列表"""
    req = JsonParser(Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')).parse()
    return service.query_element_httpheader_template_refs(req)


@blueprint.post('/element/httpheader/template/refs')
@require_login
@require_permission
def create_element_httpheader_template_refs():
    """新增元素和HTTP请求头模板列表的关联"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('templateNos', type=list, required=True, nullable=False, help='模板编号列表不能为空')
    ).parse()
    return service.create_element_httpheader_template_refs(req)


@blueprint.put('/element/httpheader/template/refs')
@require_login
@require_permission
def modify_element_httpheader_template_refs():
    """修改元素关联的HTTP请求头模板关联列表"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('templateNos', type=list, required=True, nullable=False, help='模板编号列表不能为空')
    ).parse()
    return service.modify_element_httpheader_template_refs(req)


@blueprint.get('/element/builtins')
@require_login
@require_permission
def query_element_builtins():
    """查询内置元素"""
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.query_element_builtins(req)


@blueprint.post('/element/builtins')
@require_login
@require_permission
def create_element_builtins():
    """新增内置元素"""
    req = JsonParser(
        Argument('rootNo', required=True, nullable=False, help='根元素编号不能为空'),
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('children', type=list, required=True, nullable=False, help='子元素列表不能为空')
    ).parse()
    return service.create_element_builtins(req)


@blueprint.put('/element/builtins')
@require_login
@require_permission
def modify_element_builtins():
    """修改内置元素"""
    req = ListParser().parse()
    return service.modify_element_builtins(req)


@blueprint.post('/element/collection/copy/to/workspace')
@require_login
@require_permission
def copy_collection_to_workspace():
    """复制集合至指定空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.copy_collection_to_workspace(req)


@blueprint.post('/element/collection/move/to/workspace')
@require_login
@require_permission
def move_collection_to_workspace():
    """移动集合至指定空间"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空')
    ).parse()
    return service.move_collection_to_workspace(req)


@blueprint.post('/element/http/sampler')
@require_login
@require_permission
def create_http_sampler():
    """
    新增 HTTP Sampler 元素
    request:
    {
        "rootNo": "",
        "parentNo": "",
        "child": {
            "elementName": "",
            "elementRemark": "",
            "property": { ... },
            "builtins": [
                    "elementNo": "",
                    "elementName": "",
                    "elementType": "",
                    "elementClass": "",
                    "property": { ... },
                    "sortNumber": ""
                }
                ...
            ],
            "headerTemplateNos": [ ... ]
        }
    }
    """
    req = JsonParser(
        Argument('rootNo', required=True, nullable=False, help='根元素编号不能为空'),
        Argument('parentNo', required=True, nullable=False, help='父元素编号不能为空'),
        Argument('child', type=dict, required=True, nullable=False, help='元素信息不能为空')
    ).parse()
    return service.create_http_sampler(req)


@blueprint.put('/element/http/sampler')
@require_login
@require_permission
def modify_http_sampler():
    """
    修改 HTTP Sampler 元素
    request:
    {
        "elementNo": "",
        "elementName": "",
        "elementRemark": "",
        "property": { ... },
        "builtins": [
            {
                "elementNo": "",
                "elementName": "",
                "elementType": "",
                "elementClass": "",
                "property": { ... },
                "sortNumber": ""
            }
            ...
         ],
        "headerTemplateNos": [ ... ]
    }
    """
    req = JsonParser(
        Argument('elementNo', required=True, nullable=False, help='元素编号不能为空'),
        Argument('elementName', required=True, nullable=False, help='元素名称不能为空'),
        Argument('elementRemark'),
        Argument('property', required=True, nullable=False, help='元素属性不能为空'),
        Argument('builtins', type=list),
        Argument('headerTemplateNos', type=list)
    ).parse()
    return service.modify_http_sampler(req)


@blueprint.get('/element/workspace/components')
@require_login
@require_permission
def query_workspace_components():
    """查询空间所有组件"""
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空')
    ).parse()
    return service.query_workspace_components(req)


@blueprint.post('/element/workspace/components')
@require_login
@require_permission
def set_workspace_components():
    """
    设置空间组件
    request:
    {
        "workspaceNo": "",
        "components": [

            {
                "elementNo": "",
                "elementName": "",
                "elementType": "",
                "elementClass": "",
                "property": { ... },
                "matchRules": [ ... ],
                "sortNumber": ""
            }
            ...
         ]
    }
    """
    req = JsonParser(
        Argument('workspaceNo', required=True, nullable=False, help='空间编号不能为空'),
        Argument('components', type=list)
    ).parse()
    return service.set_workspace_components(req)
