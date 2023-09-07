#!/usr/bin/ python3
# @File    : log_util.py
# @Time    : 2023-04-14 15:43:04
# @Author  : Kelvin.Ye
import logging
import sys

from loguru import logger


def is_filtered_module(record, level:int , modules: list):
    return any(bool(module in record.name and record.levelno < level) for module in modules)


class InterceptHandler(logging.Handler):
    """logging转loguru的handler"""

    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # 过滤
        if is_filtered_modules(record, logging.INFO, modules=['werkzeug', 'sqlalchemy', 'apscheduler']):
            return
        if is_filtered_modules(record, logging.WARNING, modules=['httpx', 'httpcore', 'blinker', 'faker']):
            return

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def is_filtered_modules(record, logging_level, modules: list):
    for module in modules:
        if module in record.name and record.levelno < logging_level:
            return True


def trace_id(record):
    return '[traceid:{extra[traceid]}] ' if record['extra'].get('traceid') else ''


def console_formatter(record):
    name = str(record['name'])
    if 'werkzeug' in name:
        return '{message}\n{exception}'
    elif 'sqlalchemy' in name or 'apscheduler' in name:
        return (
            '<green>[{time:%Y-%m-%d %H:%M:%S.%f}]</green> '
            '<level>[{level}] ' + trace_id(record) + '{message}</level>\n'
            '{exception}'
        )
    else:
        return (
            '<green>[{time:%Y-%m-%d %H:%M:%S.%f}]</green> '
            '<level>[{level}] [{module}.{function}:{line}] ' + trace_id(record) + '{message}</level>\n'
            '{exception}'
        )


def file_formatter(record):
    name = str(record['name'])
    if 'werkzeug' in name:
        return '{message}\n{exception}'
    elif 'sqlalchemy' in name or 'apscheduler' in name:
        return '[{time:%Y-%m-%d %H:%M:%S.%f}] [{level}] ' + trace_id(record) + '{message}\n{exception}'
    else:
        return (
            '[{time:%Y-%m-%d %H:%M:%S.%f}] [{level}] [{module}.{function}:{line}] ' + trace_id(record) + '{message}\n'
            '{exception}'
        )
