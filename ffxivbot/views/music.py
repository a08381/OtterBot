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
NETEASE_API_URL = "https://hibi.shadniw.ml/api/netease"


@csrf_exempt
def music(req: HttpRequest, str_type: str):
    lower = str_type.lower()
    if lower == "url":
        ids = req.GET.get("id", 0)
        response = requests.get(
            "{}/song?id={}".format(NETEASE_API_URL, ids), timeout=(5, 10)
        )
        try:
            if response.status_code == 200:
                music_dict = response.json()
                if music_dict["code"] == 200:
                    music_url = music_dict["data"][0]
                    return HttpResponseRedirect(music_url["url"])
        except KeyError:
            return HttpResponse("KeyError", status=500)
    elif lower == "search":
        keywords = req.GET.get("keywords", "")
        response = requests.get(
            "{}/search?keywords={}".format(NETEASE_API_URL, keywords), timeout=(5, 10)
        )
        try:
            if response.status_code == 200:
                music_dict = response.json()
                if music_dict["code"] == 200:
                    music_url = music_dict["data"][0]
                    return JsonResponse(music_url)
        except KeyError:
            return HttpResponse("KeyError", status=500)
    elif lower == "album":
        ids = req.GET.get("id", "")
        response = requests.get(
            "{}/detail?id={}".format(NETEASE_API_URL, ids), timeout=(5, 10)
        )
        try:
            if response.status_code == 200:
                music_dict = response.json()
                if music_dict["code"] == 200:
                    music_album = music_dict["result"]["songs"][0]
                    return HttpResponseRedirect(music_album["al"]["picUrl"])
        except KeyError:
            return HttpResponse("KeyError", status=500)

    return HttpResponse(status=500)
