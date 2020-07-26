from .QQEventHandler import QQEventHandler
from .QQUtils import *
from ffxivbot.models import *
import logging
import json
import random


def QQCommand_gakki(*args, **kwargs):
    try:
        QQ_BASE_URL = kwargs["global_config"]["QQ_BASE_URL"]
        action_list = []
        receive = kwargs["receive"]
        img_url = QQ_BASE_URL + "static/gakki/%s.jpg" % (random.randint(1, 1270))
        msg = "[CQ:image,file={}]".format(img_url)
        msg = [{"type": "image", "data": {"file": img_url},}]
        reply_action = reply_message_action(receive, msg)
        action_list.append(reply_action)
        return action_list
    except Exception as e:
        msg = "Error: {}".format(type(e))
        action_list.append(reply_message_action(receive, msg))
        logging.error(e)
