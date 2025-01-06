#!/usr/bin python3
# @Module  : structure
# @File    : model.py
# @Time    : 2024-10-23 11:58:40
# @Author  : Kelvin.Ye
from app.database import BaseColumn
from app.database import TableModel
from app.database import db


class TOrganization(TableModel, BaseColumn):
    """组织表"""
    __tablename__ = 'ORGANIZATION'
    ORG_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='组织编号')
    ORG_NAME = db.Column(db.String(128), nullable=False, comment='组织名称')
    ORG_DESC = db.Column(db.String(256), comment='组织描述')
    STATE = db.Column(db.String(16), nullable=False, default='ENABLE', comment='状态(ENABLE:启用, DISABLE:禁用)')


# class TWorkspace(TableModel, BaseColumn):
#     """空间表"""
#     __tablename__ = 'WORKSPACE'
#     ORG_NO = db.Column(db.String(32), index=True, nullable=False, comment='组织编号')
#     SPACE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='空间编号')
#     SPACE_NAME = db.Column(db.String(128), nullable=False, comment='空间名称')
#     SPACE_DESC = db.Column(db.String(256), comment='空间描述')
#     SPACE_TYPE = db.Column(db.String(128), nullable=False, comment='空间类型')
#     STATE = db.Column(db.String(16), nullable=False, default='ENABLE', comment='状态(ENABLE:启用, DISABLE:禁用)')


class TProject(TableModel, BaseColumn):
    """项目表"""
    __tablename__ = 'PROJECT'
    SPACE_NO = db.Column(db.String(32), index=True, nullable=False, comment='空间编号')
    PROJECT_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='项目编号')
    PROJECT_NAME = db.Column(db.String(128), nullable=False, comment='项目名称')
    PROJECT_DESC = db.Column(db.String(256), comment='项目描述')
    STATE = db.Column(db.String(16), nullable=False, default='ENABLE', comment='状态(ENABLE:启用, DISABLE:禁用)')


class TModule(TableModel, BaseColumn):
    """模块表"""
    __tablename__ = 'MODULE'
    PROJECT_NO = db.Column(db.String(32), index=True, nullable=False, comment='项目编号')
    MODULE_NO = db.Column(db.String(32), index=True, unique=True, nullable=False, comment='模块编号')
    MODULE_NAME = db.Column(db.String(128), nullable=False, comment='模块名称')
    MODULE_DESC = db.Column(db.String(256), comment='模块描述')
    STATE = db.Column(db.String(16), nullable=False, default='ENABLE', comment='状态(ENABLE:启用, DISABLE:禁用)')
