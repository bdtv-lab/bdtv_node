from .. import state
from ..types import Player
from .sender import send_event_and_forget


def heartbeat(players: list[Player]):
    """
    尝试发送心跳，无论是否成功
    """

    send_event_and_forget(
        "heartbeat",
        {
            "players": players,
            "server": state.server_data,
        },
    )
