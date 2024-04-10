#!/usr/bin/ python3
# @File    : permission_service.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye

from sqlalchemy import select

from app.database import db_execute
from app.modules.usercenter.model import TModule
from app.modules.usercenter.model import TObject
from app.modules.usercenter.model import TPermission
from app.tools.service import http_service
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_permission_all(req):
    conds = QueryCondition()
    conds.include(TModule.MODULE_CODE, req.moduleCodes)
    conds.include(TObject.OBJECT_CODE, req.objectCodes)
    conds.include(TPermission.PERMISSION_ACT, req.actIncludes)
    conds.exclude(TPermission.PERMISSION_ACT, req.actExcludes)
    stmt = (
        select(
            TModule.MODULE_NO,
            TModule.MODULE_NAME,
            TModule.MODULE_CODE,
            TObject.OBJECT_NO,
            TObject.OBJECT_NAME,
            TObject.OBJECT_CODE,
            TPermission.PERMISSION_NO,
            TPermission.PERMISSION_NAME,
            TPermission.PERMISSION_DESC,
            TPermission.PERMISSION_CODE
        )
        .outerjoin(TObject, TObject.OBJECT_NO == TPermission.OBJECT_NO)
        .outerjoin(TModule, TModule.MODULE_NO == TPermission.MODULE_NO)
        .where(*conds)
        .order_by(TModule.MODULE_CODE.asc(), TObject.OBJECT_CODE.asc())
    )
    entities = db_execute(stmt).all() # type: list[TModule | TObject | TPermission]
    return [
        {
            'moduleNo': entity.MODULE_NO,
            'moduleName': entity.MODULE_NAME,
            'moduleCode': entity.MODULE_CODE,
            'objectNo': entity.OBJECT_NO,
            'objectName': entity.OBJECT_NAME,
            'objectCode': entity.OBJECT_CODE,
            'permissionNo': entity.PERMISSION_NO,
            'permissionName': entity.PERMISSION_NAME,
            'permissionDesc': entity.PERMISSION_DESC,
            'permissionCode': entity.PERMISSION_CODE
        }
        for entity in entities
    ]
