#!/usr/bin/ python3
# @File    : model.py
# @Time    : 2023-04-11 18:18:01
# @Author  : Kelvin.Ye
from sqlalchemy.dialects.postgresql import JSONB

from app.database import BaseColumn
from app.database import TableModel
from app.database import db


class TOpenApplication(TableModel, BaseColumn):
    """开放应用表"""
    __tablename__ = 'OPEN_APPLICATION'
    APP_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='应用编号')
    APP_NAME = db.Column(db.String(128), nullable=False, comment='应用名称')
    APP_CODE = db.Column(db.String(64), unique=True, comment='应用代码')
    APP_DESC = db.Column(db.String(256), comment='应用描述')
    STATE = db.Column(db.String(16), nullable=False, default='ENABLE', comment='应用状态(ENABLE:启用, DISABLE:禁用)')


class TOpenAccessToken(TableModel, BaseColumn):
    """访问令牌表"""
    __tablename__ = 'OPEN_ACCESS_TOKEN'
    TOKEN_NO = db.Column(db.String(32), index=True, nullable=False, comment='令牌编号')
    TOKEN_NAME = db.Column(db.String(32), nullable=False, comment='令牌名称')
    TOKEN_DESC = db.Column(db.String(32), comment='令牌描述')
    TOKEN_OWNER = db.Column(db.String(32), comment='令牌持有人')
    WORKSPACES = db.Column(JSONB, comment='空间列表')
    PERMISSIONS = db.Column(JSONB, comment='权限列表')
    EXPIRE_TIME = db.Column(db.DateTime(), comment='失效时间')
    LAST_USED_TIME = db.Column(db.DateTime(), comment='最后使用时间')


class TOpenApiLog(TableModel, BaseColumn):
    """OpenAPI日志表"""
    __tablename__ = 'OPEN_API_LOG'
    LOG_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='日志编号')
    APP_NO = db.Column(db.String(32), index=True, comment='应用编号')
    USER_NO = db.Column(db.String(32), index=True, comment='用户编号')
    DESC = db.Column(db.String(256), comment='请求描述')
    IP = db.Column(db.String(32), comment='请求IP')
    URI = db.Column(db.String(256), comment='请求路径')
    METHOD = db.Column(db.String(128), comment='请求方法')
    REQUEST = db.Column(db.Text(), comment='请求数据')
    RESPONSE = db.Column(db.Text(), comment='响应数据')
    SUCCESS = db.Column(db.Boolean(), comment='是否成功')
    ELAPSED_TIME = db.Column(db.Integer(), comment='服务耗时')
