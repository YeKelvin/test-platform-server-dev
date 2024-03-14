#!/usr/bin/ python3
# @File    : element_service.py
# @Time    : 2020/3/13 16:58
# @Author  : Kelvin.Ye
from flask import request
from loguru import logger

from app.database import db_query
from app.modules.public.dao import workspace_dao
from app.modules.public.model import TWorkspace
from app.modules.script.dao import element_children_dao
from app.modules.script.dao import element_component_dao
from app.modules.script.dao import element_property_dao
from app.modules.script.dao import test_element_dao
from app.modules.script.enum import ElementClass
from app.modules.script.enum import ElementStatus
from app.modules.script.enum import ElementType
from app.modules.script.enum import PasteType
from app.modules.script.enum import is_collection
from app.modules.script.enum import is_controller
from app.modules.script.enum import is_sampler
from app.modules.script.enum import is_snippet
from app.modules.script.enum import is_timer
from app.modules.script.enum import is_worker
from app.modules.script.manager.element_manager import get_root_no
from app.modules.script.manager.element_manager import get_workspace_no
from app.modules.script.model import TElementChildren
from app.modules.script.model import TElementComponent
from app.modules.script.model import TElementProperty
from app.modules.script.model import TTestElement
from app.modules.script.types import TypedElement
from app.signals import element_copied_signal
from app.signals import element_created_signal
from app.signals import element_modified_signal
from app.signals import element_moved_signal
from app.signals import element_removed_signal
from app.signals import element_sorted_signal
from app.signals import element_transferred_signal
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.tools.validator import check_workspace_permission
from app.utils.json_util import from_json
from app.utils.json_util import to_json
from app.utils.sqlalchemy_util import QueryCondition
from app.utils.time_util import datetime_now_by_utc8


@http_service
def query_element_list(req):
    # 查询条件
    conds = QueryCondition(TTestElement)
    conds.like(TTestElement.ELEMENT_NO, req.elementNo)
    conds.like(TTestElement.ELEMENT_NAME, req.elementName)
    conds.like(TTestElement.ELEMENT_DESC, req.elementDesc)
    conds.like(TTestElement.ELEMENT_TYPE, req.elementType)
    conds.like(TTestElement.ELEMENT_CLASS, req.elementClass)
    conds.equal(TTestElement.ENABLED, req.enabled)

    if req.workspaceNo:
        conds.like(TTestElement.WORKSPACE_NO, req.workspaceNo)

    if req.workspaceName:
        conds.add_table(TWorkspace)
        conds.like(TWorkspace.WORKSPACE_NAME, req.workspaceName)
        conds.equal(TTestElement.WORKSPACE_NO, TWorkspace.WORKSPACE_NO)

    # TTestElement，TWorkspace连表查询
    pagination = (
        db_query(
            TTestElement.ELEMENT_NO,
            TTestElement.ELEMENT_NAME,
            TTestElement.ELEMENT_DESC,
            TTestElement.ELEMENT_TYPE,
            TTestElement.SKIPED,
            TTestElement.ENABLED
        )
        .filter(*conds)
        .order_by(TTestElement.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'skiped': item.SKIPED,
            'enabled': item.ENABLED,
            'elementNo': item.ELEMENT_NO,
            'elementName': item.ELEMENT_NAME,
            'elementType': item.ELEMENT_TYPE
        }
        for item in pagination.items
    ]

    return {'list': data, 'total': pagination.total}


@http_service
def query_element_all(req):
    # 查询条件
    conds = QueryCondition(TTestElement)
    conds.equal(TTestElement.ENABLED, req.enabled)
    conds.equal(TTestElement.WORKSPACE_NO, req.workspaceNo)
    conds.equal(TTestElement.ELEMENT_TYPE, req.elementType)
    conds.equal(TTestElement.ELEMENT_CLASS, req.elementClass)

    items = db_query(
        TTestElement.SKIPED,
        TTestElement.ENABLED,
        TTestElement.ELEMENT_NO,
        TTestElement.ELEMENT_NAME,
        TTestElement.ELEMENT_DESC,
        TTestElement.ELEMENT_TYPE,
        TTestElement.ELEMENT_CLASS
    ).filter(*conds).order_by(TTestElement.CREATED_TIME.desc()).all()

    return [
        {
            'skiped': item.SKIPED,
            'enabled': item.ENABLED,
            'elementNo': item.ELEMENT_NO,
            'elementName': item.ELEMENT_NAME,
            'elementType': item.ELEMENT_TYPE,
            'elementClass': item.ELEMENT_CLASS
        }
        for item in items
    ]


