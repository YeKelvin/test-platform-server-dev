#!/usr/bin/ python3
# @File    : element_children_dao.py
# @Time    : 2021/6/5 11:28
# @Author  : Kelvin.Ye
from app.modules.script.model import TElementChildren


def select_by_child(child_no) -> TElementChildren:
    return TElementChildren.filter_by(ELEMENT_NO=child_no).first()


def select_by_parent_and_child(parent_no, child_no) -> TElementChildren:
    return TElementChildren.filter_by(PARENT_NO=parent_no, ELEMENT_NO=child_no).first()


def select_by_parent_and_index(parent_no, child_index) -> TElementChildren:
    return TElementChildren.filter_by(PARENT_NO=parent_no, ELEMENT_SORT=child_index).first()


def count_by_parent(parent_no) -> int:
    return TElementChildren.count_by(PARENT_NO=parent_no)


def count_by_root(root_no) -> int:
    return TElementChildren.count_by(ROOT_NO=root_no)


def next_index(parent_no) -> int:
    return TElementChildren.count_by(PARENT_NO=parent_no) + 1


def select_all_by_parent(parent_no) -> list[TElementChildren]:
    return TElementChildren.filter_by(PARENT_NO=parent_no).order_by(TElementChildren.ELEMENT_SORT).all()
