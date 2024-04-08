#!/usr/bin python3
# @Module  : opencenter.dao
# @File    : open_access_token_dao.py
# @Time    : 2024-04-02 11:46:55
# @Author  : Kelvin.Ye
from app.modules.opencenter.model import TOpenAccessToken


def select_by_no(token_no) -> TOpenAccessToken:
    return TOpenAccessToken.filter_by(TOKEN_NO=token_no).first()