@http_service
def query_element_all_with_children(req):
    # 查询条件
    conds = QueryCondition(TTestElement)
    conds.equal(TTestElement.ENABLED, req.enabled)
    conds.equal(TTestElement.WORKSPACE_NO, req.workspaceNo)
    conds.equal(TTestElement.ELEMENT_TYPE, req.elementType)
    conds.equal(TTestElement.ELEMENT_CLASS, req.elementClass)

    items = db_query(
        TTestElement.SKIPED,
        TTestElement.ENABLED,
        TTestElement.ELEMENT_NO,
        TTestElement.ELEMENT_NAME,
        TTestElement.ELEMENT_DESC,
        TTestElement.ELEMENT_TYPE,
        TTestElement.ELEMENT_CLASS
    ).filter(*conds).order_by(TTestElement.CREATED_TIME.desc()).all()

    result = []
    for item in items:
        # 查询子代
        childconds = QueryCondition(TElementChildren, TTestElement)
        childconds.equal(TElementChildren.PARENT_NO, item.ELEMENT_NO)
        childconds.equal(TTestElement.ENABLED, req.enabled)
        childconds.equal(TTestElement.ELEMENT_NO, TElementChildren.ELEMENT_NO)
        childconds.equal(TTestElement.ELEMENT_TYPE, req.childType)
        childconds.equal(TTestElement.ELEMENT_CLASS, req.childClass)
        children = db_query(
            TTestElement.SKIPED,
            TTestElement.ENABLED,
            TTestElement.ELEMENT_NO,
            TTestElement.ELEMENT_NAME,
            TTestElement.ELEMENT_DESC,
            TTestElement.ELEMENT_TYPE,
            TTestElement.ELEMENT_CLASS,
            TElementChildren.ELEMENT_SORT
        ).filter(*childconds).order_by(TElementChildren.ELEMENT_SORT).all()
        # 添加元素信息
        result.append({
            'skiped': item.SKIPED,
            'enabled': item.ENABLED,
            'elementNo': item.ELEMENT_NO,
            'elementName': item.ELEMENT_NAME,
            'elementType': item.ELEMENT_TYPE,
            'elementClass': item.ELEMENT_CLASS,
            'children': [
                {
                    'skiped': child.SKIPED,
                    'enabled': child.ENABLED,
                    'elementNo': child.ELEMENT_NO,
                    'elementName': child.ELEMENT_NAME,
                    'elementType': child.ELEMENT_TYPE,
                    'elementClass': child.ELEMENT_CLASS,
                    'children': []
                }
                for child in children
            ]
        })
    return result


@http_service
def query_element_info(req):
    # 查询元素
    element = test_element_dao.select_by_no(req.elementNo)
    check_exists(element, error='元素不存在')

    return {
        'skiped': element.SKIPED,
        'enabled': element.ENABLED,
        'elementNo': element.ELEMENT_NO,
        'elementName': element.ELEMENT_NAME,
        'elementDesc': element.ELEMENT_DESC,
        'elementType': element.ELEMENT_TYPE,
        'elementClass': element.ELEMENT_CLASS,
        'elementAttrs': element.ELEMENT_ATTRS or {},
        'elementProps': get_element_property(req.elementNo)
    }


def get_element_property(element_no):
    """查询元素属性"""
    properties = {}
    props = element_property_dao.select_all(element_no)
    for prop in props:
        if prop.PROPERTY_TYPE in ['DICT', 'LIST']:
            properties[prop.PROPERTY_NAME] = from_json(prop.PROPERTY_VALUE)
        else:
            properties[prop.PROPERTY_NAME] = prop.PROPERTY_VALUE
    return properties


@http_service
def query_element_tree(req):
    return get_element_children(req.elementNo, req.depth)


@http_service
def query_element_tree_by_roots(req):
    result = []
    for root_no in req.roots:
        root = test_element_dao.select_by_no(root_no)
        if not root:
            logger.warning(f'元素编号:[ {root_no} ] 元素不存在')
            continue
        children = get_element_children(root_no, req.depth)
        result.append({
            'rootNo': root_no,
            'parentNo': None,
            'elementNo': root.ELEMENT_NO,
            'elementName': root.ELEMENT_NAME,
            'elementType': root.ELEMENT_TYPE,
            'elementClass': root.ELEMENT_CLASS,
            'skiped': root.SKIPED,
            'enabled': root.ENABLED,
            'children': children
        })

    return result


def get_element_children(parent_no, depth):
    """递归查询元素子代"""
    result = []
    # 查询元素所有子代
    nodes = element_children_dao.select_all_by_parent(parent_no)
    if not nodes:
        return result

    # 根据序号排序
    nodes.sort(key=lambda k: k.ELEMENT_SORT)
    for node in nodes:
        # 查询子代元素
        if element := test_element_dao.select_by_no(node.ELEMENT_NO):
            # 递归查询子代
            grandchildren = depth and get_element_children(element.ELEMENT_NO, depth) or []
            result.append({
                'rootNo': node.ROOT_NO,
                'parentNo': node.PARENT_NO,
                'elementNo': element.ELEMENT_NO,
                'elementName': element.ELEMENT_NAME,
                'elementType': element.ELEMENT_TYPE,
                'elementClass': element.ELEMENT_CLASS,
                'elementIndex': node.ELEMENT_SORT,
                'skiped': element.SKIPED,
                'enabled': element.ENABLED,
                'children': grandchildren
            })

    return result


@http_service
def create_element(req: TypedElement):
    workspace_no = None
    if req.elementType in [ElementType.COLLECTION.value, ElementType.SNIPPET.value, ElementType.CONFIG.value]:
        # 获取空间编号
        workspace_no = request.headers.get('x-workspace-no')
        # 校验工作空间
        workspace = workspace_dao.select_by_no(workspace_no)
        check_exists(workspace, error='工作空间不存在')
        # 校验空间权限
        check_workspace_permission(workspace_no)
    # 新增元素
    element_no = add_element(
        workspace_no=workspace_no,
        element_name=req.elementName,
        element_desc=req.elementDesc,
        element_type=req.elementType,
        element_class=req.elementClass,
        element_attrs=req.elementAttrs,
        element_props=req.elementProps
    )
    # 新增元素组件
    add_element_components(
        root_no=element_no,
        parent_no=element_no,
        components=req.elementCompos
    )
    # 记录元素变更日志
    element_created_signal.send(
        root_no=element_no,
        parent_no=None,
        element_no=element_no
    )
    # 返回元素编号
    return {'elementNo': element_no}


