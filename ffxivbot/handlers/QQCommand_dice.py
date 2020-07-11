from .QQEventHandler import QQEventHandler
from .QQUtils import *
from ffxivbot.models import *
import logging
import json
import random
import dice


def QQCommand_dice(*args, **kwargs):
    action_list = []
    receive = kwargs["receive"]
    try:
        QQ_BASE_URL = kwargs["global_config"]["QQ_BASE_URL"]

        dice_msg = receive["message"].replace("/dice", "", 1).strip()

        if len(dice_msg) > 50:
            return action_list

        pa = re.compile(r'(\d+)(d\d+)')
        pos = 0
        while True:
            ma = pa.search(dice_msg, pos)
            if ma:
                i = int(ma.group(1))
                if i > 10:
                    dice_msg = dice_msg.replace(ma.group(0), "10" + ma.group(2))
                    ma = pa.search(dice_msg, pos)
                pos = ma.span(0)[1]
            else:
                break

        msg = "[CQ:at,qq={}]".format(receive["user_id"])
        msg += str(dice.roll(dice_msg))
        reply_action = reply_message_action(receive, msg)
        action_list.append(reply_action)
        return action_list
    except Exception as e:
        msg = "Error: {}".format(type(e))
        action_list.append(reply_message_action(receive, msg))
        logging.error(e)
    return action_list
