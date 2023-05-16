#!/usr/bin/ python3
# @File    : job_service.py
# @Time    : 2022/5/20 11:17
# @Author  : Kelvin.Ye
from apscheduler.jobstores.base import JobLookupError

from app.extension import apscheduler
from app.modules.schedule.dao import schedule_job_dao as schedule_job_dao
from app.tools.exceptions import ServiceError
from app.tools.service import http_service
from app.tools.validator import check_exists
from app.tools.validator import check_workspace_permission


@http_service
def query_job_info(req):
    # 查询定时任务
    task = schedule_job_dao.select_by_no(req.jobNo)
    check_exists(task, error_msg='任务不存在')

    # 查询作业信息
    try:
        job = apscheduler.get_job(req.jobNo)
    except JobLookupError as e:
        raise ServiceError('查找作业失败，作业不存在或已失效') from e

    return {
        'id': job.id,
        'name': job.name,
        'func': job.func,
        'args': job.args,
        'kwargs': job.kwargs,
        'trigger': job.trigger,
        'month': job.month,
        'day': job.day,
        'day_of_week': job.day_of_week,
        'hour': job.hour,
        'minute': job.minute,
        'misfire_grace_time': job.misfire_grace_time,
        'max_instances': job.max_instances,
        'next_run_time': job.next_run_time
    }


@http_service
def run_job(req):
    # 查询定时任务
    task = schedule_job_dao.select_by_no(req.jobNo)
    check_exists(task, error_msg='任务不存在')

    # 校验空间权限
    check_workspace_permission(task.WORKSPACE_NO)

    # 立即运行作业
    apscheduler.run_job(req.jobNo)
