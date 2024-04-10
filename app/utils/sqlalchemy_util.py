#!/usr/bin/ python3
# @File    : sqlalchemy_util.py
# @Time    : 2020/1/6 17:07
# @Author  : Kelvin.Ye
from loguru import logger
from sqlalchemy.dialects import postgresql


def paginate(page, page_size):
    offset = (int(page) - 1) * int(page_size)
    limit = int(page_size)
    return offset, limit


class QueryCondition(list):

    def __init__(self, *agrs):
        super().__init__()
        for arg in agrs:
            self.join(arg)

    def join(self, table, condition=None):
        if table:
            self.append(table.DELETED == 0)
        if condition:
            self.append(condition)

    def add(self, condition):
        self.append(condition)

    def like(self, column, value):
        """模糊匹配"""
        if value:
            self.append(column.like(f'%{value}%'))

    def equal(self, column, value):
        """完全匹配"""
        if value:
            self.append(column == value)

    def unequal(self, column, value):
        """不相等"""
        if value:
            self.append(column != value)

    def lt(self, column, value):
        """小于(less than)"""
        if value:
            self.append(column < value)

    def le(self, column, value):
        """小于等于(less than or equal to)"""
        if value:
            self.append(column <= value)

    def gt(self, column, value):
        """大于(greater than)"""
        if value:
            self.append(column > value)

    def ge(self, column, value):
        """大于等于(greater than or equal to)"""
        if value:
            self.append(column >= value)

    def include(self, column, *args):
        """包含（in）"""
        if args := [arg for arg in args if arg]:
            self.append(column.in_(*args))

    def exclude(self, column, *args):
        """排除（not in）"""
        if args := [arg for arg in args if arg]:
            self.append(column.notin_(*args))


def show_statement(stmt):
    logger.info(str(
        stmt
        .compile(
            dialect=postgresql.dialect(paramstyle="named"),
            compile_kwargs={"literal_binds": True}
        )
    ))


def show_query_statement(query):
    logger.info(
        query.statement.compile(
            dialect=postgresql.dialect(paramstyle="named"),
            compile_kwargs={"literal_binds": True}
        )
    )
