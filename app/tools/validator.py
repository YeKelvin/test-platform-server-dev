#!/usr/bin/ python3
# @File    : validator.py
# @Time    : 2019/11/21 15:04
# @Author  : Kelvin.Ye
import enum

from flask import g
from flask import request

from app.modules.opencenter.model import TOpenAccessToken
from app.modules.public.model import TWorkspaceRestriction
from app.modules.public.model import TWorkspaceRestrictionExemption
from app.modules.public.model import TWorkspaceUser
from app.modules.usercenter.model import TGroupMember
from app.modules.usercenter.model import TPermission
from app.modules.usercenter.model import TRole
from app.modules.usercenter.model import TUser
from app.modules.usercenter.model import TUserRole
from app.tools.exceptions import ServiceError
from app.utils.sqlalchemy_util import QueryCondition


def check_absent(obj: any, error: str = '校验失败') -> None:
    """检查obj对象是否不存在，如果存在就抛异常"""
    if obj:
        raise ServiceError(msg=error)


def check_exists(obj: any, error: str = '校验失败') -> None:
    """检查obj对象是否存在，如果不存在就抛异常"""
    if not obj:
        raise ServiceError(msg=error)


def check_enum(string: str, enumeration: enum, error: str = '校验失败'):
    """校验枚举"""
    if string not in enumeration.__members__:
        raise ServiceError(msg=error)


def get_workspace_no_by_request():
    # 优先读取请求头中的空间编号
    workspace_no = request.headers.get('x-workspace-no')
    if not workspace_no:
        # 其次读取请求参数中的空间编号
        args = request.json if request.is_json else request.values.to_dict()
        workspace_no = args.get('workspaceNo')
    return workspace_no


def get_user_workspaces(user_no) -> list:
    return [entity.WORKSPACE_NO for entity in TWorkspaceUser.filter_by(USER_NO=user_no).all()]


def get_user_groups(user_no) -> list:
    return [entity.GROUP_NO for entity in TGroupMember.filter_by(USER_NO=user_no).all()]


def is_super_admin(user_no):
    conds = QueryCondition(TUser, TRole, TUserRole)
    conds.equal(TRole.ROLE_CODE, 'ADMIN')
    conds.equal(TUserRole.USER_NO, user_no)
    conds.equal(TUserRole.USER_NO, TUser.USER_NO)
    conds.equal(TUserRole.ROLE_NO, TRole.ROLE_NO)
    return bool(TUser.filter(*conds).first())


def exists_workspace_restriction(workspace_no):
    permission_code = getattr(g, 'permission_code', None)
    if not permission_code:
        return False
    conds = QueryCondition(TPermission, TWorkspaceRestriction)
    conds.equal(TPermission.PERMISSION_CODE, permission_code)
    conds.equal(TWorkspaceRestriction.WORKSPACE_NO, workspace_no)
    conds.equal(TWorkspaceRestriction.PERMISSION_NO, TPermission.PERMISSION_NO)
    return bool(TWorkspaceRestriction.filter(*conds).first())


def is_restriction_exemption_member(workspace_no, user_no):
    # 查询空间显示豁免
    exemption = TWorkspaceRestrictionExemption.filter_by(WORKSPACE_NO=workspace_no).first()
    # 校验用户是否为豁免成员
    if user_no in exemption.USERS:
        return True
    # 校验用户所在分组是否为豁免分组
    return any(group_no in exemption.GROUPS for group_no in get_user_groups(user_no))


def check_workspace_permission(workspace_no=None) -> None:
    """全局空间只有超级管理员可以操作"""
    # 没有指定空间编号时自动从请求头或请求参数中提取
    if not workspace_no:
        workspace_no = get_workspace_no_by_request()

    # 仍然获取不到空间编号时报错
    if not workspace_no:
        raise ServiceError(msg='未指定工作空间')

    # 校验应用令牌是否有操作空间的权限
    if hasattr(g, 'app_no'):
        if (
            TOpenAccessToken
            .filter(
                TOpenAccessToken.TOKEN_NO == g.token_no,
                TOpenAccessToken.WORKSPACES.contains(f'["{workspace_no}"]')
            )
            .first()
        ):
            return
        raise ServiceError(msg='应用无空间操作权限')

    # 获取用户编号
    user_no = getattr(g, 'user_no', None)
    if user_no is None:
        raise ServiceError(msg='空间权限校验失败，用户未登录')

    # 判断用户是否是操作空间的成员
    user_workspaces = get_user_workspaces(user_no)
    if workspace_no not in user_workspaces:
        if is_super_admin(user_no):
            return
        raise ServiceError(msg='空间权限不足，用户非目标空间成员')

    # 校验是否存在空间限制
    if not exists_workspace_restriction(workspace_no):
        return

    # 校验用户是否为豁免成员
    if is_restriction_exemption_member(workspace_no, user_no):
        return

    # 校验是否为超级管理员
    if is_super_admin(user_no):
        return

    raise ServiceError(msg='空间权限不足')
