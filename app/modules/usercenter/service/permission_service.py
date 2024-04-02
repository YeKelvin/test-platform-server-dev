#!/usr/bin/ python3
# @File    : permission_service.py
# @Time    : 2020/3/17 15:37
# @Author  : Kelvin.Ye
import select

from app.database import db_execute
from app.database import db_query
from app.modules.usercenter.model import TPermission
from app.modules.usercenter.model import TPermissionModule
from app.modules.usercenter.model import TPermissionObject
from app.tools.service import http_service
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_permission_all(req):
    conds = QueryCondition(TPermissionModule, TPermissionObject, TPermission)
    conds.equal(TPermissionModule.MODULE_NO, TPermission.MODULE_NO)
    conds.equal(TPermissionObject.OBJECT_NO, TPermission.OBJECT_NO)
    conds.in_(TPermissionModule.MODULE_CODE, req.moduleCodes)
    conds.in_(TPermissionObject.OBJECT_CODE, req.objectCodes)
    conds.notin_(TPermission.PERMISSION_ACT, req.actExcludes)
    resutls = (
        db_query(
            TPermissionModule.MODULE_NO,
            TPermissionModule.MODULE_NAME,
            TPermissionModule.MODULE_CODE,
            TPermissionObject.OBJECT_NO,
            TPermissionObject.OBJECT_NAME,
            TPermissionObject.OBJECT_CODE,
            TPermission.PERMISSION_NO,
            TPermission.PERMISSION_NAME,
            TPermission.PERMISSION_DESC,
            TPermission.PERMISSION_CODE,
            TPermission.STATE
        )
        .filter(*conds)
        .order_by(TPermissionModule.MODULE_CODE.asc(), TPermissionObject.OBJECT_CODE.asc())
        .all()
    )
    return [
        {
            'moduleNo': resutl.MODULE_NO,
            'moduleName': resutl.MODULE_NAME,
            'moduleCode': resutl.MODULE_CODE,
            'objectNo': resutl.OBJECT_NO,
            'objectName': resutl.OBJECT_NAME,
            'objectCode': resutl.OBJECT_CODE,
            'permissionNo': resutl.PERMISSION_NO,
            'permissionName': resutl.PERMISSION_NAME,
            'permissionDesc': resutl.PERMISSION_DESC,
            'permissionCode': resutl.PERMISSION_CODE,
            'state': resutl.STATE
        }
        for resutl in resutls
    ]


@http_service
def query_open_permission_all(req):
    stmt = (
        select(
            TPermissionModule.MODULE_NO,
            TPermissionModule.MODULE_NAME,
            TPermissionModule.MODULE_CODE,
            TPermissionObject.OBJECT_NO,
            TPermissionObject.OBJECT_NAME,
            TPermissionObject.OBJECT_CODE,
            TPermission.PERMISSION_NO,
            TPermission.PERMISSION_NAME,
            TPermission.PERMISSION_DESC,
            TPermission.PERMISSION_CODE
        )
        .outerjoin(TPermissionObject, TPermissionObject.OBJECT_NO == TPermission.OBJECT_NO)
        .outerjoin(TPermissionModule, TPermissionModule.MODULE_NO == TPermission.MODULE_NO)
        .where(
            TPermissionModule.MODULE_CODE.notin_(['USERCENTER', 'OPENCENTER', 'SYSTEM'])
        )
        .order_by(TPermissionModule.MODULE_CODE.asc(), TPermissionObject.OBJECT_CODE.asc())
    )
    entities = db_execute(stmt).all() # type: list[TPermission | TPermissionModule | TPermissionObject]
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
