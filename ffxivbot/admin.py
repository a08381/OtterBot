from django.contrib import admin
from .models import *

# Register your models here.


class QuestAdmin(admin.ModelAdmin):
    list_display = ("quest_id", "name", "cn_name")
    search_fields = ["name", "cn_name"]


class BossAdmin(admin.ModelAdmin):
    list_display = ("boss_id", "name", "cn_name")
    search_fields = ["name", "cn_name"]


class JobAdmin(admin.ModelAdmin):
    list_display = ("name", "cn_name")
    search_fields = ["name", "cn_name"]


class PlotQuestAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "quest_type", "endpoint", "endpoint_desc"]
    search_fields = ["id", "name"]
    list_filter = ["quest_type"]


class ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "areaId", "groupId", "alter_names")


class WeatherAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


class WeatherRateAdmin(admin.ModelAdmin):
    list_display = ["id"]


class TerritoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "mapid"]
    search_fields = ["name"]


class HuntGroupAdmin(admin.ModelAdmin):
    list_display = ["group", "server"]
    search_fields = ["group", "server"]
    raw_id_fields = ["group", "moderator"]


class MonsterAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "cn_name",
        "territory",
        "rank",
        "spawn_cd_hour",
        "pop_cd_hour",
    ]
    search_fields = ["name ", "cn_name"]
    list_filter = ["rank"]


class HuntLogAdmin(admin.ModelAdmin):
    list_display = ["monster", "hunt_group", "server", "log_type", "time"]
    search_fields = ["monster ", "hunt_group", "log_type"]
    list_filter = ["monster", "hunt_group", "server", "log_type"]
    raw_id_fields = ["hunt_group"]


class TreasureMapAdmin(admin.ModelAdmin):
    list_display = ["territory", "number"]
    search_fields = ["territory"]
    list_filter = ["territory", "rank"]


admin.site.register(Quest, QuestAdmin)
admin.site.register(Boss, BossAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(PlotQuest, PlotQuestAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Weather, WeatherAdmin)
admin.site.register(WeatherRate, WeatherRateAdmin)
admin.site.register(Territory, TerritoryAdmin)
admin.site.register(HuntGroup, HuntGroupAdmin)
admin.site.register(Monster, MonsterAdmin)
admin.site.register(HuntLog, HuntLogAdmin)
admin.site.register(TreasureMap, TreasureMapAdmin)
