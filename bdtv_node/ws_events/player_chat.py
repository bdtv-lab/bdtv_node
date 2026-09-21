from .. import state
from ..types import Player
from .sender import send_event_and_forget


def player_chat(player: Player, content: str):
    send_event_and_forget(
        "player_chat",
        {
            "player": player,
            "server": state.server_data,
            "content": content,
        },
    )
