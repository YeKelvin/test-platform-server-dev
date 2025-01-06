#!/usr/bin python3
# @File    : module_controller.py
# @Time    : 2024-10-23 16:47:29
# @Author  : Kelvin.Ye
from app.modules.structure.dao import module_dao
from app.modules.structure.model import TModule
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_module_list(req):
    # 查询模块列表
    conds = QueryCondition()
    conds.like(TModule.STATE, req.state)
    conds.like(TModule.MODULE_NO, req.moduleNo)
    conds.like(TModule.MODULE_NAME, req.moduleName)
    conds.like(TModule.MODULE_DESC, req.moduleDesc)

    pagination = (
        TModule
        .filter(*conds)
        .order_by(TModule.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'state': module.STATE,
            'moduleNo': module.MODULE_NO,
            'moduleName': module.MODULE_NAME,
            'moduleDesc': module.MODULE_DESC,
        }
        for module in pagination.items
    ]

    return {'list': data, 'total': pagination.total}


@http_service
def query_module_all():
    modules = module_dao.select_all()
    return [
        {
            'state': module.STATE,
            'moduleNo': module.MODULE_NO,
            'moduleName': module.MODULE_NAME,
            'moduleDesc': module.MODULE_DESC,
        }
        for module in modules
    ]


@http_service
def query_module_info(req):
    # 查询模块
    module = module_dao.select_by_no(req.moduleNo)
    check_exists(module, error='模块不存在')

    return {
        'state': module.STATE,
        'moduleNo': module.MODULE_NO,
        'moduleName': module.MODULE_NAME,
        'moduleDesc': module.MODULE_DESC,
    }


@http_service
def create_module(req):
    # 唯一性校验
    if module_dao.select_by_name(req.moduleName):
        raise ServiceError(msg='模块名称已存在')

    # 创建模块
    module_no = new_id()
    TModule.insert(
        STATE='ENABLE',
        MODULE_NO=module_no,
        MODULE_NAME=req.moduleName,
        MODULE_DESC=req.moduleDesc,
    )

    return {'moduleNo': module_no}


@http_service
def modify_module(req):
    # 查询模块
    module = module_dao.select_by_no(req.moduleNo)
    check_exists(module, error='模块不存在')

    # 唯一性校验
    if module.MODULE_NAME != req.moduleName and module_dao.select_by_name(req.moduleName):
        raise ServiceError(msg='模块名称已存在')

    # 更新模块信息
    module.update(
        MODULE_NAME=req.moduleName,
        MODULE_DESC=req.moduleDesc,
    )


@http_service
def modify_module_state(req):
    # 查询模块
    module = module_dao.select_by_no(req.moduleNo)
    check_exists(module, error='模块不存在')

    # 更新模块状态
    module.update(STATE=req.state)


@http_service
def move_module(req):
    # TODO: 移动模块
    pass


@http_service
def remove_module(req):
    # 查询模块
    module = module_dao.select_by_no(req.moduleNo)
    check_exists(module, error='模块不存在')

    # 查询模块空间列表
    # module_space_list = module_space_dao.select_all_by_moduleno(req.moduleNo)
    # TODO: 校验模块是否存在脚本，有的话怎么处理呢？？？

    # 删除模块
    module.delete()
