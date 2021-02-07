from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from redis import Redis

@csrf_exempt
def mirai(req: HttpRequest):
    stable = req.GET.get("stable", 1)
    r = Redis(host="localhost", port=6379, decode_responses=True)
    if stable == 1:
        return HttpResponse(r.get("MIRAISTABLEVERSION"))
    else:
        return HttpResponse(r.get("MIRAIDEVVERSION"))
