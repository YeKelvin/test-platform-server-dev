#!/usr/bin/ python3
# @File    : enum.py
# @Time    : 2020/7/3 15:07
# @Author  : Kelvin.Ye
from enum import Enum
from enum import unique


@unique
class WorkspaceScope(Enum):

    # 默认空间，每个用户注册后都有一个默认空间
    DEFAULT = 'DEFAULT'

    # 个人空间
    PERSONAL = 'PERSONAL'

    # 团队空间，空间成员才能使用此空间
    TEAM = 'TEAM'

    # 公共空间，所有用户都可以使用
    PUBLIC = 'PUBLIC'
