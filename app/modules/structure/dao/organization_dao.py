#!/usr/bin python3
# @File    : organization_dao.py
# @Time    : 2024-10-28 17:02:20
# @Author  : Kelvin.Ye
from app.modules.structure.model import TOrganization


def select_by_no(org_no) -> TOrganization:
    return TOrganization.filter_by(ORG_NO=org_no).first()


def select_by_name(org_name) -> TOrganization:
    return TOrganization.filter_by(ORG_NAME=org_name).first()


def select_all() -> list[TOrganization]:
    return TOrganization.filter_by().order_by(TOrganization.CREATED_TIME.desc()).all()
