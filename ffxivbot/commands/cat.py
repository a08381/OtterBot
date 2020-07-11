import logging
import random
from os import path

from ffxivbot.commands.cmd import CMD
from ffxivbot.handlers.QQUtils import reply_message_action


class Cat(CMD):

    def __init__(self):
        super().__init__()
        self.description = "云吸猫"
        self.use_cq_pro = True

    def index(self, *args, **kwargs):
        action_list = kwargs["action_list"]
        receive = kwargs["receive"]
        try:
            url = kwargs["global_config"]["QQ_BASE_URL"]

            msg = [
                {
                    "type": "image",
                    "data": {
                        "file": path.join(url, "static/cat/%s.jpg") % (random.randint(0, 750))
                    },
                }
            ]
            reply_action = reply_message_action(receive, msg)
            action_list.append(reply_action)
        except Exception as e:
            msg = "Error: {}".format(type(e))
            action_list.append(reply_message_action(receive, msg))
            logging.error(e)
        return action_list
