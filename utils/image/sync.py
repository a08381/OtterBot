#!/usr/bin/env python3
import sys
import os

import django

sys.path.append((os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'FFXIV.settings'
from FFXIV import settings

django.setup()
from ffxivbot.models import *
import re
import json
import time
import requests
import string
import random
import codecs
import urllib
import base64
import logging
import csv
import argparse
import traceback
from queue import Queue
from threading import Thread
from tqdm import tqdm


class Crawler(Thread):

    def __init__(self, url_queue: Queue, q: Queue, pbar: tqdm):
        super().__init__()
        self.url_queue = url_queue
        self.q = q
        self.pbar = pbar

    def run(self):
        while not self.url_queue.empty():
            t = self.url_queue.get()
            url = t[0]
            name = t[1]
            self.crawl(url, name)

    def crawl(self, url: str, name: str):
        try:
            req = requests.head(url, timeout=(5, 60))
            if req.status_code == 404:
                self.q.put(name)
            self.pbar.update()
            time.sleep(1)
        except Exception as e:
            print("except %s" % type(e))
            self.crawl(url, name)


def get_config():
    parser = argparse.ArgumentParser(description='Image Auto-Sync Script')

    parser.add_argument('-l', '--load', action='store_true',
                        help='Load images from the resource file')
    parser.add_argument('-s', '--save', action='store_true',
                        help='Save images to the resource file')
    parser.add_argument('-f', '--file', default="images.txt",
                        help='The resource file')
    parser.add_argument('-c', '--clean', action='store_true',
                        help='Clean images that are unusable')
    parser.add_argument('-t', '--thread', type=int, default=8,
                        help='The count of thread that clean method use')
    # Parse args.
    args = parser.parse_args()
    # Namespace => Dictionary.
    kwargs = vars(args)
    return kwargs


def load_images(**kwargs):
    file = kwargs.get("file", "images.txt")
    ok_cnt = 0
    with codecs.open(file, "r", "utf8") as f:
        lines = f.readlines()
        for line in tqdm(lines):
            j = json.loads(line)
            user_id = int(j["uploader"])
            (user, created) = QQUser.objects.get_or_create(user_id=user_id)
            try:
                img = Image(
                    domain=j["domain"],
                    key=j["key"],
                    name=j["name"],
                    path=j["path"],
                    img_hash="from_super",
                    timestamp=int(time.time()),
                    add_by=user,
                )
                img.save()
                ok_cnt += 1
            except Exception as e:
                pass
        print("Loaded {} images, {} failed.".format(ok_cnt, len(lines) - ok_cnt))


def save_images(**kwargs):
    keywords = ["色", "hso", "猫", "cat", "獭", "笑话", "骑", "DK", "武", "枪刃", "战士",
                "占星", "白魔", "学者", "赤魔", "召唤", "黑魔", "青魔", "诗人", "吟游", "舞者", "机工",
                "忍者", "武士", "武僧", "龙骑", "抛竿"]
    ok_cnt = 0
    file = kwargs.get("file", "images.txt")
    with codecs.open(file, "w", "utf8") as f:
        for img in Image.objects.all():
            if any([x in img.key for x in keywords]):
                d = {
                    "domain": img.domain,
                    "key": img.key,
                    "name": img.name,
                    "path": img.path,
                    "uploader": img.add_by.user_id,
                }
                line = json.dumps(d)
                f.write(line)
                f.write("\n")
                ok_cnt += 1
    print("Dumped {} images to {}".format(ok_cnt, file))


def clean_images(**kwargs):
    th = kwargs.get("thread", 8)
    images = Image.objects.all()
    ok_cnt = 0
    url_queue = Queue()
    q = Queue()
    thread_list = []
    pbar = tqdm(total=len(images))
    for image in images:
        if image.url != "":
            url = image.url
        else:
            url = os.path.join(image.domain, image.url)
        url_queue.put((url, image.name))

    for i in range(th):
        p = Crawler(url_queue, q, pbar)
        p.setDaemon(True)
        p.start()
        thread_list.append(p)

    alive = True
    while alive:
        for t in thread_list:
            if not t.is_alive():
                alive = False
                break

        while not q.empty():
            name = q.get()
            image = Image.objects.get(name=name)
            image.delete()
            print("delete {}".format(name))
            ok_cnt += 1

        time.sleep(1)
    print("Cleaned {} images from database".format(ok_cnt))


if __name__ == "__main__":
    config = get_config()
    if config.get("load", False):
        load_images(**config)
    elif config.get("save", False):
        save_images(**config)
    elif config.get("clean", False):
        clean_images(**config)
    else:
        print("Add '--help' in arguments for more information.")
