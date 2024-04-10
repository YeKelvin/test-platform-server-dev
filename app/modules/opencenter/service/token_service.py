#!/usr/bin python3
# @Module  : opencenter.service
# @File    : token_service.py
# @Time    : 2024-04-02 10:58:34
# @Author  : Kelvin.Ye
from sqlalchemy import distinct
from sqlalchemy import or_
from sqlalchemy import select

from app.database import db_execute
from app.modules.opencenter.dao import open_access_token_dao
from app.modules.opencenter.model import TOpenAccessToken
from app.modules.public.model import TWorkspace
from app.modules.usercenter.model import TObject
from app.modules.usercenter.model import TPermission
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.open_auth import encode_access_token
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.utils.time_util import TIMEFMT
from app.utils.time_util import strftime_to_timestamp


@http_service
def query_token_all(req):
    stmt = (
        select(
            TOpenAccessToken.TOKEN_NO,
            TOpenAccessToken.TOKEN_NAME,
            TOpenAccessToken.TOKEN_DESC,
            TOpenAccessToken.WORKSPACES,
            TOpenAccessToken.PERMISSIONS,
            TOpenAccessToken.EXPIRE_TIME,
            TOpenAccessToken.CREATED_TIME,
            TOpenAccessToken.LAST_USED_TIME
        )
        .where(
            TOpenAccessToken.exclude_deleted_data(),
            TOpenAccessToken.TOKEN_OWNER == req.owner
        )
        .order_by(TOpenAccessToken.CREATED_TIME.desc())
    )
    entities = db_execute(stmt).all() # type: list[TOpenAccessToken]
    return [
        {
            'tokenNo': token.TOKEN_NO,
            'tokenName': token.TOKEN_NAME,
            'tokenDesc': token.TOKEN_DESC,
            'objects': get_permission_objects(token.PERMISSIONS),
            'workspaces': get_workspace_names(token.WORKSPACES),
            'expireTime': token.EXPIRE_TIME.strftime(r'%Y-%m-%d') if token.EXPIRE_TIME else None,
            'createdTime': token.CREATED_TIME.strftime(TIMEFMT),
            'lastUsedTime': token.LAST_USED_TIME.strftime(TIMEFMT) if token.LAST_USED_TIME else None
        }
        for token in entities
    ]


@http_service
def query_token(req):
    token = open_access_token_dao.select_by_no(req.tokenNo)
    check_exists(token, error='令牌不存在')
    return {
        'tokenNo': token.TOKEN_NO,
        'tokenName': token.TOKEN_NAME,
        'tokenDesc': token.TOKEN_DESC,
        'expireTime': token.EXPIRE_TIME.strftime(r'%Y-%m-%d') if token.EXPIRE_TIME else None,
        'workspaces': token.WORKSPACES,
        'permissions': token.PERMISSIONS,
    }


@http_service
def create_app_token(req):
    # 生成令牌
    token_no = new_id()
    token = encode_access_token(
        token_no,
        app_no=req.appNo,
        expire_time=strftime_to_timestamp(req.expireTime, format=r'%Y-%m-%d') if req.expireTime else None
    )
    # 校验是否存在同名token
    if open_access_token_dao.exists_by_name(req.appNo, req.tokenName):
        raise ServiceError(msg='同名令牌已存在')
    # 记录令牌
    TOpenAccessToken.insert(
        TOKEN_NO=token_no,
        TOKEN_NAME=req.tokenName,
        TOKEN_DESC=req.tokenDesc,
        TOKEN_OWNER=req.appNo,
        EXPIRE_TIME=req.expireTime or None,
        WORKSPACES=req.workspaces,
        PERMISSIONS=req.permissions
    )
    return {'token': token}


@http_service
def create_user_token(req):
    # 生成令牌
    token_no = new_id()
    token = encode_access_token(
        token_no,
        user_no=req.userNo,
        expire_time=strftime_to_timestamp(req.expireTime, format=r'%Y-%m-%d') if req.expireTime else None
    )
    # 校验是否存在同名token
    if open_access_token_dao.exists_by_name(req.appNo, req.tokenName):
        raise ServiceError(msg='同名令牌已存在')
    # 记录令牌
    TOpenAccessToken.insert(
        TOKEN_NO=token_no,
        TOKEN_NAME=req.tokenName,
        TOKEN_DESC=req.tokenDesc,
        TOKEN_OWNER=req.userNo,
        PEXPIRE_TIME=req.expireTime or None,
        WORKSPACES=req.workspaces,
        PERMISSIONS=req.permissions
    )
    return {'token': token}


@http_service
def modify_token(req):
    # 查询令牌
    token = open_access_token_dao.select_by_no(req.tokenNo)
    check_exists(token, error='令牌不存在')
    # 校验是否存在同名token
    if req.tokenName != token.TOKEN_NAME and open_access_token_dao.exists_by_name(token.TOKEN_OWNER, req.tokenName):
        raise ServiceError(msg='同名令牌已存在')
    # 更新令牌
    token.update(
        TOKEN_NAME=req.tokenName,
        TOKEN_DESC=req.tokenDesc,
        WORKSPACES=req.workspaces,
        PERMISSIONS=req.permissions
    )


@http_service
def remove_token(req):
    # 查询令牌
    token = open_access_token_dao.select_by_no(req.tokenNo)
    check_exists(token, error='令牌不存在')
    # 物理删除，留着也没用
    token.physical_delete()


def get_workspace_names(workspaces) -> list[str]:
    """根据空间列表获取对应的空间名称"""
    if not workspaces:
        return []
    stmt = (
        select(TWorkspace.WORKSPACE_NAME)
        .where(or_(*[TWorkspace.WORKSPACE_NO == number for number in workspaces]))
    )
    return list(db_execute(stmt).scalars())


def get_permission_objects(permissions) -> list[str]:
    """根据权限列表获取对应的操作对象名称（去重）"""
    if not permissions:
        return []
    stmt = (
        select(
            distinct(TObject.OBJECT_NAME)
        )
        .outerjoin(TPermission, TPermission.OBJECT_NO == TObject.OBJECT_NO)
        .where(
            or_(*[TPermission.PERMISSION_NO == number for number in permissions])
        )
    )
    return list(db_execute(stmt).scalars())
