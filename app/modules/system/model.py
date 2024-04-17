#!/usr/bin/ python3
# @File    : model.py
# @Time    : 2019/11/7 9:54
# @Author  : Kelvin.Ye
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from app.database import BaseColumn
from app.database import TableModel
from app.database import db


class TTag(TableModel, BaseColumn):
    """标签表"""
    __tablename__ = 'TAG'
    TAG_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='标签编号')
    TAG_NAME = db.Column(db.String(256), nullable=False, comment='标签名称')
    TAG_DESC = db.Column(db.String(256), nullable=False, comment='标签描述')
    UniqueConstraint('TAG_NAME', 'DELETED', name='unique_tagname')


class TWorkspace(TableModel, BaseColumn):
    """工作空间表"""
    __tablename__ = 'WORKSPACE'
    WORKSPACE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='空间编号')
    WORKSPACE_NAME = db.Column(db.String(128), nullable=False, comment='空间名称')
    WORKSPACE_DESC = db.Column(db.String(256), comment='空间描述')
    WORKSPACE_SCOPE = db.Column(db.String(128), nullable=False, comment='空间作用域')
    UniqueConstraint('WORKSPACE_NAME', 'WORKSPACE_SCOPE', 'DELETED', name='unique_name_scope')


class TWorkspaceUser(TableModel, BaseColumn):
    """空间用户表"""
    __tablename__ = 'WORKSPACE_USER'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    USER_NO = db.Column(db.String(32), index=True, nullable=False, comment='用户编号')
    UniqueConstraint('WORKSPACE_NO', 'USER_NO', 'DELETED', name='unique_workspace_user')


class TWorkspaceRestriction(TableModel, BaseColumn):
    """空间限制表"""
    __tablename__ = 'WORKSPACE_RESTRICTION'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    PERMISSION_NO = db.Column(db.String(32), index=True, nullable=False, comment='权限编号')


class TWorkspaceExemption(TableModel, BaseColumn):
    """空间豁免表"""
    __tablename__ = 'WORKSPACE_EXEMPTION'
    WORKSPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    USERS = db.Column(JSONB, comment='豁免用户列表')
    GROUPS = db.Column(JSONB, comment='豁免分组列表')


class TRestApiLog(TableModel, BaseColumn):
    """RestAPI日志表"""
    __tablename__ = 'REST_API_LOG'
    LOG_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='日志编号')
    DESC = db.Column(db.String(256), comment='请求描述')
    IP = db.Column(db.String(32), comment='请求IP')
    URI = db.Column(db.String(256), comment='请求路径')
    METHOD = db.Column(db.String(128), comment='请求方法')
    REQUEST = db.Column(db.Text(), comment='请求数据')
    RESPONSE = db.Column(db.Text(), comment='响应数据')
    SUCCESS = db.Column(db.Boolean(), comment='是否成功')
    ELAPSED_TIME = db.Column(db.Integer(), comment='服务耗时')


class TSystemDataChangelog(TableModel, BaseColumn):
    """系统数据变更日志表"""
    __tablename__ = 'SYSTEM_DATA_CHANGELOG'
    LOG_NO = db.Column(db.String(64), index=True, nullable=False, comment='日志编号')
    ACTION = db.Column(db.String(32), nullable=False, comment='动作(INSERT:新增, UPDATE:修改, DELETE:删除)')
    TABLE = db.Column(db.String(128), comment='表名')
    ROWID = db.Column(db.Integer(), comment='行ID')
    FIELD = db.Column(db.String(128), comment='字段名')
    OLD_VALUE = db.Column(db.Text(), comment='旧值')
    NEW_VALUE = db.Column(db.Text(), comment='新值')
