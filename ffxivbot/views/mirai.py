from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from redis import Redis

@csrf_exempt
def mirai(req: HttpRequest, str_type: str):
    lower = str_type.lower()
    r = Redis(host="localhost", port=6379, decode_responses=True)
    if lower == "stable":
        return HttpResponse(r.get("MIRAISTABLEVERSION"))
    else:
        return HttpResponse(r.get("MIRAIDEVVERSION"))