@http_service
def create_element_child(req):
    # 校验空间权限
    check_workspace_permission(get_workspace_no(req.rootNo))
    # 新增元素
    element_no = add_element(
        element_name=req.elementName,
        element_desc=req.elementDesc,
        element_type=req.elementType,
        element_class=req.elementClass,
        element_attrs=req.elementAttrs,
        element_props=req.elementProps
    )
    # 新增元素节点
    add_element_node(
        root_no=req.rootNo,
        parent_no=req.parentNo,
        element_no=element_no
    )
    # 新增元素组件
    add_element_components(
        root_no=req.rootNo,
        parent_no=element_no,
        components=req.elementCompos
    )
    # 记录元素变更日志
    element_created_signal.send(
        root_no=req.rootNo,
        parent_no=req.parentNo,
        element_no=element_no
    )
    # 返回元素编号
    return {'elementNo': element_no}


def add_element(
        element_name,
        element_desc,
        element_type,
        element_class,
        element_attrs: dict = None,
        element_props: dict = None,
        enabled: bool = ElementStatus.ENABLE.value,
        workspace_no = None
):
    # 创建元素
    element_no = new_id()
    TTestElement.insert(
        WORKSPACE_NO=workspace_no,
        ELEMENT_NO=element_no,
        ELEMENT_NAME=element_name,
        ELEMENT_DESC=element_desc,
        ELEMENT_TYPE=element_type,
        ELEMENT_CLASS=element_class,
        ELEMENT_ATTRS=element_attrs,
        ENABLED=enabled
    )
    # 创建元素属性
    add_element_property(element_no, element_props)
    return element_no


def add_element_node(root_no, parent_no, element_no):
    TElementChildren.insert(
        ROOT_NO=root_no,
        PARENT_NO=parent_no,
        ELEMENT_NO=element_no,
        ELEMENT_SORT=element_children_dao.next_index(parent_no)
    )


@http_service
def modify_element(req):
    # 校验空间权限
    # TODO: 空间校验改造成装饰器
    check_workspace_permission(request.headers.get('x-workspace-no'))
    # 更新元素
    update_element(
        element_no=req.elementNo,
        element_name=req.elementName,
        element_desc=req.elementDesc,
        element_attrs=req.elementAttrs,
        element_props=req.elementProps
    )
    # 更新元素组件
    update_element_components(
        parent_no=req.elementNo,
        components=req.elementCompos
    )


def update_element(
        element_no,
        element_name,
        element_desc,
        element_attrs: dict = None,
        element_props: dict = None
):
    # 查询元素
    element = test_element_dao.select_by_no(element_no)
    check_exists(element, error='元素不存在')
    # 更新元素属性
    update_element_property(element_no, element_props)
    # 记录元素变更日志
    record_element_changelog(
        element,
        new_name=element_name,
        new_desc=element_desc,
        new_attrs=element_attrs
    )
    # 更新元素
    element.update(
        ELEMENT_NAME=element_name,
        ELEMENT_DESC=element_desc,
        ELEMENT_ATTRS=element_attrs,
        UPDATED_TIME=datetime_now_by_utc8()
    )


def record_element_changelog(element: TTestElement, new_name: str, new_desc: str, new_attrs: dict):
    """记录元素变更日志（仅元素名称，元素描述，元素attrs）"""
    # 元素名称
    if element.ELEMENT_NAME != new_name:
        element_modified_signal.send(
            element_no=element.ELEMENT_NO,
            prop_name='TestElement__name',
            old_value=element.ELEMENT_NAME,
            new_value=new_name
        )
    # 元素描述
    if element.ELEMENT_DESC != new_desc:
        element_modified_signal.send(
            element_no=element.ELEMENT_NO,
            prop_name='TestElement__desc',
            old_value=element.ELEMENT_DESC,
            new_value=new_desc
        )
    # 元素属性
    old_attrs = element.attrs
    for attr_name, new_value in new_attrs.items():
        old_value = old_attrs.get(attr_name)
        if isinstance(old_value, dict | list):
            old_value = to_json(old_value)
        if isinstance(new_value, dict | list):
            new_value = to_json(new_value)
        if old_value != new_value:
            element_modified_signal.send(
            element_no=element.ELEMENT_NO,
            attr_name=attr_name,
            old_value=old_value,
            new_value=new_value
        )


@http_service
def remove_element(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))
    # 删除元素
    return delete_element(req.elementNo)


def delete_element(element_no):
    """递归删除元素"""
    # 查询元素
    element = test_element_dao.select_by_no(element_no)
    check_exists(element, error='元素不存在')
    # 删除元素子代（递归）
    delete_element_children(element_no)
    # 删除元素节点并重新排序
    delete_element_child(element_no)
    # 删除元素组件
    delete_element_components_by_parent(element_no)
    # 删除元素属性
    delete_element_property(element_no)
    # 记录元素变更日志
    element_removed_signal.send(element_no=element_no)
    # 删除元素
    element.delete()


def delete_element_children(parent_no):
    """递归删除子代元素（包含子代元素、子代属性、子代节点、元素组件和元素组件属性）"""
    # 查询所有子代节点
    nodes = element_children_dao.select_all_by_parent(parent_no)
    for node in nodes:
        # 查询子代元素
        child = test_element_dao.select_by_no(node.ELEMENT_NO)
        # 删除元素组件
        delete_element_components_by_parent(node.ELEMENT_NO)
        # 删除元素子代
        delete_element_children(node.ELEMENT_NO)
        # 删除元素属性
        delete_element_property(node.ELEMENT_NO)
        # 删除节点信息
        node.delete()
        # 删除子代元素
        child.delete()


