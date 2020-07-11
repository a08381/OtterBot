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
import uuid
import argparse
import traceback


def get_config():
    parser = argparse.ArgumentParser(description="Active Code Generator")

    parser.add_argument('-g', '--generate', action="store_true",
                        help="generate active code into database.")
    parser.add_argument('-c', '--clean', action="store_true",
                        help="remove used active code in database.")
    parser.add_argument('-p', '--parse', action="store_true",
                        help="parse active code into text file.")
    parser.add_argument('-n', '--num', type=int, default=0,
                        help="the number of active code will process.")
    parser.add_argument('-f', '--file', type=str, default="code.txt",
                        help="the file of active code will parse.")
    # Parse args.
    args = parser.parse_args()
    # Namespace => Dictionary.
    kwargs = vars(args)
    return kwargs


def generate(**kwargs):
    num = kwargs.get("num", 0)
    is_parse = kwargs.get("parse", False)
    file = kwargs.get("file", "code.txt")
    if is_parse:
        with codecs.open(file, "w", "utf8") as f:
            if num == 0:
                num = 100
            for i in range(num):
                code = str(uuid.uuid4())
                active_code = ActiveCode(code=code, is_used=False)
                active_code.save()
                f.write(code)
                f.write("\n")
    else:
        if num == 0:
            num = 100
        for i in range(num):
            code = uuid.uuid4()
            active_code = ActiveCode(code=code, is_used=False)
            active_code.save()


def parse(**kwargs):
    num = kwargs.get("num", 0)
    file = kwargs.get("file", "code.txt")
    with codecs.open(file, "w", "utf8") as f:
        codes = ActiveCode.objects.filter(is_used=False)
        if num != 0 and len(codes) > num:
            codes = codes[:num]
        for code in codes:
            f.write(code.code)
            f.write("\n")


def clean_used(**kwargs):
    num = kwargs.get("num", 0)
    if num == 0:
        ActiveCode.objects.filter(is_used=True).delete()
    else:
        codes = ActiveCode.objects.filter(is_used=True)
        if len(codes) > num:
            codes = codes[:num]
            codes.delete()


if __name__ == "__main__":
    config = get_config()
    if config.get("generate", False):
        generate(**config)
    elif config.get("parse", False):
        clean_used(**config)
    elif config.get("clean", False):
        clean_used(**config)
    else:
        print("Add '--help' in arguments for more information.")
