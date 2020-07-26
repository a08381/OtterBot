class QQEventHandler:
    def __init__(self, receive):
        self.receive = receive

    def reply_message(self, reply_msg):
        action = {"action": "", "params": {}, "echo": ""}
        if self.receive["message_type"] == "group":
            action.update(
                {
                    "action": "send_group_msg",
                    "params": {
                        "group_id": self.receive["group_id"],
                        "message": reply_msg,
                    },
                }
            )
        else:
            action.update(
                {
                    "action": "send_private_msg",
                    "params": {
                        "user_id": self.receive["user_id"],
                        "message": reply_msg,
                    },
                }
            )
        return action

    def group_ban(self, duration):
        group_id, user_id = self.receive["group_id"], self.receive["user_id"]
        action = {
            "action": "set_group_ban",
            "params": {"group_id": group_id, "user_id": user_id, "duration": duration},
            "echo": "",
        }
        return action

    def delete_message(self, message_id):
        action = {
            "action": "delete_msg",
            "params": {"message_id": message_id},
            "echo": "",
        }
        return action

    def __call__(self, **kwargs):
        pass
