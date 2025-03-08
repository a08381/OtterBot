import functools
import importlib
import inspect
import pkgutil
import re
from enum import IntFlag, auto

from ffxivbot import commands


class CMD:

    def __init__(self):
        self.__sub_commands__ = list(filter(
            lambda m: not m.startswith("__") and not m.endswith("__") and m != "index" and callable(
                getattr(self, m)), dir(self)))
        self.description = "默认指令."
        self.sub_description = {
            "help": "[子命令] 显示指令帮助",
        }
        self.is_group_command = False
        self.use_cq_pro = False
        self.use_global_cooldown = True
        self.cooldown = 15
        self.default = True

    def index(self, *args, **kwargs):
        print(self.description, *args, kwargs)

    def help(self, *args, **kwargs):
        if len(args) != 0 and str(args[0]).lower() in self.__sub_commands__:
            sub_name = str(args[0]).lower()
            sub_description = self.sub_description[sub_name]
            msg = "/{}： {}\n指令帮助：\n\n".format(
                type(self).__name__.lower(),
                self.description)

            msg += "\t{} {}".format(sub_name, sub_description)
        else:
            msg = "/{}： {}\n指令帮助：\n\n".format(
                type(self).__name__.lower(),
                self.description)
            for k, v in self.sub_description.items():
                msg += "\t{} {}".format(k, v)
        print(msg)


class Perm(IntFlag):
    MEMBER = auto()
    ADMIN = auto()
    OWNER = auto()
    BOT_OWNER = auto()


def get_class():
    clazz = dict()
    for loader, path, ispkg in pkgutil.iter_modules(commands.__path__, commands.__name__ + "."):
        if ispkg:
            continue
        module = importlib.import_module(path)
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name == "CMD":
                continue
            clazz[name.lower()] = obj()
    return clazz


cmds = get_class()
pa = re.compile(r"^[\\/](.*?)(?:\s+(.*)\s*)$")
sp = re.compile(r"\s+")
ksp = re.compile(r"^([^=]+)=(.+)$")


def format_command(cmdline: str):
    args = list()
    kwargs = dict()
    ma1 = pa.match(cmdline)
    method = None

    if not ma1:
        return method, args, kwargs

    name = ma1.group(1)
    sub_command = ma1.group(2)
    cmd = cmds.get(name, None)

    if not cmd:
        return method, args, kwargs

    if not sub_command:
        method = cmd.__getattribute__("index")
        return method, args, kwargs

    sub_commands = sp.split(sub_command)

    for sub in sub_commands:
        ma2 = ksp.match(sub)
        if not ma2:
            continue
        kwargs[ma2.group(1)] = ma2.group(2)
        sub_commands.remove(sub)

    name = sub_commands[0].lower()
    if name in cmd.__sub_commands__:
        sub_commands = sub_commands[1:]
    else:
        name = "index"

    method = cmd.__getattribute__(name)
    args.append(sub_commands)

    return method, args, kwargs


def invoke(cmd, *args, **kwargs):
    if not cmd:
        print("Unknown Command, try /help.")
    else:
        cmd(*args, **kwargs)


def check_permission(role: Perm = Perm.NONE):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if role == Perm.NONE:
                func(*args, **kwargs)
            user_info = kwargs["user_info"]
            receive = kwargs["receive"]
            user_id = receive["user_id"]

        return wrapper
    return decorator
