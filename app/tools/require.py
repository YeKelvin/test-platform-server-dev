#!/usr/bin/ python3
# @File    : require.py
# @Time    : 2020/1/14 10:49
# @Author  : Kelvin.Ye
import inspect

from datetime import datetime
from functools import wraps

import jwt

from flask import g
from flask import request
from loguru import logger
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy import select

from app.extension import db
from app.modules.opencenter.model import TOpenAccessToken
from app.modules.usercenter.model import TGroup
from app.modules.usercenter.model import TGroupMember
from app.modules.usercenter.model import TGroupRole
from app.modules.usercenter.model import TPermission
from app.modules.usercenter.model import TRole
from app.modules.usercenter.model import TRolePermission
from app.modules.usercenter.model import TUser
from app.modules.usercenter.model import TUserLoginLog
from app.modules.usercenter.model import TUserRole
from app.tools import localvars
from app.tools.auth import JWTAuth
from app.tools.exceptions import ServiceStatus
from app.tools.response import ResponseDTO
from app.tools.response import http_response


def require_login(func):
    """登录校验装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        user_no = None
        issued_at = None
        # 校验access-token
        if 'access-token' not in request.headers:
            # 缺失请求头
            return failed_response(ServiceStatus.CODE_401, msg='缺失令牌')
        # 获取access-token
        access_toekn = request.headers.get('access-token')
        try:
            # 解析token，获取payload
            payload = JWTAuth.decode_token(access_toekn)
            user_no = payload['data']['id']
            issued_at = payload['iat']
            # 存储用户编号
            localvars.set('user_no', user_no)
        except jwt.ExpiredSignatureError:
            return failed_response(ServiceStatus.CODE_401, msg='令牌已失效')
        except jwt.InvalidTokenError:
            return failed_response(ServiceStatus.CODE_401, msg='无效的令牌')
        except Exception:
            logger.bind(traceid=g.trace_id).exception()
            return failed_response(ServiceStatus.CODE_500)

        # 用户不存在
        user = TUser.filter_by(USER_NO=user_no).first()
        if not user:
            logger.bind(traceid=g.trace_id).info('用户不存在')
            return failed_response(ServiceStatus.CODE_401)

        # 用户未登录，请先登录
        if not user.LOGGED_IN:
            logger.bind(traceid=g.trace_id).info('用户未登录')
            return failed_response(ServiceStatus.CODE_401)

        # 用户状态异常
        if user.STATE != 'ENABLE':
            logger.bind(traceid=g.trace_id).info('用户状态异常')
            return failed_response(ServiceStatus.CODE_401)

        # 用户最后成功登录时间和 token 签发时间不一致，即 token 已失效
        user_login_log = TUserLoginLog.filter_by(USER_NO=user_no).order_by(TUserLoginLog.CREATED_TIME.desc()).first()
        if user_login_log.LOGIN_TIME != datetime.fromtimestamp(issued_at):
            logger.bind(traceid=g.trace_id).info('令牌已失效')
            return failed_response(ServiceStatus.CODE_401)

        localvars.set('operator', user.USER_NAME)
        return func(*args, **kwargs)

    return wrapper


def require_permission(func):
    """权限校验装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 获取权限代码
        code = inspect.signature(func).parameters.get('CODE').default

        # 获取登录用户
        user_no = localvars.get_user_no()
        if not user_no:
            logger.bind(traceid=g.trace_id).info(
                f'method:[ {request.method} ] path:[ {request.path} ] 获取用户编号失败'
            )
            return failed_response(ServiceStatus.CODE_403)

        # 查询用户权限，判断权限是否存在且状态正常
        if exists_user_permission(user_no, code):
            localvars.set('permission_code', code)  # 存储权限唯一代码
            return func(*args, **kwargs)

        # 超级管理员无需校验权限
        if is_super_admin(user_no):
            return func(*args, **kwargs)

        # 其余情况校验不通过
        logger.bind(traceid=g.trace_id).info(
            f'method:[ {request.method} ] path:[ {request.path} ] 角色无此权限，或状态异常'
        )
        return failed_response(ServiceStatus.CODE_403)

    return wrapper


