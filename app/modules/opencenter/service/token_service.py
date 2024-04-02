#!/usr/bin python3
# @Module  : opencenter.service
# @File    : token_service.py
# @Time    : 2024-04-02 10:58:34
# @Author  : Kelvin.Ye
import select

from app.database import db_execute
from app.modules.opencenter.dao import access_token_dao
from app.modules.opencenter.model import TAccessToken
from app.tools.identity import new_id
from app.tools.open_auth import encode_access_token
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.utils.time_util import strftime_to_timestamp


@http_service
def query_token_all(req):
    stmt = (
        select(
            TAccessToken.TOKEN_NO,
            TAccessToken.TOKEN_NAME,
            TAccessToken.TOKEN_DESC,
            TAccessToken.VALIDATED,
        )
        .where(
            TAccessToken.exclude_deleted_data(),
            TAccessToken.TOKEN_OWNER == req.owner
        )
        .order_by(TAccessToken.CREATED_TIME.desc())
    )
    entities = db_execute(stmt).all() # type: list[TAccessToken]
    return [
        {
            'tokenNo': token.TOKEN_NO,
            'tokenName': token.TOKEN_NAME,
            'tokenDesc': token.TOKEN_DESC,
            'validated': token.VALIDATED
        }
        for token in entities
    ]


@http_service
def query_token(req):
    token = access_token_dao.select_by_no(req.tokenNo)
    check_exists(token, error='令牌不存在')
    return {
        'tokenNo': token.TOKEN_NO,
        'tokenName': token.TOKEN_NAME,
        'tokenDesc': token.TOKEN_DESC,
        'permissions': token.PERMISSIONS
    }


@http_service
def create_app_token(req):
    token_no = new_id()
    token = encode_access_token(
        token_no,
        app_no=req.appNo,
        expire_time=strftime_to_timestamp(req.expireTime) if req.expireTime else None
    )
    TAccessToken.insert(
        TOKEN_NO=token_no,
        TOKEN_NAME=req.tokenName,
        TOKEN_DESC=req.tokenDesc,
        TOKEN_OWNER=req.appNo,
        PERMISSIONS=req.permissions
    )
    return {'token': token}


@http_service
def create_user_token(req):
    token_no = new_id()
    token = encode_access_token(
        token_no,
        user_no=req.userNo,
        expire_time=strftime_to_timestamp(req.expireTime) if req.expireTime else None
    )
    TAccessToken.insert(
        TOKEN_NO=token_no,
        TOKEN_NAME=req.tokenName,
        TOKEN_DESC=req.tokenDesc,
        TOKEN_OWNER=req.userNo,
        PERMISSIONS=req.permissions
    )
    return {'token': token}


@http_service
def modify_token(req):
    token = access_token_dao.select_by_no(req.tokenNo)
    check_exists(token, error='令牌不存在')
    token.update(
        TOKEN_NAME=req.tokenName,
        TOKEN_DESC=req.tokenDesc,
        PERMISSIONS=req.permissions
    )


@http_service
def remove_token(req):
    token = access_token_dao.select_by_no(req.tokenNo)
    check_exists(token, error='令牌不存在')
    token.delete()


@http_service
def invalid_token(req):
    token = access_token_dao.select_by_no(req.tokenNo)
    check_exists(token, error='令牌不存在')
    token.update(VALIDATED=False)
