import logging
import threading
from concurrent.futures import ThreadPoolExecutor

import mcdreforged as mcdr
from websocket import WebSocketApp

from . import state
from .commands import register_command
from .config import load_or_init_config
from .heart import start_heartbeat
from .utils import handle_player_join, pure_players
from .ws import handle_message, on_reconnect, start_ws


def on_player_joined(server: mcdr.PluginServerInterface, player: str, info: mcdr.Info):
    real_player = pure_players([player])

    # 非 0 则为单一玩家名称存在于白名单中
    if len(real_player) != 0:
        handle_player_join(server, real_player[0])  # type: ignore[operator]


def on_user_info(server: mcdr.PluginServerInterface, info: mcdr.Info):
    if not info.is_player:
        return

    state.logger.info(info.content)


def on_load(server: mcdr.PluginServerInterface, prev_module):
    state.logger = server.logger
    logger = state.logger

    logger.info("分配线程池")
    state.threadpool_for_ws = ThreadPoolExecutor(max_workers=4)

    config = load_or_init_config(server)
    logger.info("配置文件已加载")

    state.server_data = {
        "address": config["mc_public_address"],
        "port": config["mc_port"],
        "nickname": config["server_nickname"],
        "slug": config["server_slug"],
    }
    state.hub_url_base = config["bdtv_hub_base"]

    register_command(server)

    logging.getLogger("websocket").setLevel(logging.WARNING)
    state.ws = WebSocketApp(
        f"{config['bdtv_hub_base'].replace('https://', 'wss://').replace('http://', 'ws://')}/ws",
        on_message=handle_message,
        on_open=lambda ws: logger.info("与 hub 的 WebSocket 连接已建立"),
        on_error=lambda ws, e: logger.error(f"与 hub 的 WebSocket 连接出现错误: {e}"),
        on_close=lambda ws, state, msg: logger.warning(
            f"与 hub 的 WebSocket 连接已断开{f': {msg}' if msg is not None else ''}"
        ),
        on_reconnect=on_reconnect,
    )

    state.ws_thread = start_ws()  # type: ignore[operator]

    state.stop_heartbeat = threading.Event()

    state.heartbeat_thread = start_heartbeat()  # type: ignore[operator]


def on_unload(server: mcdr.PluginServerInterface):
    logger = state.logger

    # 向心跳线程发送终止信号
    state.stop_heartbeat.set()
    # 等待心跳线程终止
    logger.info("等待心跳线程终止")
    state.heartbeat_thread.join()

    logger.info("等待 WebSocket 线程终止")
    state.ws.close()
    state.ws_thread.join()

    logger.info("等待线程池终止")
    state.threadpool_for_ws.shutdown(wait=True)
