#!/usr/bin/env python3
import sys
import os
from pathlib import Path
import django
from redis import Redis

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ["DJANGO_SETTINGS_MODULE"] = "FFXIV.settings"
from FFXIV import settings

django.setup()

from ffxivbot.handlers.QQUtils import *
from ffxivbot.models import *
from ffxivbot.handlers.RsshubUtil import RsshubUtil

import asyncio
from channels.layers import get_channel_layer

import logging
from logging.handlers import TimedRotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers={TimedRotatingFileHandler(BASE_DIR / "log/crawl.log", when="D", backupCount=5)},
)
rss = RsshubUtil()
loop = asyncio.get_event_loop()


async def send_message(bot: QQBot, jdata: dict):
    if not bot.api_post_url:
        channel_layer = get_channel_layer()
        await channel_layer.send(
            bot.api_channel_name,
            {
                "type": "send.event",
                "text": json.dumps(jdata),
            },
        )
    else:
        url = os.path.join(
            bot.api_post_url,
            "{}?access_token={}".format(jdata["action"], bot.access_token),
        )
        headers = {"Content-Type": "application/json"}
        r = requests.post(
            url=url, headers=headers, data=json.dumps(jdata["params"]), timeout=10
        )
        if r.status_code != 200:
            logging.error(r.text)


def crawl_json(liveuser: LiveUser):
    platform = liveuser.platform
    rsshub = RsshubUtil()
    if platform == "bilibili":
        try:
            feed = rsshub.live(liveuser.platform, room_id=liveuser.room_id)
            if feed.entries:
                entry = feed.entries[0]
                title = re.sub(r"\d+-\d+-\d+ \d+:\d+:\d+", "", entry.title).strip()
                face_url = ""
                name = feed.feed.title.replace(" 直播间开播状态", "")
                jinfo = {"title": title, "status": "live"}
                if face_url:
                    jinfo.update({"image": face_url})
                if name:
                    jinfo.update({"name": name})
            else:
                jinfo = {
                    "status": "offline",
                }
            return jinfo
        except Exception as e:
            logging.error("Error at parsing bilibili API")
            print("Error at parsing bilibili API:{}".format(type(e)))
            traceback.print_exc()
    elif platform == "douyu":
        try:
            feed = rsshub.live(liveuser.platform, room_id=liveuser.room_id)
            if feed.entries:
                entry = feed.entries[0]
                title = re.sub(r"\d+-\d+-\d+ \d+:\d+:\d+", "", entry.title).strip()
                face_url = ""
                name = feed.feed.title.replace("的斗鱼直播间", "")
                jinfo = {"title": title, "status": "live"}
                if face_url:
                    jinfo.update({"image": face_url})
                if name:
                    jinfo.update({"name": name})
            else:
                jinfo = {
                    "status": "offline",
                }
            return jinfo
        except Exception as e:
            logging.error("Error at parsing douyu API")
            print("Error at parsing douyu API:{}".format(type(e)))
            traceback.print_exc()
    return None


async def crawl_live(liveuser: LiveUser, push=False):
    if not liveuser.subscribed_by.exists():
        for group in liveuser.subscribed_by.all():
            group.pushed_live.remove(liveuser)
        logging.info("Skipping {} cuz no subscription".format(liveuser))
        return
    jinfo = crawl_json(liveuser)
    print("{} jinfo:{}".format(liveuser, json.dumps(jinfo)))
    if not jinfo:
        logging.error("Crawling {} failed, please debug the response.".format(liveuser))
        logging.error("jinfo:{}".format(jinfo))
        return
    live_status = jinfo.get("status")
    liveuser.name = jinfo.get("name", liveuser.name)
    liveuser_info = json.loads(liveuser.info)
    liveuser_info.update(jinfo)
    liveuser.info = json.dumps(liveuser_info)
    liveuser.last_update_time = int(time.time())
    if live_status != "live":
        for group in liveuser.subscribed_by.all():
            group.pushed_live.remove(liveuser)
    pushed_group = set()
    if push and live_status == "live":
        for bot in QQBot.objects.all():
            group_id_list = (
                [int(item["group_id"]) for item in json.loads(bot.group_list)]
                if json.loads(bot.group_list)
                else []
            )
            for group in liveuser.subscribed_by.all():
                try:
                    if int(group.group_id) not in group_id_list:
                        continue
                    if group.pushed_live.filter(
                        name=liveuser.name,
                        room_id=liveuser.room_id,
                        platform=liveuser.platform,
                    ).exists():
                        continue
                    msg = liveuser.get_share(mode="text")
                    if bot.share_banned:
                        jmsg = liveuser.get_share()
                        msg = "{}\n{}\n{}".format(
                            jmsg.get("title"), jmsg.get("content"), jmsg.get("url")
                        )
                    jdata = {
                        "action": "send_group_msg",
                        "params": {"group_id": int(group.group_id), "message": msg},
                        "echo": "",
                    }
                    await send_message(bot, jdata)
                    group.pushed_live.add(liveuser)
                    pushed_group.add(group.group_id)
                except Exception as e:
                    logging.error(
                        "Error at pushing crawled live to {}: {}".format(group, e)
                    )
    liveuser.status = live_status
    liveuser.save()
    logging.info("crawled {}".format(liveuser))


