from django.contrib import admin
from .models import *

# Register your models here.


class QQGroupAdmin(admin.ModelAdmin):
    list_display = ("group_id", "welcome_msg", "last_reply_time")
    search_fields = ["group_id"]


class CustomReplyAdmin(admin.ModelAdmin):
    list_display = ("group", "key", "value")
    list_filter = ["group__group_id"]
    search_fields = ["group__group_id", "key", "value"]


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        "group",
        "message",
        "timestamp",
        "message_hash",
        "times",
        "repeated",
    )
    list_filter = ["group__group_id"]
    search_fields = ["group__group_id", "message"]


class BanMemberAdmin(admin.ModelAdmin):
    list_display = ("user_id", "group", "vote_list")
    list_filter = ["group__group_id"]
    search_fields = ["group__group_id", "user_id"]


class RevengeAdmin(admin.ModelAdmin):
    list_display = ("user_id", "group", "vote_list")
    list_filter = ["group__group_id"]
    search_fields = ["group__group_id", "user_id"]


class VoteAdmin(admin.ModelAdmin):
    list_display = ("name", "starttime", "endtime", "group")
    list_filter = ["group"]
    search_fields = ["name"]


class QQBotAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user_id",
        "access_token",
        "auto_accept_friend",
        "auto_accept_invite",
        "owner_id",
    )
    search_fields = ["name", "user_id", "owner_id"]


class CommentAdmin(admin.ModelAdmin):
    list_display = ("left_by", "content", "left_time")


class SorryGIFAdmin(admin.ModelAdmin):
    list_display = ("name", "api_name")


class QQUserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "bot_token")
    search_fields = ["user_id"]


class HsoAlterNameAdmin(admin.ModelAdmin):
    list_display = ("name", "key")


class ImageAdmin(admin.ModelAdmin):
    list_display = ["name", "key"]
    search_fields = ["name", "key"]
    raw_id_fields = ["add_by"]


class LotteryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "group"]
    search_fields = ["name", "group"]


class IFTTTChannelAdmin(admin.ModelAdmin):
    list_display = ["name", "group"]
    search_fields = ["name ", "group"]
    raw_id_fields = ["members"]




class LuckDataAdmin(admin.ModelAdmin):
    list_display = ["number"]


admin.site.register(QQGroup, QQGroupAdmin)
admin.site.register(CustomReply, CustomReplyAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(BanMember, BanMemberAdmin)
admin.site.register(Revenge, RevengeAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(QQBot, QQBotAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(SorryGIF, SorryGIFAdmin)
admin.site.register(QQUser, QQUserAdmin)
admin.site.register(HsoAlterName, HsoAlterNameAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Lottery, LotteryAdmin)
admin.site.register(IFTTTChannel, IFTTTChannelAdmin)
admin.site.register(LuckData, LuckDataAdmin)
