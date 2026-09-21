from mcdreforged.api.decorator import new_thread

from online_player_api import get_player_list

from . import state, ws_events
from .utils import pure_players


@new_thread("Heartbeat")
def start_heartbeat(delay: float = 5.0):
    """
    开始心跳循环线程，不断尝试发送服务器与在线玩家的心跳请求
    """

    logger = state.logger

    while not state.stop_heartbeat.is_set():
        # 获取在线玩家列表
        # 并筛选出白名单中的玩家
        players = pure_players(get_player_list())

        ws_events.heartbeat(players)

        state.stop_heartbeat.wait(delay)
    logger.info("Bye!")