async def crawl_wb(weibouser: WeiboUser, push=False):
    uid = weibouser.uid
    feed = rss.weibo("user", uid=uid)
    if feed and feed["items"]:
        for item in feed["items"]:
            if str(weibouser.name) != item["author"]:
                weibouser.name = item["author"]
                weibouser.save()
            bs = BeautifulSoup(item["summary"], "lxml")
            h = img_tag_to_cq(bs)

            t = WeiboTile(itemid=item["id"])
            t.owner = weibouser
            t.content = h.text
            t.crawled_time = int(time.mktime(item["published_parsed"]))

            channel_layer = get_channel_layer()

            groups = weibouser.subscribed_by.all()
            # print("ready to push groups:{}".format(list(groups)))
            bots = QQBot.objects.all()
            t.save()
            for group in groups:
                for bot in bots:
                    group_id_list = (
                        [item["group_id"] for item in json.loads(bot.group_list)]
                        if json.loads(bot.group_list)
                        else []
                    )
                    if int(group.group_id) not in group_id_list:
                        continue
                    try:
                        msg = get_weibotile_share(
                            t, feed["feed"]["image"]["href"], mode="text"
                        )
                        if bot.share_banned:
                            msg = "{}\n{}\n{}".format(t.owner, h.text, t.itemid)
                        logging.info("Pushing {} to group: {}".format(t, group))
                        # print("msg: {}".format(msg))
                        if push:
                            t.pushed_group.add(group)
                            jdata = {
                                "action": "send_group_msg",
                                "params": {
                                    "group_id": int(group.group_id),
                                    "message": msg,
                                },
                                "echo": "",
                            }
                            await send_message(bot, jdata)
                    except requests.ConnectionError as e:
                        logging.error(
                            "Pushing {} to group: {} ConnectionError".format(t, group)
                        )
                    except requests.ReadTimeout as e:
                        logging.error(
                            "Pushing {} to group: {} timeout".format(t, group)
                        )
                    except Exception as e:
                        traceback.print_exc()
                        logging.error(
                            "Error at pushing crawled weibo to {}: {}".format(group, e)
                        )

            logging.info("crawled {} of {}".format(t.itemid, t.owner))
    return


async def crawl_mirai():
    rss_g = RsshubUtil("https://github.com/")
    feed = rss_g.raw_parse("/mamoe/mirai/releases.atom")
    found_stable = False
    found_dev = False
    differ = False
    r = Redis(host="localhost", port=6379, decode_responses=True)
    stable_ver = r.get("MIRAI_STABLE_VERSION")
    dev_ver = r.get("MIRAI_DEV_VERSION")
    if feed and feed["items"]:
        items = feed["items"]
        while len(items) > 0:
            item = items.pop(0)
            title = item["title"]
            if title.find("dev") != -1 and title.find("publish") == -1 and not found_dev:
                found_dev = True
                if dev_ver != title:
                    differ = True
                dev_ver = title
                r.set("MIRAIDEVVERSION", dev_ver, ex=7200)
            if title.find("dev") == -1 and not found_stable:
                found_stable = True
                if stable_ver != title:
                    differ = True
                stable_ver = title
                r.set("MIRAISTABLEVERSION", stable_ver, ex=7200)
            if differ:
                requests.get("https://ci.yumc.pw/buildWithParameters?token=mirai_build_with_no_bcprov")
            if found_stable and found_dev:
                break
                


async def e_crawl_live():
    lus = LiveUser.objects.all()
    for lu in lus:
        logging.info("Begin crawling {}".format(lu))
        try:
            await crawl_live(lu, True)
        except Exception as e:
            logging.error(e)
            print("Error:{}".format(e))
        await asyncio.sleep(1)
        logging.info("Crawl {} finish".format(lu))


async def e_crawl_wb():
    wbus = WeiboUser.objects.all()
    for wbu in wbus:
        logging.info("Begin crawling {}".format(wbu.name))
        try:
            await crawl_wb(wbu, True)
        except requests.ReadTimeout as e:
            logging.error("crawling {} timeout".format(wbu.name))
        except Exception as e:
            traceback.print_exc()
            logging.error(e)
        await asyncio.sleep(1)
        logging.info("Crawl {} finish".format(wbu.name))


async def r_crawl_live():
    while True:
        loop.create_task(e_crawl_live())
        await asyncio.sleep(300)


async def r_crawl_wb():
    while True:
        loop.create_task(e_crawl_wb())
        await asyncio.sleep(300)


async def r_crawl_mirai():
    while True:
        loop.create_task(crawl_mirai())
        await asyncio.sleep(3600)


if __name__ == "__main__":
    r1 = loop.create_task(r_crawl_live())
    r2 = loop.create_task(r_crawl_wb())
    r3 = loop.create_task(r_crawl_mirai())
    loop.run_forever()
