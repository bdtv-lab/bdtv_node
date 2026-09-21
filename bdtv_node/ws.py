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
    pass
