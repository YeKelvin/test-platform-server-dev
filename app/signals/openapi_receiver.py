#!/usr/bin python3
# @File    : openapi_subscriber.py
# @Time    : 2023-04-21 18:25:08
# @Author  : Kelvin.Ye
from flask import g
from loguru import logger

from app.extension import db
from app.modules.opencenter.model import TOpenApiLog
from app.signals import openapi_log_signal
from app.tools.cache import API_DOC_STORAGER
from app.utils.json_util import to_json


# resrapi排除列表
EXCLUDED_URI = ['/run', '/execute']


@openapi_log_signal.connect
def record_openapi_log(sender, method, uri, request, response, success, elapsed):
    """记录openapi调用日志（POST、PUT、DELETE）"""
    try:
        # 仅记录POST、PUT或DELETE的请求
        if method not in ['POST', 'PUT', 'DELETE']:
            return
        # 过滤指定路径的请求
        for path in EXCLUDED_URI:
            if path in uri:
                return
        # 获取接口描述
        desc = API_DOC_STORAGER.get(f'{method}://{uri}')
        if not desc:
            logger.warning(f'uri:[ {method} {uri} ] 缺失接口描述')
        # 记录日志
        record = TOpenApiLog()
        record.LOG_NO=g.trace_id,
        record.APP_NO=getattr(g, 'app_no', None),
        record.USER_NO=getattr(g, 'user_no', None),
        record.DESC=desc,
        record.IP=g.ip,
        record.URI=uri,
        record.METHOD=method,
        record.REQUEST=to_json(request),
        record.RESPONSE=to_json(response),
        record.SUCCESS=success
        record.ELAPSED_TIME=elapsed
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        logger.exception(str(e))
