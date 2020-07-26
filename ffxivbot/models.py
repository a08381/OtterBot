from django.db import models
from django.contrib.auth.models import User
from otterbot.models import QQGroup, QQUser
from datetime import datetime
from pytz import timezone
import json
import time

# Create your models here.
class Quest(models.Model):
    quest_id = models.IntegerField(primary_key=True)
    name = models.CharField(default="", max_length=64, blank=True)
    cn_name = models.CharField(default="", max_length=64, blank=True)

    def __str__(self):
        return str(self.name)


class Boss(models.Model):
    boss_id = models.IntegerField(primary_key=True)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    name = models.CharField(default="", max_length=64, blank=True)
    cn_name = models.CharField(default="", max_length=64, blank=True)
    nickname = models.TextField(default="{}")
    add_time = models.BigIntegerField(default=0)
    cn_add_time = models.BigIntegerField(default=0)
    cn_offset = models.IntegerField(default=0)
    parsed_days = models.IntegerField(default=0)
    frozen = models.BooleanField(default=False)
    patch = models.IntegerField(default=0)
    savage = models.IntegerField(default=100)  # 100 for normal; 101 for savage
    global_server = models.IntegerField(
        default=3
    )  # 3 for boss after 5.0, 1 for boss before 5.0
    cn_server = models.IntegerField(
        default=5
    )  # 5 for boss after 5.0, 3 for boss before 5.0

    def __str__(self):
        return str(self.name)


class Job(models.Model):
    name = models.CharField(default="", max_length=64, blank=True)
    cn_name = models.CharField(default="", max_length=64, blank=True)
    nickname = models.TextField(default="{}")

    def __str__(self):
        return str(self.name)


class PlotQuest(models.Model):
    name = models.CharField(max_length=128)
    tooltip_url = models.TextField(default="", blank=True)
    tooltip_html = models.TextField(default="", blank=True)
    pre_quests = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="suf_quests"
    )
    language_names = models.TextField(default="{}", blank=True)
    endpoint = models.BooleanField(default=False)
    endpoint_desc = models.CharField(max_length=64, default="", blank=True)
    quest_type = models.IntegerField(
        default=0
    )  # 0:nothing 3:main-scenario 8:special 1,10:other

    def __str__(self):
        return self.name

    def is_main_scenario(self):
        return self.quest_type == 3

    def is_special(self):
        return self.quest_type == 8


class Server(models.Model):
    name = models.CharField(max_length=16)
    areaId = models.IntegerField(default=1)
    groupId = models.IntegerField(default=25)
    alter_names = models.TextField(default="[]")
    worldId = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Weather(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=32, default="")

    def __str__(self):
        return self.name


class WeatherRate(models.Model):
    id = models.IntegerField(primary_key=True)
    rate = models.TextField(default="[]")


class Territory(models.Model):
    name = models.CharField(max_length=32, default="")
    nickname = models.TextField(default="[]")
    weather_rate = models.ForeignKey(
        WeatherRate, blank=True, null=True, on_delete=models.CASCADE
    )
    mapid = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class ContentFinderItem(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64, default="")
    nickname = models.TextField(default="{}")
    guide = models.TextField(default="")

    def __str__(self):
        return self.name


class HuntGroup(models.Model):
    name = models.CharField(default="", max_length=64)
    group = models.ForeignKey(
        QQGroup, on_delete=models.CASCADE, related_name="hunt_group"
    )
    server = models.ForeignKey(
        Server, on_delete=models.CASCADE, related_name="hunt_group"
    )
    moderator = models.ManyToManyField(
        QQUser, related_name="managed_hunt_group", blank=True
    )
    servermark = models.CharField(default="", max_length=16, blank=True, null=True)
    remark = models.CharField(default="", max_length=64, blank=True, null=True)
    public = models.BooleanField(default=False)

    def __str__(self):
        return self.name if self.name else "{}-{}".format(self.group, self.server)


class Monster(models.Model):
    name = models.CharField(default="", blank=True, max_length=32, unique=True)
    cn_name = models.CharField(default="", blank=True, max_length=32)
    territory = models.ForeignKey(
        Territory, on_delete=models.CASCADE, related_name="hunt_monster"
    )
    rank = models.CharField(default="A", max_length=5)  # enum: "A", "B", "S", "Fate"
    spawn_cooldown = models.IntegerField(default=0)
    first_spawn_cooldown = models.IntegerField(default=0)
    pop_cooldown = models.IntegerField(default=0)
    first_pop_cooldown = models.IntegerField(default=0)
    info = models.CharField(default="", max_length=128)
    status = models.TextField(default="{}")

    def spawn_cd_hour(self):
        return self.spawn_cooldown // 3600

    def pop_cd_hour(self):
        return self.pop_cooldown // 3600

    def __str__(self):
        return self.cn_name if self.cn_name else self.name


class HuntLog(models.Model):
    monster = models.ForeignKey(
        Monster,
        on_delete=models.CASCADE,
        related_name="hunt_log",
        blank=True,
        null=True,
    )
    hunt_group = models.ForeignKey(
        HuntGroup, on_delete=models.CASCADE, related_name="hunt_log"
    )
    server = models.ForeignKey(
        Server, on_delete=models.CASCADE, related_name="hunt_log"
    )
    log_type = models.CharField(default="", max_length=16)
    time = models.BigIntegerField(default=0)

    def __str__(self):
        return "{}-{}".format(self.server, self.monster)

    def get_info(self):
        return "HuntLog#{}: {}-{} {}".format(
            self.id, self.server, self.monster, self.log_type
        )


class TreasureMap(models.Model):
    territory = models.ForeignKey(
        Territory, blank=True, null=True, on_delete=models.CASCADE
    )
    position = models.TextField(default="[0, 0]")
    rank = models.CharField(max_length=8, default="")
    number = models.IntegerField(default=0)
    uri = models.TextField(default="")

    def __str__(self):
        return "{}#{}".format(self.territory, self.number)
