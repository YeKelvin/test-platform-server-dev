#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sqlalchemy-util
# @Time    : 2020/1/6 17:07
# @Author  : Kelvin.Ye
from server.librarys.request import RequestDTO


def get_page_number_info(req: RequestDTO):
    offset = (int(req.attr.page) - 1) * int(req.attr.pageSize)
    limit = int(req.attr.pageSize)
    return offset, limit
