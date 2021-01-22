import json
import os

import requests
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from FFXIV import settings

FFXIVBOT_ROOT = os.environ.get("FFXIVBOT_ROOT", settings.BASE_DIR)
CONFIG_PATH = os.environ.get(
    "FFXIVBOT_CONFIG", os.path.join(FFXIVBOT_ROOT, "ffxivbot/config.json")
)
config = json.load(open(CONFIG_PATH, encoding="utf-8"))

NETEASE_API_URL = config.get("NETEASE_API_URL", "http://localhost:3000")
NETEASE_USERNAME = config.get("NETEASE_USERNAME", "")
NETEASE_PASSWORD = config.get("NETEASE_PASSWORD", "")

if NETEASE_USERNAME != "":
    session = requests.session()
    try:
        session.get(
            "{}/login?email={}&password={}".format(
                NETEASE_API_URL, NETEASE_USERNAME, NETEASE_PASSWORD
            ), timeout=5
        )
    except Exception:
        pass
else:
    session = requests


@csrf_exempt
def music(req: HttpRequest, str_type: str):
    lower = str_type.lower()
    if lower == "url":
        ids = req.GET.get("id", 0)
        response = session.get(
            "{}/song/url?id={}".format(NETEASE_API_URL, ids), timeout=(5, 10)
        )
        try:
            if response.status_code == 200:
                music_dict = response.json()
                music_url = music_dict["data"][0]
                if music_url["code"] == 200:
                    return HttpResponseRedirect(music_url["url"])
        except KeyError:
            return HttpResponse("KeyError", status=500)
    elif lower == "search":
        keywords = req.GET.get("keywords", "")
        response = session.get(
            "{}/search?keywords={}".format(NETEASE_API_URL, keywords), timeout=(5, 10)
        )
        try:
            if response.status_code == 200:
                music_dict = response.json()
                music_url = music_dict["data"][0]
                if music_url["code"] == 200:
                    return JsonResponse(music_url)
        except KeyError:
            return HttpResponse("KeyError", status=500)

    return HttpResponse(status=500)