def require_open_permission(func):
    """OpenAPI校验装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 校验access-token
        if 'access-token' not in request.headers:
            # 缺失请求头
            return failed_response(ServiceStatus.CODE_401, msg='缺失令牌')
        try:
            # 解析token，获取payload
            payload = JWTAuth.decode_token(request.headers['access-token'])
            app_no = payload.get('app_no')
            user_no = payload.get('user_no')
            token_no = payload.get('token_no')
            # 存储应用编号
            app_no and localvars.set('app_no', app_no)
            # 存储用户编号
            user_no and localvars.set('user_no', user_no)
        except jwt.ExpiredSignatureError:
            return failed_response(ServiceStatus.CODE_401, msg='令牌已失效')
        except jwt.InvalidTokenError:
            return failed_response(ServiceStatus.CODE_401, msg='无效的令牌')
        except Exception:
            logger.bind(traceid=g.trace_id).exception()
            return failed_response(ServiceStatus.CODE_500)

        # 获取权限代码
        code = inspect.signature(func).parameters.get('CODE').default
        # 查询令牌
        token = TOpenAccessToken.filter_by(TOKEN_NO=token_no).first()  # type: TOpenAccessToken
        # 查询权限
        stmt = (
            select(
                TPermission.PERMISSION_CODE
            )
            .where(
                and_(
                    TPermission.PERMISSION_CODE == code,
                    or_(*[TPermission.PERMISSION_NO == number for number in token.PERMISSIONS])
                )
            )
        )
        # 令牌有权限则返回响应
        if db.session.execute(stmt).first():
            localvars.set('external_invoke', True)
            return func(*args, **kwargs)

        # 其余情况校验不通过
        logger.bind(traceid=g.trace_id).info(f'method:[ {request.method} ] path:[ {request.path} ] 令牌无此权限')
        return failed_response(ServiceStatus.CODE_403)

    return wrapper



def failed_response(error: ServiceStatus, msg=None):
    logger.bind(traceid=g.trace_id).info(
        f'uri:[ {request.method} {request.path} ] '
        f'header:[ {dict(request.headers)} ] request:[ {dict(request.values)} ]'
    )
    res = ResponseDTO(msg=msg or error.MSG, code=error.CODE)
    http_res = http_response(res)
    logger.bind(traceid=g.trace_id).info(
        f'uri:[ {request.method} {request.path} ] '
        f'header:[ {dict(http_res.headers)}] response:[ {res} ]'
    )
    return http_res


def get_user_roles(user_no):
    user_role_stmt = db.session.query(
        TRole.ROLE_NO
    ).filter(
        TRole.DELETED == 0,
        TRole.STATE == 'ENABLE',
        TUserRole.DELETED == 0,
        TUserRole.USER_NO == user_no,
        TUserRole.ROLE_NO == TRole.ROLE_NO,
    )
    group_role_stmt = db.session.query(
        TRole.ROLE_NO
    ).filter(
        TGroup.DELETED == 0,
        TGroup.STATE == 'ENABLE',
        TRole.DELETED == 0,
        TRole.STATE == 'ENABLE',
        TGroupMember.DELETED == 0,
        TGroupMember.USER_NO == user_no,
        TGroupMember.GROUP_NO == TGroup.GROUP_NO,
        TGroupRole.DELETED == 0,
        TGroupRole.ROLE_NO == TRole.ROLE_NO,
        TGroupRole.GROUP_NO == TGroupMember.GROUP_NO,
    )
    return [entity.ROLE_NO for entity in user_role_stmt.union(group_role_stmt).all()]


def exists_user_permission(user_no, code):
    conds = [
        TPermission.DELETED == 0,
        TPermission.PERMISSION_CODE == code,
        TRolePermission.DELETED == 0,
        TRolePermission.ROLE_NO.in_(get_user_roles(user_no)),
        TRolePermission.PERMISSION_NO == TPermission.PERMISSION_NO
    ]
    return db.session.query(TPermission.PERMISSION_NO).filter(*conds).first()


def is_super_admin(user_no):
    superadmin = db.session.query(
        TRole.ROLE_NO
    ).filter(
        TRole.DELETED == 0,
        TRole.STATE == 'ENABLE',
        TRole.ROLE_CODE == 'ADMIN',
        TUserRole.DELETED == 0,
        TUserRole.USER_NO == user_no,
        TUserRole.ROLE_NO == TRole.ROLE_NO
    ).first()
    return bool(superadmin)
