from .QQEventHandler import QQEventHandler
import re


class QQCommand(object):
    def __init__(self, *args, **kwargs):
        self.global_config = kwargs.get("global_config")
        self.bot = kwargs.get("bot")

    def __call__(self, *args, **kwargs):
        self.receive = kwargs.get("receive")
        self.action_handler = QQEventHandler(self.receive)
        self.raw_message = self.receive.get("message")
        self.message = self.raw_message
        # Extract image url (only one) in message
        image_pattern = r"\[CQ:image,file=(.*?)\]"
        match = re.findall(image_pattern, self.raw_message)
        self.image_url = match[0] if match else None
        self.message = re.sub(image_pattern, "", self.message)
        # Split messages into segments
        self.split_message = self.message.split(" ")
        while " " in self.split_message:  # Remove additional spaces
            self.split_message.remove(" ")
        # Extract (multiple) at in message
        at_pattern = r"\[CQ:at,qq=(\d+?)\]"
        self.at = re.findall(at_pattern, self.raw_message)
        self.message = re.sub(at_pattern, "", self.message)
        # Need to be implemented
        pass


class QQGroupCommand(QQCommand):
    def __init__(self, *args, **kwargs):
        super(QQGroupCommand, self).__init__(*args, **kwargs)
        self.group = kwargs.get("group")
        self.user_info = kwargs.get("user_info")
        self.member_list = kwargs.get("member_list")

    def __call__(self, *args, **kwargs):
        super(QQGroupCommand, self).__call__(*args, **kwargs)
        # Need to be implemented
        pass
