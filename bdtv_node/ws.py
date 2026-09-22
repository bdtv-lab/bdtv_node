import json

import mcdreforged as mcdr
from mcdreforged.api.decorator import new_thread
from websocket import WebSocketApp

from bdtv_node.types import Player, Server
from bdtv_node.utils import pure_players
from online_player_api import get_player_list

from . import state, ws_events


@new_thread("WebSocket")
def start_ws(delay: float = 5.0):

    state.ws.run_forever(reconnect=3)


def on_reconnect(ws: WebSocketApp):
    state.logger.info("已重新与 hub 建立 WebSocket 连接")
    players = pure_players(get_player_list())
    ws_events.heartbeat(players)


def handle_message(ws: WebSocketApp, data):
    logger = state.logger
    server = state.server_interface
    event: dict = json.loads(data)

    event_type = event.get("event", None)
    event_data = event.get("data", None)
    if event_type is None or event_data is None:
        return
    logger.info(f"接收到事件: {event_type}")

    # 处理来自服务器的事件
    match event_type:
        case "group_member_sent_msg":
            sender_nickname = event_data["sender_nickname"]
            message = event_data["message"]
            server.say(f"QQ <{sender_nickname}> {message}")

        case "client_sent_msg":
            sender: Player = event_data["sender"]
            source: Server = event_data["source"]
            message = event_data["message"]
            server.say(f"{source['nickname']} <{sender['nickname']}> {message}")

        case "console_sent_msg":
            server.say(f"[Server] {event_data}")

        case "player_join":
            s: Server = event_data["server"]
            p: Player = event_data["player"]
            server.say(mcdr.RTextList(f"§e{p['nickname']}加入了{s['nickname']}§r"))

        case "player_left":
            s: Server = event_data["server"]
            p: Player = event_data["player"]
            server.say(mcdr.RTextList(f"§e{p['nickname']}离开了{s['nickname']}§r"))
