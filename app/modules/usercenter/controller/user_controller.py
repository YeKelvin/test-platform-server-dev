#!/usr/bin/ python3
# @File    : user_controller.py
# @Time    : 2020/3/17 15:36
# @Author  : Kelvin.Ye
from app.modules.usercenter.controller import blueprint
from app.modules.usercenter.enum import UserState
from app.modules.usercenter.service import user_service as service
from app.tools.parser import Argument
from app.tools.parser import JsonParser
from app.tools.require import require_login
from app.tools.require import require_permission


@blueprint.post('/user/login')
def login():
    """用户登录"""
    req = JsonParser(
        Argument('loginName', required=True, nullable=False, help='账号或密码不能为空'),
        Argument('password', required=True, nullable=False, help='账号或密码不能为空'),
        Argument('index', required=True, nullable=False, help='密钥索引不能为空')
    ).parse()
    return service.login(req)


@blueprint.post('/user/login/by-enterprise')
def login_by_enterprise():
    """企业登录"""
    req = JsonParser(
        Argument('email', required=True, nullable=False, help='邮箱或密码不能为空'),
        Argument('password', required=True, nullable=False, help='邮箱或密码不能为空'),
        Argument('index', required=True, nullable=False, help='密钥索引不能为空')
    ).parse()
    return service.login_by_enterprise(req)


@blueprint.post('/user/logout')
@require_login
def logout():
    """用户登出"""
    return service.logout()


@blueprint.get('/user/info')
@require_login
def query_user_info():
    """查询个人用户信息"""
    return service.query_user_info()


@blueprint.get('/user/list')
@require_login
@require_permission
def query_user_list(CODE='QUERY_USER'):
    """分页查询用户列表"""
    req = JsonParser(
        Argument('userNo'),
        Argument('userName'),
        Argument('loginName'),
        Argument('mobile'),
        Argument('email'),
        Argument('state'),
        Argument('page', type=int, required=True, nullable=False, help='页数不能为空'),
        Argument('pageSize', type=int, required=True, nullable=False, help='每页总数不能为空')
    ).parse()
    return service.query_user_list(req)


@blueprint.get('/user/all')
@require_login
@require_permission
def query_user_all(CODE='QUERY_USER'):
    """查询全部用户"""
    return service.query_user_all()


@blueprint.post('/user')
@require_login
@require_permission
def create_user(CODE='CREATE_USER'):
    """用户注册"""
    req = JsonParser(
        Argument('loginName', required=True, nullable=False, help='登录账号不能为空'),
        Argument('userName', required=True, nullable=False, help='用户名称不能为空'),
        Argument('password', required=True, nullable=False, help='用户密码不能为空'),
        Argument('mobile'),
        Argument('email'),
        Argument('roles', type=list),
        Argument('groups', type=list)
    ).parse()
    return service.create_user(req)


@blueprint.put('/user')
@require_login
@require_permission
def modify_user(CODE='MODIFY_USER'):
    """更新用户信息"""
    req = JsonParser(
        Argument('userNo', required=True, nullable=False, help='用户编号不能为空'),
        Argument('userName', required=True, nullable=False, help='用户名称不能为空'),
        Argument('mobile'),
        Argument('email'),
        Argument('roles', type=list),
        Argument('groups', type=list)
    ).parse()
    return service.modify_user(req)


@blueprint.put('/user/state')
@require_login
@require_permission
def modify_user_state(CODE='MODIFY_USER'):
    """更新用户状态"""
    req = JsonParser(
        Argument('userNo', required=True, nullable=False, help='用户编号不能为空'),
        Argument('state', required=True, nullable=False, enum=UserState, help='用户状态不能为空')
    ).parse()
    return service.modify_user_state(req)


@blueprint.put('/user/info')
@require_login
def modify_user_info():
    """更新用户信息"""
    req = JsonParser(
        Argument('userName', required=True, nullable=False, help='用户名称不能为空'),
        Argument('mobile'),
        Argument('email')
    ).parse()
    return service.modify_user_info(req)


@blueprint.put('/user/settings')
@require_login
def modify_user_settings():
    """修改用户设置"""
    req = JsonParser(
        Argument('data', type=dict, required=True, nullable=False, help='用户设置不能为空')
    ).parse()
    return service.modify_user_settings(req)


@blueprint.put('/user/password')
@require_login
def modify_user_password():
    """修改密码"""
    req = JsonParser(
        Argument('oldPassword', required=True, nullable=False, help='旧密码不能为空'),
        Argument('newPassword', required=True, nullable=False, help='新密码不能为空'),
        Argument('index', required=True, nullable=False, help='密钥索引不能为空')
    ).parse()
    return service.modify_user_password(req)


@blueprint.put('/user/password/reset')
@require_login
@require_permission
def reset_password(CODE='RESET_PASSWORD'):
    """重置密码"""
    req = JsonParser(
        Argument('userNo', required=True, nullable=False, help='用户编号不能为空')
    ).parse()
    return service.reset_login_password(req)


@blueprint.delete('/user')
@require_login
@require_permission
def remove_user(CODE='REMOVE_USER'):
    """删除用户"""
    req = JsonParser(
        Argument('userNo', required=True, nullable=False, help='用户编号不能为空')
    ).parse()
    return service.remove_user(req)
