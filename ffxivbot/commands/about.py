import logging

from ffxivbot.commands.cmd import CMD
from ffxivbot.handlers.QQUtils import reply_message_action


class About(CMD):

    def __init__(self):
        super().__init__()
        self.description = "关于项目"

    def index(self, *args, **kwargs):
        action_list = kwargs["action_list"]
        receive = kwargs["receive"]
        try:

            res_data = {
                "url": "https://github.com/Bluefissure/FFXIVBOT",
                "title": "FFXIVBOT",
                "content": "by Bluefissure",
                "image": "https://i.loli.net/2018/05/06/5aeeda6f1fd4f.png",
            }
            msg = [{"type": "share", "data": res_data}]

            reply_action = reply_message_action(receive, msg)
            action_list.append(reply_action)
        except Exception as e:
            msg = "Error: {}".format(type(e))
            action_list.append(reply_message_action(receive, msg))
            logging.error(e)
        return action_list
