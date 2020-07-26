from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from pytz import timezone
import json
import time

# Create your models here.
class QQGroup(models.Model):
    group_id = models.CharField(primary_key=True, max_length=64, unique=True)
    welcome_msg = models.TextField(default="", blank=True)
    bots = models.TextField(default="[]")
    repeat_ban = models.IntegerField(default=-1)
    repeat_length = models.IntegerField(default=-1)
    repeat_prob = models.IntegerField(default=0)
    left_reply_cnt = models.IntegerField(default=100)
    ban_cnt = models.IntegerField(default=-1)
    ban_till = models.BigIntegerField(default=0)
    last_reply_time = models.BigIntegerField(default=0)
    member_list = models.TextField(default="[]")
    registered = models.BooleanField(default=False)
    commands = models.TextField(default="{}")
    api = models.BooleanField(default=False)

    def __str__(self):
        return self.group_id


class CustomReply(models.Model):
    group = models.ForeignKey(QQGroup, on_delete=models.CASCADE)
    key = models.CharField(default="", max_length=64, blank=True)
    value = models.TextField(default="", blank=True)

    class Meta:
        indexes = [models.Index(fields=["group", "key"])]


class ChatMessage(models.Model):
    group = models.ForeignKey(QQGroup, on_delete=models.CASCADE)
    message = models.TextField(default="", blank=True)
    message_hash = models.CharField(default="", max_length=32, blank=True)
    timestamp = models.BigIntegerField(default=0)
    times = models.IntegerField(default=1)
    repeated = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["group", "message_hash"])]


class BanMember(models.Model):
    user_id = models.CharField(max_length=64)
    group = models.ForeignKey(QQGroup, on_delete=models.CASCADE)
    ban_time = models.IntegerField(default=0)
    vote_list = models.TextField(default="{}")
    timestamp = models.BigIntegerField(default=0)


class Revenge(models.Model):
    user_id = models.CharField(max_length=64)
    group = models.ForeignKey(QQGroup, on_delete=models.CASCADE)
    vote_list = models.TextField(default="{}")
    timestamp = models.BigIntegerField(default=0)
    ban_time = models.IntegerField(default=0)