def delete_element_child(child_no):
    # 如果存在子代节点，则删除并重新排序子代元素
    if node := element_children_dao.select_by_child(child_no):
        # 重新排序父级子代
        (
            TElementChildren
            .filter(
                TElementChildren.PARENT_NO == node.PARENT_NO,
                TElementChildren.ELEMENT_SORT > node.ELEMENT_SORT
            ).update(
                {TElementChildren.ELEMENT_SORT: TElementChildren.ELEMENT_SORT - 1}
            )
        )
        # 删除节点信息
        node.delete()


def delete_element_property(element_no):
    # 查询所有元素属性
    props = element_property_dao.select_all(element_no)
    for prop in props:
        prop.delete()


@http_service
def enable_element(req):
    # 查询元素
    element = test_element_dao.select_by_no(req.elementNo)
    check_exists(element, error='元素不存在')

    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 更新元素状态为启用，移除跳过标记
    element.update(
        SKIPED=True,
        ENABLED=ElementStatus.ENABLE.value
    )


@http_service
def disable_element(req):
    # 查询元素
    element = test_element_dao.select_by_no(req.elementNo)
    check_exists(element, error='元素不存在')

    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 更新元素状态为禁用
    element.update(ENABLED=ElementStatus.DISABLE.value)


@http_service
def skip_element(req):
    # 查询元素
    element = test_element_dao.select_by_no(req.elementNo)
    check_exists(element, error='元素不存在')

    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 标记元素状态为跳过
    element.update(SKIPED=True)


@http_service
def toggle_element_state(req):
    # 查询元素
    element = test_element_dao.select_by_no(req.elementNo)
    check_exists(element, error='元素不存在')
    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.elementNo)))
    # 更新元素状态
    state = ElementStatus.DISABLE.value if element.ENABLED == ElementStatus.ENABLE.value else ElementStatus.ENABLE.value
    element.update(ENABLED=state)


def add_element_property(element_no, element_props: dict):
    """遍历添加元素属性"""
    if element_props is None:
        return
    for prop_name, prop_value in element_props.items():
        prop_type = 'STR'
        # 转json
        if isinstance(prop_value, dict):
            prop_type = 'DICT'
            prop_value = to_json(prop_value)
        elif isinstance(prop_value, list):
            prop_type = 'LIST'
            prop_value = to_json(prop_value)
        # 新增属性
        TElementProperty.insert(
            ELEMENT_NO=element_no,
            PROPERTY_TYPE=prop_type,
            PROPERTY_NAME=prop_name,
            PROPERTY_VALUE=prop_value
        )


def update_element_property(element_no, element_props: dict):
    """遍历修改元素属性"""
    if element_props is None:
        return
    # 遍历更新元素属性
    for prop_name, prop_value in element_props.items():
        # 查询元素属性
        prop = element_property_dao.select_by_name(element_no, prop_name)
        prop_type = 'STR'
        # 转json
        if isinstance(prop_value, dict):
            prop_type = 'DICT'
            prop_value = to_json(prop_value)
        elif isinstance(prop_value, list):
            prop_type = 'LIST'
            prop_value = to_json(prop_value)

        # 有属性就更新，没有就新增（为了以后兼容新增的属性）
        if prop:
            if prop.PROPERTY_VALUE != prop_value:
                # 记录属性变更日志
                element_modified_signal.send(
                    element_no=element_no,
                    prop_name=prop_name,
                    old_value=prop.PROPERTY_VALUE,
                    new_value=prop_value
                )
                # 更新属性
                prop.update(PROPERTY_TYPE=prop_type, PROPERTY_VALUE=prop_value)
        else:
            # 新增属性
            TElementProperty.insert(
                ELEMENT_NO=element_no,
                PROPERTY_TYPE=prop_type,
                PROPERTY_NAME=prop_name,
                PROPERTY_VALUE=prop_value
            )
            # 记录属性变更日志
            element_modified_signal.send(
                element_no=element_no,
                prop_name=prop_name,
                new_value=prop_value
            )
    # 删除请求中没有的属性
    element_property_dao.delete_all_by_notin_name(element_no, list(element_props.keys()))


