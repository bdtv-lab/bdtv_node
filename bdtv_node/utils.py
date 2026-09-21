import mcdreforged as mcdr
import requests
from mcdreforged.api.decorator import new_thread

from whitelist_api import get_whitelist

from . import state, ws_events
from .types import Player, Server


def pure_players(players_name: list[str]) -> list[Player]:
    """
    提供玩家名称列表，从中筛出白名单中的玩家
    """

    # 获取白名单
    whitelist = get_whitelist()

    # 剔除不在白名单内的玩家
    # 限定为白名单是因为不在白名单里的通常是假人
    # TODO: 如果玩家改名，白名单不会及时更新，那么玩家就无法被判定
    real_players: list[Player] = [
        {"nickname": player.name, "uuid": player.uuid}
        for player in whitelist
        if player.name in players_name
    ]

    return real_players


def try_get_motd(server: mcdr.ServerInterface) -> mcdr.RTextBase | None:
    """
    尝试获取 MOTD 的 JSON 格式文本

    解析失败与请求失败均返回 None
    """

    try:
        raw = requests.get(f"{state.hub_url_base}/motd", timeout=(3, 3))
        component = mcdr.RTextBase.from_json_object(raw.json())
        return component
    except requests.RequestException as _:
        return None
    except TypeError as e:
        server.logger.error(f"无法解析 JSON 格式文本: {e}")
        return None


def try_get_servers(server: mcdr.ServerInterface) -> dict[str, Server] | None:
    """
    尝试获取在线的服务器列表

    解析失败与请求失败均返回 None
    """

    try:
        raw = requests.get(f"{state.hub_url_base}/servers", timeout=(3, 3))
        return raw.json()
    except requests.RequestException as _:
        return None
    except TypeError as e:
        server.logger.error(f"解析 JSON 出现错误: {e}")
        return None


@new_thread("RealPlayerJoin")
def handle_player_join(server: mcdr.PluginServerInterface, player: Player):
    """
    真实玩家加入游戏时的处理函数
    """

    ws_events.heartbeat([player])

    # 尝试给玩家展示 motd
    if motd := try_get_motd(server):
        server.logger.info(f"为 {player['nickname']} 展示 MOTD")
        server.tell(player["nickname"], motd)
