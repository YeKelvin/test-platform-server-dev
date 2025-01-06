#!/usr/bin python3
# @File    : project_controller.py
# @Time    : 2024-10-23 16:46:36
# @Author  : Kelvin.Ye
from app.modules.structure.dao import project_dao
from app.modules.structure.model import TProject
from app.tools.exceptions import ServiceError
from app.tools.identity import new_id
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.utils.sqlalchemy_util import QueryCondition


@http_service
def query_project_list(req):
    # 查询项目列表
    conds = QueryCondition()
    conds.like(TProject.STATE, req.state)
    conds.like(TProject.SPACE_NO, req.spaceNo)
    conds.like(TProject.PROJECT_NO, req.projectNo)
    conds.like(TProject.PROJECT_NAME, req.projectName)
    conds.like(TProject.PROJECT_DESC, req.projectDesc)

    pagination = (
        TProject
        .filter(*conds)
        .order_by(TProject.CREATED_TIME.desc())
        .paginate(page=req.page, per_page=req.pageSize, error_out=False)
    )

    data = [
        {
            'state': project.STATE,
            'spaceNo': project.SPACE_NO,
            'projectNo': project.PROJECT_NO,
            'projectName': project.PROJECT_NAME,
            'projectDesc': project.PROJECT_DESC,
        }
        for project in pagination.items
    ]

    return {'list': data, 'total': pagination.total}


@http_service
def query_project_all():
    projects = project_dao.select_all()
    return [
        {
            'state': project.STATE,
            'spaceNo': project.SPACE_NO,
            'projectNo': project.PROJECT_NO,
            'projectName': project.PROJECT_NAME,
            'projectDesc': project.PROJECT_DESC,
        }
        for project in projects
    ]


@http_service
def query_project_info(req):
    # 查询项目
    project = project_dao.select_by_no(req.projectNo)
    check_exists(project, error='项目不存在')

    return {
        'state': project.STATE,
        'spaceNo': project.SPACE_NO,
        'projectNo': project.PROJECT_NO,
        'projectName': project.PROJECT_NAME,
        'projectDesc': project.PROJECT_DESC,
    }


@http_service
def create_project(req):
    # 唯一性校验
    if project_dao.select_by_name(req.projectName):
        raise ServiceError(msg='项目名称已存在')

    # 创建项目
    project_no = new_id()
    TProject.insert(
        STATE='ENABLE',
        SPACE_NO=req.spaceNo,
        PROJECT_NO=project_no,
        PROJECT_NAME=req.projectName,
        PROJECT_DESC=req.projectDesc,
    )

    return {'projectNo': project_no}


@http_service
def modify_project(req):
    # 查询项目
    project = project_dao.select_by_no(req.projectNo)
    check_exists(project, error='项目不存在')

    # 唯一性校验
    if project.PROJECT_NAME != req.projectName and project_dao.select_by_name(req.projectName):
        raise ServiceError(msg='项目名称已存在')

    # 更新项目信息
    project.update(
        PROJECT_NAME=req.projectName,
        PROJECT_DESC=req.projectDesc,
    )


@http_service
def modify_project_state(req):
    # 查询项目
    project = project_dao.select_by_no(req.projectNo)
    check_exists(project, error='项目不存在')

    # 更新项目状态
    project.update(STATE=req.state)


@http_service
def move_project(req):
    # TODO: 移动项目
    pass


@http_service
def remove_project(req):
    # 查询项目
    project = project_dao.select_by_no(req.projectNo)
    check_exists(project, error='项目不存在')

    # TODO: 校验项目是否存在模块和脚本，有的话怎么处理呢？？？

    # 删除项目
    project.delete()
