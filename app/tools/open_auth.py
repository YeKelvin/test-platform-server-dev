#!/usr/bin python3
# @Module  : tools
# @File    : open_auth.py
# @Time    : 2024-04-02 15:21:41
# @Author  : Kelvin.Ye
import time

import jwt

from app import config as CONFIG
from app.utils.jwt_util import jwt_decode
from app.utils.jwt_util import jwt_encode


def encode_access_token(token_no, app_no=None, user_no=None, expire_time=None):
    """序列化token"""
    # 生成payload
    payload = {'token_no': token_no}
    if app_no:
        payload['app_no'] = app_no
    if user_no:
        payload['user_no'] = user_no
    if expire_time:
        payload['expire_time'] = expire_time
    # 序列化token
    return jwt_encode(payload, CONFIG.JWT_SECRET_KEY)


def decode_access_token(token) -> dict:
    """反序列token"""
    # 解码token
    payload = jwt_decode(token, CONFIG.JWT_SECRET_KEY, options=None)
    # 校验有效期
    exp = payload.get('expire_time')
    if exp and int(exp) < int(time.time()):
        raise jwt.ExpiredSignatureError
    return payload
