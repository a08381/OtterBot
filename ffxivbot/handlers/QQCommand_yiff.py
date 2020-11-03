import json
import logging
import os
import random
import time
import traceback
import urllib.parse

import requests

from ffxivbot.models import *
from .QQUtils import *

corrector = TagCompletion(os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "yiff_tags.json"))


def is_nsfw(item):
    if "cum" in item["tags"]["general"] or "penis" in item["tags"]["general"] or "sex" in item["tags"]["general"]:
        return True


def QQCommand_yiff(*args, **kwargs):
    action_list = []
    receive = kwargs["receive"]
    try:
        QQ_BASE_URL = kwargs["global_config"]["QQ_BASE_URL"]
        bot = kwargs["bot"]
        if time.time() < bot.api_time + bot.long_query_interval:
            msg = "技能冷却中"
        else:
            msg = "What does the fox say?"
            second_command_msg = receive["message"].replace("/yiff", "", 1).strip()
            if bot.r18 and random.randint(0, 10) != 0:
                alter_tags = HsoAlterName.objects.all()
                tags = list(filter(lambda x : x, second_command_msg.split(" ")))
                if tags:
                    for alter in alter_tags:
                        if alter.name in tags:
                            tags[tags.index(alter.name)] = alter.key
                    # tags = list(map(corrector.select_tag, tags))
                    tags_params = "+".join(list(map(urllib.parse.quote, tags)))
                    if "female" in tags:
                        params = "tags=order:score+{}".format(tags_params)
                    else:
                        params = "tags=-intersex+-female+male+order:score+{}".format(tags_params)
                else:
                    page = random.randint(1, 5)
                    params = "tags=-intersex+-female+male+order:rank&limit=20&page={}".format(page)
                api_url = "https://e621.net/posts.json?{}".format(params)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36 Edg/80.0.361.66'
                }
                # print(api_url+"===============================================")
                r = requests.get(api_url, headers=headers, timeout=(5, 60))
                img_json = json.loads(r.text).get("posts", [])

                tmp_list = []
                for item in img_json:
                    ext = item["file"]["ext"]
                    if ext == "png" or ext == "jpg" or ext == "gif":
                        tmp_list.append(item)
                img_json = tmp_list

                if len(img_json) == 0:
                    msg = "未能找到所需图片"
                else:
                    idx = random.randint(0, len(img_json) - 1)
                    img = img_json[idx]
                    flag = False
                    if receive["message_type"] == "group":
                        group_id = receive["group_id"]
                        group = QQGroup.objects.get(group_id=group_id)
                        group_commands = json.loads(group.commands)
                        if group_commands.get("r18", "disable") == "disable":
                            flag = is_nsfw(img)
                    destruct = 1 if flag else 0
                    msg = "[CQ:image,file={},destruct={}]".format(img["file"]["url"], destruct)

        reply_action = reply_message_action(receive, msg)
        action_list.append(reply_action)
    except Exception as e:
        msg = "Error: {}".format(type(e))
        action_list.append(reply_message_action(receive, msg))
        logging.error(e)
        traceback.print_exc()
    return action_list
