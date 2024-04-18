#!/usr/bin/ python3
# @File    : wecom.py
# @Time    : 2022-05-08 15:13:18
# @Author  : Kelvin.Ye
import httpx

from app.tools.exceptions import NoticeError
from app.utils.json_util import to_json


def send(webhook, data):
    res = httpx.post(
        url=webhook,
        headers={'content-type': 'application/json'},
        data=to_json(data).encode(encoding='UTF-8')
    )
    if res.status_code != 200:
        raise NoticeError(f'企业微信通知发送失败，接口响应: {res.text}')


def send_text(webhook: str, content: str, mentioned_list: list = None, mentioned_mobile_list: list = None):
    """发送文本消息

    Args:
        webhook: 机器人webhook地址
        content: 文本内容，最长不超过2048个字节，必须是utf8编码
        mentioned_list:  userid的列表，提醒群中的指定成员(@某个成员)，@all表示提醒所有人
        mentioned_mobile_list: 手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人
    """
    data = {
        'msgtype': 'text',
        'text': {
            'content': content,
            'mentioned_list': mentioned_list or [],
            'mentioned_mobile_list': mentioned_mobile_list or []
        }
    }
    send(webhook, data)


def send_markdown(webhook: str, content: str):
    """发送markdown消息

    Args:
        webhook: 机器人webhook地址: 机器人唯一标识
        content: markdown内容，最长不超过4096个字节，必须是utf8编码
    """
    data = {
        'msgtype': 'markdown',
        'markdown': {
            'content': content
        }
    }
    send(webhook, data)



def send_image(webhook: str, base64: str, md5: str):
    """发送图片消息

    Args:
        webhook: 机器人webhook地址
        base64: 图片内容的base64编码
        md5: 图片内容（base64编码前）的md5值
    """
    data = {
        'msgtype': 'image',
        'image': {
            'base64': base64,
            'md5': md5
        }
    }
    send(webhook, data)


def send_news(webhook: str, articles: list):
    """发送图文消息

    Args:
        webhook: 机器人webhook地址
        articles: 图文消息，一个图文消息支持1到8条图文
            - title: 标题，不超过128个字节，超过会自动截断
            - description: 描述，不超过512个字节，超过会自动截断
            - url: 点击后跳转的链接
            - picurl: 图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150
    """
    data = {
        'msgtype': 'news',
        'news': {
            'articles': articles
        }
    }
    send(webhook, data)


def send_file(webhook: str, media_id: str):
    """发送文件消息

    Args:
        webhook: 机器人webhook地址
        media_id: 文件id，通过文件上传接口获取
    """
    data = {
        'msgtype': 'file',
        'file': {
            'media_id': media_id
        }
    }
    send(webhook, data)


def send_template_card(webhook: str, card: dict):
    """发送模板卡片消息"""
    data = {
        'msgtype': 'template_card',
        'template_card': card
    }
    send(webhook, data)
