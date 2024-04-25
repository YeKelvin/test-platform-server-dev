#!/usr/bin/ python3
# @File    : workspace_member_dao.py
# @Time    : 2021/6/5 23:27
# @Author  : Kelvin.Ye
from app.modules.system.model import TWorkspaceMember


def select_by_workspace_and_user(workspace_no, user_no) -> TWorkspaceMember:
    return TWorkspaceMember.filter_by(WORKSPACE_NO=workspace_no, USER_NO=user_no).first()


def count_by_workspace(workspace_no) -> int:
    return TWorkspaceMember.count_by(WORKSPACE_NO=workspace_no)


def select_all_by_user(user_no) -> list[TWorkspaceMember]:
    return TWorkspaceMember.filter_by(USER_NO=user_no).all()


def delete_all_by_workspace_and_notin_user(workspace_no, *args) -> None:
    TWorkspaceMember.deletes(
        TWorkspaceMember.WORKSPACE_NO == workspace_no,
        TWorkspaceMember.USER_NO.notin_(*args)
    )