@http_service
def move_element(req):
    # 查询 source 元素节点
    source_node = element_children_dao.select_by_child(req.sourceNo)
    check_exists(source_node, error='来源元素父级不存在')

    # 校验元素序号
    if req.targetIndex < 0:
        raise ServiceError(msg='目标元素序号不能小于0')

    # source 父元素编号
    source_parent_no = source_node.PARENT_NO
    # source 元素序号
    source_index = source_node.ELEMENT_SORT

    # 父元素不变时，仅重新排序 source 同级元素
    if source_parent_no == req.targetParentNo:
        # 校验空间权限
        check_workspace_permission(get_workspace_no(get_root_no(req.sourceNo)))
        # 序号相等时直接跳过
        if req.targetIndex == source_node.ELEMENT_SORT:
            return
        # 元素移动类型，上移或下移
        move_type = 'UP' if source_index > req.targetIndex else 'DOWN'
        if move_type == 'UP':
            # 下移  [target, source) 区间元素
            (
                TElementChildren
                .filter(
                    TElementChildren.PARENT_NO == source_parent_no,
                    TElementChildren.ELEMENT_SORT < source_index,
                    TElementChildren.ELEMENT_SORT >= req.targetIndex
                )
                .update({
                    TElementChildren.ELEMENT_SORT: TElementChildren.ELEMENT_SORT + 1
                })
            )
        else:
            # 上移  (source, target] 区间元素
            (
                TElementChildren
                .filter(
                    TElementChildren.PARENT_NO == source_parent_no,
                    TElementChildren.ELEMENT_SORT > source_index,
                    TElementChildren.ELEMENT_SORT <= req.targetIndex,
                )
                .update({
                    TElementChildren.ELEMENT_SORT: TElementChildren.ELEMENT_SORT - 1
                })
            )
        # 更新 target 元素序号
        source_node.update(ELEMENT_SORT=req.targetIndex)
        # 记录元素变更日志
        element_sorted_signal.send(
            element_no=req.sourceNo,
            source_index=source_index,
            target_index=req.targetIndex
        )
    # source 元素移动至不同的父元素下
    else:
        # 校验空间权限
        check_workspace_permission(get_workspace_no(req.targetRootNo))
        # source 元素下方的同级元素序号 - 1（上移元素）
        (
            TElementChildren
            .filter(
                TElementChildren.PARENT_NO == source_parent_no,
                TElementChildren.ELEMENT_SORT > source_index
            )
            .update({
                TElementChildren.ELEMENT_SORT: TElementChildren.ELEMENT_SORT - 1
            })
        )
        # target 元素下方（包含 target 自身位置）的同级元素序号 + 1（下移元素）
        (
            TElementChildren
            .filter(
                TElementChildren.PARENT_NO == req.targetParentNo,
                TElementChildren.ELEMENT_SORT >= req.targetIndex
            ).update({
                TElementChildren.ELEMENT_SORT: TElementChildren.ELEMENT_SORT + 1
            })
        )
        # 移动 source 元素至 target 位置
        source_node.update(
            ROOT_NO=req.targetRootNo,
            PARENT_NO=req.targetParentNo,
            ELEMENT_SORT=req.targetIndex
        )
        # 记录元素变更日志
        element_moved_signal.send(
            element_no=req.sourceNo,
            source_no=source_parent_no,
            source_index=source_index,
            target_no=req.targetParentNo,
            target_index=req.targetIndex
        )
        # 递归修改 source 子代元素的根元素编号
        update_children_root(req.sourceNo, req.targetRootNo)

    # 校验 target 父级子代元素序号的连续性，避免埋坑
    target_child_nodes = element_children_dao.select_all_by_parent(req.targetParentNo)
    for target_index, target_node in enumerate(target_child_nodes):
        if target_node.ELEMENT_SORT != target_index + 1:
            logger.error(
                f'父级编号:[ {req.targetParentNo} ] '
                f'元素编号:[ {target_node.ELEMENT_NO} ] '
                f'元素序号:[ {target_node.ELEMENT_SORT} ] '
                f'序号连续性错误'
            )
            raise ServiceError(msg='目标元素父级的子代序号连续性错误')


def update_children_root(parent_no, root_no):
    """递归修改子代元素的根元素编号"""
    # 查询子代节点
    nodes = element_children_dao.select_all_by_parent(parent_no)
    if not nodes:
        return
    # 遍历更新根元素编号
    for node in nodes:
        node.update(ROOT_NO=root_no)
        # 递归修改
        update_children_root(node.ELEMENT_NO, root_no)

@http_service
def duplicate_element(req):
    # 查询元素
    source = test_element_dao.select_by_no(req.elementNo)
    check_exists(source, error='元素不存在')

    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 排除不支持复制的元素
    if source.ELEMENT_TYPE == ElementType.COLLECTION.value:
        raise ServiceError(msg='暂不支持复制集合')

    # 递归复制元素
    copied_no = copy_element(source)
    # 非配置元素才移动
    if source.ELEMENT_TYPE != ElementType.CONFIG.value:
        # 下移 source 元素的下方的元素
        source_node = element_children_dao.select_by_child(source.ELEMENT_NO)
        (
            TElementChildren
            .filter(
                TElementChildren.PARENT_NO == source_node.PARENT_NO,
                TElementChildren.ELEMENT_SORT > source_node.ELEMENT_SORT
            ).update({
                TElementChildren.ELEMENT_SORT: TElementChildren.ELEMENT_SORT + 1
            })
        )
        # 将 copy 元素插入 source 元素的下方
        TElementChildren.insert(
            ROOT_NO=source_node.ROOT_NO,
            PARENT_NO=source_node.PARENT_NO,
            ELEMENT_NO=copied_no,
            ELEMENT_SORT=source_node.ELEMENT_SORT + 1
        )
    # 记录元素变更日志
    element_copied_signal.send(element_no=copied_no, source_no=source.ELEMENT_NO)
    # 返回元素编号
    return {'elementNo': copied_no}


@http_service
def paste_element(req):
    # 校验空间权限
    check_workspace_permission(get_workspace_no(get_root_no(req.targetNo)))

    # 查询 source 元素
    source = test_element_dao.select_by_no(req.sourceNo)
    check_exists(source, error='来源元素不存在')

    # 查询 target 元素
    target = test_element_dao.select_by_no(req.targetNo)
    check_exists(target, error='目标元素不存在')

    # 排除不支持剪贴的元素
    if source.ELEMENT_TYPE in [ElementType.COLLECTION.value, ElementType.SNIPPET.value]:
        raise ServiceError(msg='暂不支持剪贴集合')

    # 检查元素是否允许剪贴
    check_allow_to_paste(source, target)

    if req.pasteType == PasteType.COPY.value:
        paste_element_by_copy(source, target)
    elif req.pasteType == PasteType.CUT.value:
        paste_element_by_cut(source, target)
    else:
        raise ServiceError(msg='剪贴类型非法')

