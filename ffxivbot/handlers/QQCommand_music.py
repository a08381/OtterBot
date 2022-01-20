from .QQEventHandler import QQEventHandler
from .QQUtils import *
from ffxivbot.models import *
import logging
import json
import random
import requests
from bs4 import BeautifulSoup
import urllib
import logging
import time
import traceback


def search_word(word):
    urlword = urllib.parse.quote(word)
    url = "https://hibi.shadniw.ml/api/netease/search?s={}".format(urlword)
    r = requests.get(url=url, timeout=3)
    jres = json.loads(r.text)
    status_code = jres["code"]
    if int(status_code) == 200 and int(jres["result"]["songCount"]) > 0:
        songs = jres["result"]["songs"]
        song = songs[0]
        song_name = song["name"]
        song_id = song["id"]
        song_artists = "/".join([ar["name"] for ar in song["ar"]])
        msg = [
            {
                "type": "music",
                "data": {
                    "type": "custom",
                    "url": "https://music.163.com/#/song?id={}".format(song_id),
                    "audio": "https://botapi.dead-war.cn/music/url?id={}".format(song_id),
                    "image": "https://botapi.dead-war.cn/music/album?id={}".format(song_id),
                    "title": song_name,
                    "content": song_artists
                },
            }
        ]
    else:
        msg = '未能找到"{}"对应歌曲'.format(word)
    return msg


def QQCommand_music(*args, **kwargs):
    try:
        global_config = kwargs["global_config"]
        action_list = []
        receive = kwargs["receive"]

        bot = kwargs["bot"]
        if time.time() < bot.api_time + bot.long_query_interval:
            msg = "技能冷却中"
        else:
            message_content = receive["message"].replace("/music", "", 1).strip()
            msg = "default msg"
            if message_content.find("help") == 0 or message_content == "":
                msg = (
                    "/music $name : 搜索关键词$name的歌曲\n"
                    "Powered by https://api.imjad.cn, https://github.com/mixmoe/HibiAPI "
                )
            else:
                word = message_content
                msg = search_word(word)

        if type(msg) == str:
            msg = msg.strip()
        reply_action = reply_message_action(receive, msg)
        action_list.append(reply_action)
        return action_list
    except Exception as e:
        logging.error(e)
        traceback.print_exc()
