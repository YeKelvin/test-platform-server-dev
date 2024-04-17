#!/usr/bin/ python3
# @File    : workspace_exemption_dao.py
# @Time    : 2022/4/22 15:51
# @Author  : Kelvin.Ye
from app.modules.system.model import TWorkspaceExemption


def select_by_workspace(workspace_no) -> TWorkspaceExemption:
    return TWorkspaceExemption.filter_by(WORKSPACE_NO=workspace_no).first()
