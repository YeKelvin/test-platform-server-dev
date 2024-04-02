#!/usr/bin/ python3
# @File    : variables_service.py
# @Time    : 2020/3/13 16:59
# @Author  : Kelvin.Ye
from flask import request
from sqlalchemy import and_

from app.modules.script.dao import variable_dao
from app.modules.script.dao import variable_dataset_dao
from app.modules.script.enum import VariableDatasetType
from app.modules.script.enum import VariableDatasetWeight
from app.modules.script.model import TVariable
from app.modules.script.model import TVariableDataset
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.service import http_service
from app.tools.validator import check_absent
from app.tools.validator import check_exists
from app.tools.validator import check_workspace_permission
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_dataset_list(req):
    # 条件查询
    conds = QueryCondition()
    conds.like(TVariableDataset.WORKSPACE_NO, req.workspaceNo)
    conds.like(TVariableDataset.DATASET_NO, req.datasetNo)
    conds.like(TVariableDataset.DATASET_NAME, req.datasetName)
    conds.like(TVariableDataset.DATASET_TYPE, req.datasetType)
    conds.like(TVariableDataset.DATASET_DESC, req.datasetDesc)

    # 条件分页查询
    pagination = (
        TVariableDataset
        .filter(*conds)
        .order_by(TVariableDataset.DATASET_WEIGHT.desc(), TVariableDataset.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'datasetNo': item.DATASET_NO,
            'datasetName': item.DATASET_NAME,
            'datasetType': item.DATASET_TYPE,
            'datasetDesc': item.DATASET_DESC,
            'datasetBinding': item.DATASET_BINDING
        }
        for item in pagination.items
    ]

    return {'list': data, 'total': pagination.total}


@http_service
def query_dataset_all(req):
    # 条件查询
    conds = QueryCondition()
    conds.equal(TVariableDataset.WORKSPACE_NO, req.workspaceNo)
    conds.equal(TVariableDataset.DATASET_TYPE, req.datasetType)

    results = (
        TVariableDataset
        .filter(and_(*conds) | (TVariableDataset.DATASET_TYPE == VariableDatasetType.GLOBAL.value))
        .order_by(TVariableDataset.DATASET_WEIGHT.desc(), TVariableDataset.CREATED_TIME.desc())
        .all()
    )

    return [
        {
            'datasetNo': item.DATASET_NO,
            'datasetName': item.DATASET_NAME,
            'datasetType': item.DATASET_TYPE,
            'datasetDesc': item.DATASET_DESC,
            'datasetBinding': item.DATASET_BINDING
        }
        for item in results
    ]


@http_service
def create_dataset(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)

    # 查询变量集信息
    dataset = variable_dataset_dao.select_first(
        WORKSPACE_NO=req.workspaceNo,
        DATASET_NAME=req.datasetName,
        DATASET_TYPE=req.datasetType
    )
    check_absent(dataset, error='变量集已存在')

    # 变量集为ENVIRONMENT或CUSTOM时，工作空间编号不能为空
    if req.datasetType != VariableDatasetType.GLOBAL.value and not req.workspaceNo:
        raise ServiceError(msg='空间编号不能为空')

    # 新增变量集
    dataset_no = new_id()
    TVariableDataset.insert(
        WORKSPACE_NO=req.workspaceNo,
        DATASET_NO=dataset_no,
        DATASET_NAME=req.datasetName,
        DATASET_TYPE=req.datasetType,
        DATASET_DESC=req.datasetDesc,
        DATASET_WEIGHT=VariableDatasetWeight[req.datasetType].value,
        DATASET_BINDING=req.datasetBinding
    )

    return {'datasetNo': dataset_no}


@http_service
def modify_dataset(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error='变量集不存在')

    # 更新变量集信息
    dataset.update(
        DATASET_NAME=req.datasetName,
        DATASET_DESC=req.datasetDesc,
        DATASET_BINDING=req.datasetBinding
    )


@http_service
def remove_dataset(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))
    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error='变量集不存在')
    # 删除变量集下的所有变量
    variable_dao.delete_all_by_dataset(req.datasetNo)
    # 删除变量集
    dataset.delete()


@http_service
def create_variable(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 查询变量信息
    variable = variable_dao.select_by_dataset_and_name(req.datasetNo, req.variableName)
    check_absent(variable, error='变量集已存在')

    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error='变量集不存在')

    # 新增变量
    variable_no = new_id()
    TVariable.insert(
        DATASET_NO=req.datasetNo,
        VARIABLE_NO=variable_no,
        VARIABLE_NAME=req.variableName.strip() if req.variableName else req.variableName,
        VARIABLE_DESC=req.variableDesc.strip() if req.variableDesc else req.variableDesc,
        INITIAL_VALUE=req.initialValue.strip() if req.initialValue else req.initialValue,
        CURRENT_VALUE=req.currentValue.strip() if req.currentValue else req.currentValue,
        ENABLED=True
    )

    return variable_no