class Vote(models.Model):
    group = models.ForeignKey(QQGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    starttime = models.BigIntegerField(default=0)
    endtime = models.BigIntegerField(default=0)
    vote = models.TextField(default="{}")

    def __str__(self):
        return str(self.name)


class QQBot(models.Model):
    name = models.CharField(max_length=16)
    user_id = models.CharField(max_length=64, unique=True)
    wechat_id = models.CharField(max_length=64, default="", blank=True)
    owner_id = models.CharField(max_length=16)
    access_token = models.CharField(max_length=16, default="")
    auto_accept_friend = models.BooleanField(default=False)
    auto_accept_invite = models.BooleanField(default=False)
    tuling_token = models.CharField(max_length=32, default="", blank=True)
    saucenao_token = models.CharField(max_length=32, default="", blank=True)
    api_channel_name = models.CharField(max_length=32, default="", blank=True)
    event_channel_name = models.CharField(max_length=32, default="", blank=True)
    api_post_url = models.CharField(max_length=64, default="", blank=True)
    group_list = models.TextField(default="[]")
    plugin_status = models.TextField(default="{}")
    version_info = models.TextField(default="{}")
    event_time = models.BigIntegerField(default=0)
    api_time = models.BigIntegerField(default=0)
    long_query_interval = models.IntegerField(default=15)
    friend_list = models.TextField(default="{}")
    public = models.BooleanField(default=True)
    r18 = models.BooleanField(default=False)
    disconnections = models.TextField(default="[]")
    disconnect_time = models.BigIntegerField(default=0)
    commands = models.TextField(default="{}")
    share_banned = models.BooleanField(default=False)
    img_banned = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Comment(models.Model):
    left_by = models.CharField(max_length=16)
    left_group = models.CharField(max_length=16, default="")
    left_time = models.BigIntegerField(default=0)
    bot_id = models.CharField(max_length=16, default="")
    content = models.TextField(default="", blank=True)
    reply = models.TextField(default="", blank=True)

    def __str__(self):
        return self.content[:10]


class SorryGIF(models.Model):
    name = models.CharField(max_length=16)
    api_name = models.CharField(max_length=32)
    example = models.TextField(default="")

    def __str__(self):
        return self.name


class QQUser(models.Model):
    dbuser = models.OneToOneField(
        User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="qquser"
    )
    user_id = models.CharField(max_length=64, unique=True)
    bot_token = models.CharField(max_length=16, blank=True)
    able_to_upload_image = models.BooleanField(default=True)
    last_api_time = models.BigIntegerField(default=0)
    last_chat_time = models.BigIntegerField(default=0)
    api_interval = models.IntegerField(default=5)
    ban_till = models.BigIntegerField(default=0)
    ban_share_till = models.BigIntegerField(default=0)
    sent_weibo = models.TextField(default="[]")
    ifttt_token = models.CharField(default="", max_length=128, blank=True)
    nickname = models.CharField(default="", max_length=64, blank=True)
    avatar_url = models.CharField(default="", max_length=256, blank=True)
    open_id = models.CharField(default="", max_length=128, blank=True)
    vcode = models.CharField(default="", max_length=16, blank=True)
    vcode_time = models.BigIntegerField(default=0)
    timezone = models.CharField(default="Asia/Shanghai", max_length=32)

    def __str__(self):
        return str(self.user_id)


class HsoAlterName(models.Model):
    name = models.CharField(max_length=32, unique=True, default="")
    key = models.CharField(max_length=64, default="")

    def __str__(self):
        return self.name


class Image(models.Model):
    domain = models.CharField(max_length=128, default="https://i.loli.net")
    url = models.CharField(max_length=128, default="")
    key = models.CharField(max_length=16, default="")
    name = models.CharField(max_length=32, default="")
    path = models.CharField(max_length=64, default="", unique=True)
    img_hash = models.CharField(max_length=32, default="")
    timestamp = models.IntegerField(default=0)
    add_by = models.ForeignKey(
        QQUser, on_delete=models.CASCADE, related_name="upload_images"
    )

    def __str__(self):
        return self.name


class Lottery(models.Model):
    name = models.CharField(max_length=32, default="")
    description = models.TextField(default="", blank=True, null=True)
    group = models.ForeignKey(
        QQGroup, on_delete=models.CASCADE, related_name="lotteries"
    )
    host_user = models.CharField(max_length=16, default="")
    participate_user = models.TextField(default="[]")
    prize = models.TextField(default="[]")
    random_res = models.TextField(default="{}")
    begin_time = models.BigIntegerField(default=0)
    end_time = models.BigIntegerField(default=0)
    uuid = models.CharField(max_length=36, unique=True)  # uuid.uuid4()
    public = models.BooleanField(default=False)
    max_participate = models.IntegerField(default=-1)
    mode = models.IntegerField(default=1)  # 0: system random shuffle 1: random.org

    def __str__(self):
        return self.name

    def winner_info(self):
        res_json = json.loads(self.random_res)
        msg = ""
        try:
            random_list = res_json["result"]["random"]["data"]
        except KeyError:
            return "KeyError"
        else:
            member_score_list = []
            members = json.loads(self.participate_user)
            prizes = json.loads(self.prize)
            for member, score in zip(members, random_list):
                member_score_list.append((member, score))
            member_score_list.sort(key=lambda x: x[1], reverse=True)
            for member, prize in zip(member_score_list, prizes):
                msg += "[CQ:at,qq={}] --- {}\n".format(member[0], prize)
        return msg

    def prize_info(self):
        prizes = json.loads(self.prize)
        prize_dict = {}
        for p in prizes:
            if p not in prize_dict.keys():
                prize_dict[p] = 1
            else:
                prize_dict[p] += 1
        return ", ".join(
            ["{}*{}".format(item[0], item[1]) for item in prize_dict.items()]
        )

    def info(self, **kwargs):
        msg = "抽奖 #{}: {} 的信息如下：".format(self.id, self.name)
        TIMEFORMAT = kwargs.get("TIMEFORMAT", None)
        import time

        msg += "\n开始时间：{}".format(
            time.strftime(TIMEFORMAT, time.localtime(self.begin_time))
            if TIMEFORMAT
            else self.begin_time
        )
        if self.end_time > 0:
            msg += "\n结束时间：{}".format(
                time.strftime(TIMEFORMAT, time.localtime(self.end_time))
                if TIMEFORMAT
                else self.end_time
            )
        prizes = self.prize_info()
        msg += "\n奖品：{}".format(prizes)
        mems = " ".join(
            ["[CQ:at,qq={}]".format(qq) for qq in json.loads(self.participate_user)]
        )
        msg += "\n参与人：{}".format(mems)
        if time.time() > self.end_time and self.end_time > 0:
            msg += "\n获奖者：{}".format(self.winner_info())
        return msg


class CommandLog(models.Model):
    time = models.BigIntegerField(default=0)
    command = models.CharField(max_length=32)
    message = models.TextField(default="")
    bot_id = models.CharField(max_length=16)
    user_id = models.CharField(max_length=64)
    group_id = models.CharField(max_length=64)


class IFTTTChannel(models.Model):
    name = models.CharField(default="", max_length=32)
    group = models.ForeignKey(
        QQGroup,
        null=True,
        blank=True,
        related_name="ifttt_channel",
        on_delete=models.CASCADE,
    )
    members = models.ManyToManyField(QQUser, blank=True)
    last_push_time = models.BigIntegerField(default=0)
    callback_link = models.CharField(default="", max_length=256)

    def __str__(self):
        return self.name


class LuckData(models.Model):
    number = models.IntegerField(default=0)
    text = models.TextField(default="")
    img_url = models.CharField(max_length=128, default="")

    def __str__(self):
        return str(self.number)