def check_allow_to_paste(source: TTestElement, target: TTestElement):
    # Wroup
    if is_worker(source) and not is_collection(target):
        raise ServiceError(msg='用例仅支持在【集合】下剪贴')
    # Sampler
    elif is_sampler(source) and (
        is_collection(target) or not (is_snippet(target) or is_worker(target) or is_controller(target))
    ):
        raise ServiceError(msg='请求仅支持在【片段|用例|控制器】下剪贴')
    # Controller
    elif is_controller(source) and (
        is_collection(target) or not (is_snippet(target) or is_worker(target) or is_controller(target))
    ):
        raise ServiceError(msg='逻辑控制器仅支持在【片段|用例|控制器】下剪贴')
    # Timer
    elif is_timer(source) and (
        is_collection(target)
        or not (is_snippet(target) or is_worker(target) or is_sampler(target) or is_controller(target))
    ):
        raise ServiceError(msg='【时间控制器】仅支持在【片段|用例|控制器】节点下剪贴')
    else:
        return True


def paste_element_by_copy(source: TTestElement, target: TTestElement):
    target_no = target.ELEMENT_NO
    target_root_no = get_root_no(target_no)
    # 递归复制元素
    copied_no = copy_element(source, root_no=target_root_no)
    # 将 copy 元素插入 target 元素的最后
    TElementChildren.insert(
        ROOT_NO=target_root_no,
        PARENT_NO=target_no,
        ELEMENT_NO=copied_no,
        ELEMENT_SORT=element_children_dao.next_index(target_no)
    )
    # 记录元素变更日志
    element_copied_signal.send(element_no=copied_no, source_no=source.ELEMENT_NO)


def paste_element_by_cut(source: TTestElement, target: TTestElement):
    source_no = source.ELEMENT_NO
    target_no = target.ELEMENT_NO
    target_root_no = get_root_no(target_no)
    # 查询 source 元素节点
    source_node = element_children_dao.select_by_child(source_no)
    source_parent_no = source_node.PARENT_NO
    source_index = source_node.ELEMENT_SORT
    # 上移 source 元素下方的元素
    (
        TElementChildren
        .filter(
            TElementChildren.PARENT_NO == source_node.PARENT_NO,
            TElementChildren.ELEMENT_SORT > source_node.ELEMENT_SORT
        ).update({
            TElementChildren.ELEMENT_SORT: TElementChildren.ELEMENT_SORT - 1
        })
    )
    # 修改 source 元素节点
    target_index = element_children_dao.next_index(target_no)
    source_node.update(
        ROOT_NO=target_root_no,
        PARENT_NO=target_no,
        ELEMENT_SORT=target_index
    )
    # 递归修改 source 子代元素的根元素编号
    update_children_root(source_no, target_root_no)
    # 记录元素变更日志
    element_moved_signal.send(
        element_no=source_no,
        source_no=source_parent_no,
        source_index=source_index,
        target_no=target_no,
        target_index=target_index
    )


def copy_element(source: TTestElement, rename=False, root_no=None, workspace_no=None):
    # 克隆元素和属性
    copied_no = clone_element(source, rename, workspace_no)
    # 克隆的元素为根元素时，递归传递根元素编号
    if is_collection(source) or is_snippet(source):
        root_no = copied_no
    # 遍历克隆元素子代
    source_child_nodes = element_children_dao.select_all_by_parent(source.ELEMENT_NO)
    for source_node in source_child_nodes:
        source_child = test_element_dao.select_by_no(source_node.ELEMENT_NO)
        copied_child_no = copy_element(source_child, root_no=root_no)
        TElementChildren.insert(
            ROOT_NO=root_no or source_node.ROOT_NO,
            PARENT_NO=copied_no,
            ELEMENT_NO=copied_child_no,
            ELEMENT_SORT=source_node.ELEMENT_SORT
        )
    # 遍历克隆元素组件
    source_component_nodes = element_component_dao.select_all_by_parent(source.ELEMENT_NO)
    for source_node in source_component_nodes:
        source_component = test_element_dao.select_by_no(source_node.ELEMENT_NO)
        copied_component_no = copy_element(source_component, root_no=root_no)
        TElementComponent.insert(
            ROOT_NO=root_no or source_node.ROOT_NO,
            PARENT_NO=copied_no,
            ELEMENT_NO=copied_component_no,
            ELEMENT_SORT=source_node.ELEMENT_SORT
        )
    return copied_no


def clone_element(source: TTestElement, rename=False, workspace_no=None):
    cloned_no = new_id()
    # 克隆元素
    TTestElement.insert(
        WORKSPACE_NO=workspace_no or source.WORKSPACE_NO,
        ELEMENT_NO=cloned_no,
        ELEMENT_NAME=f'{source.ELEMENT_NAME}的副本' if rename else source.ELEMENT_NAME,
        ELEMENT_DESC=source.ELEMENT_DESC,
        ELEMENT_TYPE=source.ELEMENT_TYPE,
        ELEMENT_CLASS=source.ELEMENT_CLASS,
        ELEMENT_ATTRS=source.ELEMENT_ATTRS
    )
    # 克隆元素属性
    props = element_property_dao.select_all(source.ELEMENT_NO)
    for prop in props:
        TElementProperty.insert(
            ELEMENT_NO=cloned_no,
            PROPERTY_TYPE=prop.PROPERTY_TYPE,
            PROPERTY_NAME=prop.PROPERTY_NAME,
            PROPERTY_VALUE=prop.PROPERTY_VALUE
        )

    return cloned_no


