import json

from websocket import WebSocketException

from .. import state


def send_event_and_forget(action: str, data: dict):
    def _send():
        json_data = {
            "action": action,
            "data": data,
        }

        try:
            state.ws.send(json.dumps(json_data))
        except WebSocketException as _:
            pass

    state.threadpool_for_ws.submit(_send)
