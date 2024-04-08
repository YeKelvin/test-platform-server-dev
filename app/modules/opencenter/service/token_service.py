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
from app.modules.usercenter.model import TObject
from app.modules.usercenter.model import TPermission
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
        'permissions': token.PERMISSIONS,
    }


@http_service
def create_app_token(req):
    token_no = new_id()
    token = encode_access_token(
        token_no,
        app_no=req.appNo,
        expire_time=strftime_to_timestamp(req.expireTime, format=r'%Y-%m-%d') if req.expireTime else None
    )
    TOpenAccessToken.insert(
        TOKEN_NO=token_no,
        TOKEN_NAME=req.tokenName,
        TOKEN_DESC=req.tokenDesc,
        TOKEN_OWNER=req.appNo,
        EXPIRE_TIME=req.expireTime,
        PERMISSIONS=req.permissions
    )
    return {'token': token}


@http_service
def create_user_token(req):
    token_no = new_id()
    token = encode_access_token(
        token_no,
        user_no=req.userNo,
        expire_time=strftime_to_timestamp(req.expireTime, format=r'%Y-%m-%d') if req.expireTime else None
    )
    TOpenAccessToken.insert(
        TOKEN_NO=token_no,
        TOKEN_NAME=req.tokenName,
        TOKEN_DESC=req.tokenDesc,
        TOKEN_OWNER=req.userNo,
        PEXPIRE_TIME=req.expireTime,
        PERMISSIONS=req.permissions
    )
    return {'token': token}


@http_service
def modify_token(req):
    token = open_access_token_dao.select_by_no(req.tokenNo)
    check_exists(token, error='令牌不存在')
    token.update(
        TOKEN_NAME=req.tokenName,
        TOKEN_DESC=req.tokenDesc,
        PERMISSIONS=req.permissions
    )


@http_service
def remove_token(req):
    token = open_access_token_dao.select_by_no(req.tokenNo)
    check_exists(token, error='令牌不存在')
    token.physical_delete()  # 物理删除，留着也没用


def get_permission_objects(permissions) -> list[str]:
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