@http_service
def query_element_components(req):
    conf_list = []
    prev_list = []
    post_list = []
    test_list = []

    # 查询元素组件节点
    nodes = element_component_dao.select_all_by_parent(req.elementNo)
    if not nodes:
        return {'confList': [], 'prevList': [], 'postList': [], 'testList': []}

    for node in nodes:
        # 查询元素组件
        if component := test_element_dao.select_by_no(node.ELEMENT_NO):
            if component.type == ElementType.CONFIG.value:
                conf_list.append({
                    'enabled': component.ENABLED,
                    'elementNo': component.ELEMENT_NO,
                    'elementName': component.ELEMENT_NAME,
                    'elementType': component.ELEMENT_TYPE,
                    'elementClass': component.ELEMENT_CLASS,
                    'elementIndex': node.ELEMENT_SORT,
                    'elementProps': get_element_property(component.ELEMENT_NO)
                })
                continue
            if component.type == ElementType.PREV_PROCESSOR.value:
                prev_list.append({
                    'enabled': component.ENABLED,
                    'elementNo': component.ELEMENT_NO,
                    'elementName': component.ELEMENT_NAME,
                    'elementType': component.ELEMENT_TYPE,
                    'elementClass': component.ELEMENT_CLASS,
                    'elementIndex': node.ELEMENT_SORT,
                    'elementProps': get_element_property(component.ELEMENT_NO)
                })
                continue
            if component.type == ElementType.POST_PROCESSOR.value:
                post_list.append({
                    'enabled': component.ENABLED,
                    'elementNo': component.ELEMENT_NO,
                    'elementName': component.ELEMENT_NAME,
                    'elementType': component.ELEMENT_TYPE,
                    'elementClass': component.ELEMENT_CLASS,
                    'elementIndex': node.ELEMENT_SORT,
                    'elementProps': get_element_property(component.ELEMENT_NO)
                })
                continue
            if component.type == ElementType.ASSERTION.value:
                test_list.append({
                    'enabled': component.ENABLED,
                    'elementNo': component.ELEMENT_NO,
                    'elementName': component.ELEMENT_NAME,
                    'elementType': component.ELEMENT_TYPE,
                    'elementClass': component.ELEMENT_CLASS,
                    'elementIndex': node.ELEMENT_SORT,
                    'elementProps': get_element_property(component.ELEMENT_NO)
                })
                continue

    # 根据序号排序
    conf_list.sort(key=lambda k: k.get('elementIndex'))
    prev_list.sort(key=lambda k: k.get('elementIndex'))
    post_list.sort(key=lambda k: k.get('elementIndex'))
    test_list.sort(key=lambda k: k.get('elementIndex'))

    return {
        'confList': conf_list,
        'prevList': prev_list,
        'postList': post_list,
        'testList': test_list
    }


def add_element_components(root_no, parent_no, components: dict) -> list:
    result = []
    if not components:
        return result
    # 分类获取组件列表
    conf_list = components.get('confList', []) or []
    prev_list = components.get('prevList', []) or []
    post_list = components.get('postList', []) or []
    test_list = components.get('testList', []) or []
    # 新增配置组件
    for component in conf_list:
        component_no = add_component(root_no, parent_no, component)
        result.append(component_no)
    # 新增前置组件
    for component in prev_list:
        component_no = add_component(root_no, parent_no, component)
        result.append(component_no)
    # 新增后置组件
    for component in post_list:
        component_no = add_component(root_no, parent_no, component)
        result.append(component_no)
    # 新增断言组件
    for component in test_list:
        component_no = add_component(root_no, parent_no, component)
        result.append(component_no)
    return result


def add_component(root_no, parent_no, component: dict):
    # 创建元素
    component_no = add_element(
        element_name=component.get('elementName'),
        element_desc=component.get('elementDesc'),
        element_type=component.get('elementType'),
        element_class=component.get('elementClass'),
        element_attrs=component.get('elementAttrs'),
        element_props=component.get('elementProps'),
        enabled=component.get('enabled', ElementStatus.ENABLE.value)
    )
    # 创建元素组件节点
    TElementComponent.insert(
        ROOT_NO=root_no,
        PARENT_NO=parent_no,
        ELEMENT_NO=component_no,
        ELEMENT_SORT=component.get('elementIndex', 0)
    )
    return component_no


def record_component_changelog(element: TTestElement, new_name):
    if element.ELEMENT_NAME != new_name:
        element_modified_signal.send(
            element_no=element.ELEMENT_NO,
            prop_name='TestElement__name',
            old_value=element.ELEMENT_NAME,
            new_value=new_name
        )


def update_element_components(parent_no: str, components: dict):
    if components is None:
        return
    # 临时存储组件编号，用于删除非请求中的元素
    numbers = []
    # 分类获取组件列表
    conf_list = components.get('confList', []) or []
    prev_list = components.get('prevList', []) or []
    post_list = components.get('postList', []) or []
    test_list = components.get('testList', []) or []
    # 更新配置组件
    for component in conf_list:
        component_no = update_component(parent_no, component)
        numbers.append(component_no)
    # 更新前置组件
    for component in prev_list:
        component_no = update_component(parent_no, component)
        numbers.append(component_no)
    # 更新后置组件
    for component in post_list:
        component_no = update_component(parent_no, component)
        numbers.append(component_no)
    # 更新断言组件
    for component in test_list:
        component_no = update_component(parent_no, component)
        numbers.append(component_no)
    # 删除非请求中的元素组件
    pending_deletes = element_component_dao.select_all_by_parent_and_notin_components(parent_no, numbers)
    for component in pending_deletes:
        # 记录元素变更日志
        element_removed_signal.send(element_no=component.ELEMENT_NO)
        # 删除组件
        component.delete()