@http_service
def modify_variable(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 查询变量信息
    variable = variable_dao.select_by_no(req.variableNo)
    check_exists(variable, error='变量不存在')

    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(variable.DATASET_NO)
    check_exists(dataset, error='变量集不存在')

    # 更新变量信息
    variable.update(
        VARIABLE_NAME=req.variableName.strip() if req.variableName else req.variableName,
        VARIABLE_DESC=req.variableDesc.strip() if req.variableDesc else req.variableDesc,
        INITIAL_VALUE=req.initialValue.strip() if req.initialValue else req.initialValue,
        CURRENT_VALUE=req.currentValue.strip() if req.currentValue else req.currentValue
    )


@http_service
def remove_variable(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 查询变量信息
    variable = variable_dao.select_by_no(req.variableNo)
    check_exists(variable, error='变量不存在')

    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(variable.DATASET_NO)
    check_exists(dataset, error='变量集不存在')

    # 删除变量
    variable.delete()


@http_service
def enable_variable(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 查询变量信息
    variable = variable_dao.select_by_no(req.variableNo)
    check_exists(variable, error='变量不存在')

    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(variable.DATASET_NO)
    check_exists(dataset, error='变量集不存在')

    # 启用变量
    variable.update(ENABLED=True)


@http_service
def disable_variable(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 查询变量信息
    variable = variable_dao.select_by_no(req.variableNo)
    check_exists(variable, error='变量不存在')

    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(variable.DATASET_NO)
    check_exists(dataset, error='变量集不存在')

    # 禁用变量
    variable.update(ENABLED=False)


@http_service
def update_current_value(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 查询变量信息
    variable = variable_dao.select_by_no(req.variableNo)
    check_exists(variable, error='变量不存在')

    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(variable.DATASET_NO)
    check_exists(dataset, error='变量集不存在')

    # 更新当前值
    variable.update(CURRENT_VALUE=req.value.strip() if req.value else req.value)


@http_service
def query_variable_by_dataset(req):
    variables = variable_dao.select_all_by_dataset(req.datasetNo)

    return [
        {
            'variableNo': variable.VARIABLE_NO,
            'variableName': variable.VARIABLE_NAME,
            'variableDesc': variable.VARIABLE_DESC,
            'initialValue': variable.INITIAL_VALUE,
            'currentValue': variable.CURRENT_VALUE,
            'enabled': variable.ENABLED
        }
        for variable in variables
    ]


@http_service
def query_variables(req):
    result = []
    for dataset_no in req.datasets:
        # 查询变量集信息
        dataset = variable_dataset_dao.select_by_no(dataset_no)
        if not dataset:
            continue

        # 查询变量列表
        variables = variable_dao.select_all_by_dataset(dataset_no)

        result.extend(
            {
                'datasetNo': dataset.DATASET_NO,
                'datasetName': dataset.DATASET_NAME,
                'variableNo': variable.VARIABLE_NO,
                'variableName': variable.VARIABLE_NAME,
                'variableDesc': variable.VARIABLE_DESC,
                'initialValue': variable.INITIAL_VALUE,
                'currentValue': variable.CURRENT_VALUE,
                'enabled': variable.ENABLED
            }
            for variable in variables
        )

    return result


@http_service
def create_variables(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error='变量集不存在')

    for vari in req.variableList:
        # 跳过变量名为空的数据
        if not vari.variableName:
            continue

        # 查询变量信息
        variable = variable_dao.select_by_dataset_and_name(req.datasetNo, vari.variableName)
        check_absent(variable, error=f'变量名称:[ {vari.variableName} ] 变量已存在')

        # 新增变量
        TVariable.insert(
            DATASET_NO=req.datasetNo,
            VARIABLE_NO=new_id(),
            VARIABLE_NAME=vari.variableName.strip() if vari.variableName else vari.variableName,
            VARIABLE_DESC=vari.variableDesc.strip() if vari.variableDesc else vari.variableDesc,
            INITIAL_VALUE=vari.initialValue.strip() if vari.initialValue else vari.initialValue,
            CURRENT_VALUE=vari.currentValue.strip() if vari.currentValue else vari.currentValue,
            ENABLED=True
        )


@http_service
def modify_variables(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))
    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error='变量集不存在')
    # 遍历更新变量
    for vari in req.variableList:
        # 跳过变量名为空的数据
        if not vari.variableName:
            continue

        if 'variableNo' in vari:
            # 查询变量信息
            variable = variable_dao.select_by_no(vari.variableNo)
            check_exists(variable, error='变量不存在')
            # 更新变量信息
            variable.update(
                VARIABLE_NAME=vari.variableName.strip() if vari.variableName else vari.variableName,
                VARIABLE_DESC=vari.variableDesc.strip() if vari.variableDesc else vari.variableDesc,
                INITIAL_VALUE=vari.initialValue.strip() if vari.initialValue else vari.initialValue,
                CURRENT_VALUE=vari.currentValue.strip() if vari.currentValue else vari.currentValue,
                ENABLED=vari.enabled
            )
        else:
            # 查询变量信息
            variable = variable_dao.select_by_dataset_and_name(req.datasetNo, vari.variableName)
            check_absent(variable, error=f'变量名称:[ {vari.variableName} ] 变量已存在')
            # 新增变量
            TVariable.insert(
                DATASET_NO=req.datasetNo,
                VARIABLE_NO=new_id(),
                VARIABLE_NAME=vari.variableName.strip() if vari.variableName else vari.variableName,
                VARIABLE_DESC=vari.variableDesc.strip() if vari.variableDesc else vari.variableDesc,
                INITIAL_VALUE=vari.initialValue.strip() if vari.initialValue else vari.initialValue,
                CURRENT_VALUE=vari.currentValue.strip() if vari.currentValue else vari.currentValue,
                ENABLED=vari.enabled
            )


@http_service
def remove_variables(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))
    # 查询变量集信息
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error='变量集不存在')
    # 批量删除变量
    variable_dao.delete_in_no(req.variables)


@http_service
def duplicate_dataset(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 查询变量集
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error='变量集不存在')

    # 复制变量集
    new_dataset_no = new_id()
    TVariableDataset.insert(
        WORKSPACE_NO=dataset.WORKSPACE_NO,
        DATASET_NO=new_dataset_no,
        DATASET_NAME=f'{dataset.DATASET_NAME} copy',
        DATASET_TYPE=dataset.DATASET_TYPE,
        DATASET_DESC=dataset.DATASET_DESC,
        DATASET_WEIGHT=dataset.DATASET_WEIGHT
    )

    # 复制变量
    variables = variable_dao.select_all_by_dataset(req.datasetNo)
    for variable in variables:
        TVariable.insert(
            DATASET_NO=new_dataset_no,
            VARIABLE_NO=new_id(),
            VARIABLE_NAME=variable.VARIABLE_NAME,
            VARIABLE_DESC=variable.VARIABLE_DESC,
            INITIAL_VALUE=variable.INITIAL_VALUE,
            CURRENT_VALUE=variable.CURRENT_VALUE,
            ENABLED=True
        )

    return {'datasetNo': new_dataset_no}


@http_service
def copy_dataset_to_workspace(req):
    # 校验空间权限
    check_workspace_permission(request.headers.get('x-workspace-no'))

    # 查询变量集
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error='变量集不存在')

    # 复制变量集
    new_dataset_no = new_id()
    TVariableDataset.insert(
        WORKSPACE_NO=req.workspaceNo,
        DATASET_NO=new_dataset_no,
        DATASET_NAME=f'{dataset.DATASET_NAME} copy',
        DATASET_TYPE=dataset.DATASET_TYPE,
        DATASET_DESC=dataset.DATASET_DESC,
        DATASET_WEIGHT=dataset.DATASET_WEIGHT
    )

    # 复制变量
    variables = variable_dao.select_all_by_dataset(req.datasetNo)
    for variable in variables:
        TVariable.insert(
            DATASET_NO=new_dataset_no,
            VARIABLE_NO=new_id(),
            VARIABLE_NAME=variable.VARIABLE_NAME,
            VARIABLE_DESC=variable.VARIABLE_DESC,
            INITIAL_VALUE=variable.INITIAL_VALUE,
            CURRENT_VALUE=variable.CURRENT_VALUE,
            ENABLED=True
        )

    return {'datasetNo': new_dataset_no}


@http_service
def move_dataset_to_workspace(req):
    # 校验空间权限
    check_workspace_permission(req.workspaceNo)
    # 查询变量集
    dataset = variable_dataset_dao.select_by_no(req.datasetNo)
    check_exists(dataset, error='变量集不存在')
    # 移动变量集
    dataset.update(WORKSPACE_NO=req.workspaceNo)
