from collections.abc import Callable
from typing import cast

import mcdreforged as mcdr
from mcdreforged.api.decorator import new_thread

from .. import state
from ..types import Server
from ..utils import try_get_servers


@new_thread("GotoList")
def list_servers(src: mcdr.CommandSource, ctx: mcdr.CommandContext):
    """
    展示当前 BDTV hub 中记录的在线服务器列表
    """

    # 尝试获取在线服务器
    servers = try_get_servers(src.get_server())

    if servers is None:
        src.reply(mcdr.RText("获取在线服务器失败", color=mcdr.RColor.red))
        return

    t = [mcdr.RText(f"现在有{len(servers)}个服务器在线"), mcdr.RText("\n")]

    # 对服务器列表进行按 slug 排序
    servers_value = list(servers.values())
    sort_by_slug: Callable[[Server], str] = lambda s: s["slug"]
    servers_value.sort(key=sort_by_slug)
    # 遍历服务器构造消息列表
    for index, server in enumerate(servers_value):
        if index > 0:
            t.append(mcdr.RText("\n"))

        s = []
        if server["slug"] == state.server_data["slug"]:
            s.append(mcdr.RText("当前 ", color=mcdr.RColor.gray).h("你在这个服务器里"))
        else:
            s.append(
                mcdr.RText("前往 ", color=mcdr.RColor.yellow)
                .h("点击前往")
                .c(mcdr.RClickAction.suggest_command, f"!!goto {server['slug']}")
            )

        s.extend(
            [
                mcdr.RText(f"{server['nickname']}", color=mcdr.RColor.green).h(
                    f"{server['slug']}"
                ),
                mcdr.RText(" ", color=mcdr.RColor.green),
            ]
        )

        t.extend(s)

    src.reply(mcdr.RTextList(*t))


@new_thread("GotoSwitch")
def switch_server(src: mcdr.CommandSource, ctx: mcdr.CommandContext):
    """
    将玩家转移至另一服务器
    """

    # 服务器无法被转移，所以限定为玩家
    if not src.is_player:
        src.reply("Only players can use this command.")
        return

    # 现在必定是玩家类型了，强转
    src = cast(mcdr.PlayerCommandSource, src)

    player_name = src.player
    target_server_slug = ctx["server_slug"]

    # 如果对象是本服务器，不执行转移，也不请求
    if target_server_slug == state.server_data["slug"]:
        src.reply("你已经在这个服务器里了")
        return

    # 尝试获取在线服务器
    servers = try_get_servers(src.get_server())

    if servers is None:
        src.reply(mcdr.RText("获取在线服务器失败", color=mcdr.RColor.red))
        return

    # 遍历服务器列表，尝试找到匹配服务器的地址并转移
    # 注意这里不会特判目标是不是本服务器
    for server in servers.values():
        # 跳过非目标服务器
        if server["slug"] != target_server_slug:
            continue

        # 构造转移命令并执行
        command = f"/transfer {server['address']} {server['port']} {player_name}"
        src.get_server().execute(command)
        break
    # 如果没有匹配的服务器
    else:
        t = [
            mcdr.RText("没有ID为"),
            mcdr.RText(f"{target_server_slug}", color=mcdr.RColor.aqua),
            mcdr.RText("的服务器在线，试试使用"),
            mcdr.RText("!!goto", color=mcdr.RColor.yellow)
            .h("点击执行")
            .c(mcdr.RClickAction.suggest_command, "!!goto"),
            mcdr.RText("命令查看在线服务器清单"),
        ]
        src.reply(mcdr.RTextList(*t))


def register_command(server: mcdr.PluginServerInterface):
    """
    注册 goto 系列命令
    """

    builder = mcdr.SimpleCommandBuilder()

    server.register_help_message("!!goto", "用于切换服务器的命令")
    builder.command("!!goto", list_servers)  # type: ignore[operator]
    builder.command("!!goto <server_slug>", switch_server)  # type: ignore[operator]

    builder.arg("server_slug", mcdr.Text)

    builder.register(server)
