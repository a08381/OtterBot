#!/usr/bin/env python3
import json
import logging
import sys
import os
import time

import django
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'FFXIV.settings'
from FFXIV import settings
django.setup()
from ffxivbot.models import QQBot

channel_layer = get_channel_layer()


def crawl():
    action_list = [
        {"action": "get_group_list", "params": {}, "echo": "get_group_list"},
        {
            "action": "get_friend_list",
            "params": {"flat": True},
            "echo": "get_friend_list",
        },
        {
            "action": "get_version_info",
            "params": {},
            "echo": "get_version_info",
        }
    ]
    bots = QQBot.objects.filter(event_time__gt=time.time()-300)
    for bot in bots:
        for action in action_list:
            call_api(
                bot,
                action=action["action"],
                params=action["params"],
                echo=action["echo"],
                post_type="websocket" if not bot.api_post_url else "http"
            )


def handle_message(bot, message):
    new_message = message
    if isinstance(message, list):
        new_message = []
        for idx, msg in enumerate(message):
            if msg["type"] == "share" and bot.share_banned:
                share_data = msg["data"]
                new_message.append(
                    {
                        "type": "image",
                        "data": {
                            "file": share_data["image"],
                            "url": share_data["image"],
                        },
                    }
                )
                new_message.append(
                    {
                        "type": "text",
                        "data": {
                            "text": "{}\n{}\n{}".format(
                                share_data["title"],
                                share_data["content"],
                                share_data["url"],
                            )
                        },
                    }
                )
            else:
                new_message.append(msg)
    return new_message


def call_api(bot, action, params, echo=None, **kwargs):
    if "async" not in action and not echo:
        action = action + "_async"
    if "send_" in action and "_msg" in action:
        params["message"] = handle_message(bot, params["message"])
    jdata = {"action": action, "params": params}
    if echo:
        jdata["echo"] = echo
    post_type = kwargs.get("post_type", "websocket")
    if post_type=="websocket":
        async_to_sync(channel_layer.send)(
            bot.api_channel_name, {"type": "send.event", "text": json.dumps(jdata)}
        )
    elif post_type=="http":
        url = os.path.join(bot.api_post_url, "{}?access_token={}".format(action, bot.access_token))
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url=url, headers=headers, data=json.dumps(params), timeout=5)
        if r.status_code!=200:
            print("HTTP Callback failed:")
            print(r.text)


if __name__ == "__main__":
    while True:
        try:
            crawl()
        except BaseException:
            logging.error("Error")
        time.sleep(600)
