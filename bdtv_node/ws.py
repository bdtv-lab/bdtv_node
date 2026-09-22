import json

from mcdreforged.api.decorator import new_thread
from websocket import WebSocketApp

from . import state, ws_events


@new_thread("WebSocket")
def start_ws(delay: float = 5.0):

    state.ws.run_forever(reconnect=3)


def on_reconnect(ws: WebSocketApp):
    state.logger.info("已重新与 hub 建立 WebSocket 连接")
    ws_events.heartbeat([])


def handle_message(ws: WebSocketApp, data):
    logger = state.logger
    server = state.server_interface
    event: dict = json.loads(data)

    event_type = event.get("event", None)
    event_data = event.get("data", None)
    if event_type is None or event_data is None:
        return
    logger.info(f"接收到事件: {event_type}")

    match event_type:
        case "group_member_sent_msg":
            sender = event_data["sender_nickname"]
            message = event_data["message"]
            server.say(f"QQ <{sender}> {message}")
