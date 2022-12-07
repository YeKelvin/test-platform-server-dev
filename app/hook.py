#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : hook.py
# @Time    : 2019/11/7 20:02
# @Author  : Kelvin.Ye
import traceback

import jwt
from flask import g
from flask import request
from ulid import microsecond as ulid

from app.extension import db
from app.system.model import TSystemOperationLog
from app.tools import globals
from app.tools.auth import JWTAuth
from app.tools.logger import get_logger
from app.tools.response import http_response


log = get_logger(__name__)


def set_trace_id():
    """设置当前请求的全局 TraceID"""
    trace_id = getattr(g, 'trace_id', None)
    if not trace_id:
        g.trace_id = ulid.new().str


def set_user():
    """设置当前请求的全局user信息"""
    # 排除指定的请求
    if ('/user/login' in request.path) and ('POST' in request.method):
        return

    # 判断请求头部是否包含Authorization属性
    if 'Authorization' in request.headers:
        access_toekn = request.headers.get('Authorization')
        # noinspection PyBroadException
        try:
            # 解析token，获取payload
            payload = JWTAuth.decode_token(access_toekn)
            # 设置全局属性
            globals.put('user_no', payload['data']['id'])
            globals.put('issued_at', payload['iat'])
        except jwt.ExpiredSignatureError:
            log.info(f'accessToken:[ {access_toekn} ] token已失效')
        except jwt.InvalidTokenError:
            log.info(f'accessToken:[ {access_toekn} ] 无效的token')
        except Exception:
            log.error(traceback.format_exc())


def add_operation_log():
    # 过滤无需记录的操作
    if request.method not in ['POST', 'PUT', 'PATCH', 'DELETE'] or '/execute' in request.path:
        return
    # 记录操作日志
    oplog = TSystemOperationLog()
    oplog.LOG_NO = g.trace_id,
    oplog.OPERATION_SOURCE = 'HTTP'
    oplog.OPERATION_METHOD = request.method,
    oplog.OPERATION_ENDPOINT = request.path
    db.session.add(oplog)
    db.session.flush()


def cross_domain_access(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'

    if request.method == 'OPTIONS':
        response.headers['Access-Control-Max-Age'] = 60 * 60 * 24
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE'

    return response


# app.register_error_handler(404, page_not_found)
def page_not_found(_):
    return http_response(errorMsg='Resource not found'), 404


# app.register_error_handler(Exception, exception_handler)
def exception_handler(ex):
    log.exception(ex)
    return http_response(errorMsg='服务器开小差')