def update_component(parent_no: str, component: dict):
    # 元素存在则更新
    if element := test_element_dao.select_by_no(component.elementNo):
        # 记录元素变更日志
        record_component_changelog(element, component.elementName)
        # 更新元素属性
        update_element_property(component.elementNo, component.get('elementProps'))
        # 更新元素信息
        element.update(ELEMENT_NAME=component.elementName, ENABLED=component.enabled)
        # 查询元素节点
        node = element_component_dao.select_by_component(component.elementNo)
        # 更新元素序号
        node.update(ELEMENT_SORT=component.elementIndex)
        # 返回元素编号
        return component.elementNo
    # 元素不存在则新增
    else:
        root_no = get_root_no(parent_no)
        # 新增元素组件
        component_no = add_component(root_no, parent_no, component)
        # 记录元素变更日志
        element_created_signal.send(root_no=root_no, parent_no=parent_no, element_no=component_no)
        # 返回元素编号
        return component_no


def delete_element_component(element_no):
    # 查询元素
    element = test_element_dao.select_by_no(element_no)
    check_exists(element, error='元素不存在')
    # 删除元素属性
    delete_element_property(element_no)
    # 删除元素
    element.delete()


def delete_element_components_by_parent(parent_no):
    # 根据父级删除所有元素组件
    if nodes := element_component_dao.select_all_by_parent(parent_no):
        for node in nodes:
            # 删除元素组件
            delete_element_component(node.ELEMENT_NO)
            # 删除元素节点
            node.delete()


@http_service
def copy_element_to_workspace(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)

    # 查询根元素
    element = test_element_dao.select_by_no(req.elementNo)
    if element.ELEMENT_TYPE not in [ElementType.COLLECTION.value, ElementType.SNIPPET.value, ElementType.CONFIG.value]:
        raise ServiceError(msg='仅支持复制【集合｜片段｜配置】')

    # 复制集合到指定的空间
    copied_no = copy_element(element, workspace_no=req.workspaceNo)

    # 记录元素变更日志
    element_copied_signal.send(element_no=copied_no, source_no=req.elementNo)


@http_service
def move_element_to_workspace(req):
    # 校验空间权限
    source_workspace_no = request.headers.get('x-workspace-no')
    target_workspace_no = req.workspaceNo
    check_workspace_permission(source_workspace_no)  # 校验来源空间权限
    check_workspace_permission(target_workspace_no)  # 校验目标空间权限
    # 查询集合或片段
    element = test_element_dao.select_by_no(req.elementNo)
    # 校验空间
    if not element.WORKSPACE_NO:
        raise ServiceError(msg='元素没有绑定空间，不支持移动')
    if element.ELEMENT_TYPE not in [ElementType.COLLECTION.value, ElementType.SNIPPET.value, ElementType.CONFIG.value]:
        raise ServiceError(msg='仅支持移动【集合｜片段｜配置】')
    # 记录元素变更日志
    element_transferred_signal.send(
        collection_no=req.elementNo,
        source_workspace_no=source_workspace_no,
        target_workspace_no=target_workspace_no
    )
    # 移动空间
    element.update(WORKSPACE_NO=target_workspace_no)


@http_service
def query_database_config_all(req):
    conds = QueryCondition(TTestElement)
    conds.equal(TTestElement.WORKSPACE_NO, req.workspaceNo)
    conds.equal(TTestElement.ELEMENT_TYPE, ElementType.CONFIG.value)
    conds.equal(TTestElement.ELEMENT_CLASS, ElementClass.DATABASE_ENGINE.value)

    items = (
        db_query(
            TTestElement.ELEMENT_NO,
            TTestElement.ELEMENT_NAME,
            TTestElement.ELEMENT_ATTRS,
            TTestElement.CREATED_TIME,
            TTestElement.UPDATED_TIME
        )
        .filter(*conds)
        .order_by(TTestElement.CREATED_TIME.desc())
        .all()
    )

    return [
        {
            'databaseNo': item.ELEMENT_NO,
            'databaseName':item.ELEMENT_NAME,
            'databaseType': item.ELEMENT_ATTRS['DatabaseEngine__database_type'],
            'createdTime': item.CREATED_TIME,
            'updatedTime': item.UPDATED_TIME
        }
        for item in items
    ]


@http_service
def query_httpheader_template_all(req):
    conds = QueryCondition(TTestElement)
    conds.equal(TTestElement.WORKSPACE_NO, req.workspaceNo)
    conds.equal(TTestElement.ELEMENT_TYPE, ElementType.CONFIG.value)
    conds.equal(TTestElement.ELEMENT_CLASS, ElementClass.HTTP_HEADER_TEMPLATE.value)

    items = (
        db_query(
            TTestElement.ELEMENT_NO,
            TTestElement.ELEMENT_NAME,
            TTestElement.CREATED_TIME,
            TTestElement.UPDATED_TIME
        )
        .filter(*conds)
        .order_by(TTestElement.CREATED_TIME.desc())
        .all()
    )

    return [
        {
            'templateNo': item.ELEMENT_NO,
            'templateName':item.ELEMENT_NAME,
            'createdTime': item.CREATED_TIME,
            'updatedTime': item.UPDATED_TIME
        }
        for item in items
    ]


@http_service
def query_httpheader_all_by_template(req):
    result = []
    for template_no in req.templates:
        # 查询请求头模板
        element = test_element_dao.select_by_no(template_no)
        if not element:
            continue

        # 获取请求头列表
        headers = element.attrs.get('HTTPHeaderTemplate__headers')

        result.extend(
            {
                'name': header['name'],
                'desc': header['desc'],
                'value': header['value'],
                'enabled': header['enabled']
            }
            for header in headers
        )

    return result
