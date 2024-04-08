#!/usr/bin/ python3
# @File    : open_application_dao.py
# @Time    : 2023-04-17 18:04:35
# @Author  : Kelvin.Ye
from app.modules.opencenter.model import TOpenApplication


def select_by_no(app_no) -> TOpenApplication:
    return TOpenApplication.filter_by(APP_NO=app_no).first()


def select_by_name(app_name) -> TOpenApplication:
    return TOpenApplication.filter_by(APP_NAME=app_name).first()


def select_by_code(app_code) -> TOpenApplication:
    return TOpenApplication.filter_by(APP_CODE=app_code).first()
