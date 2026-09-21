import threading
from concurrent.futures import ThreadPoolExecutor
from logging import Logger

from mcdreforged import FunctionThread
from websocket import WebSocketApp

from .types import Server

# 日志记录器
logger: Logger
# BDTV hub 请求地址
hub_url_base: str
# 服务器数据
server_data: Server
# 是否需要终止心跳
stop_heartbeat: threading.Event
heartbeat_thread: FunctionThread
# 用于 ws 请求的线程池
threadpool_for_ws: ThreadPoolExecutor
# 与 hub 的 ws 连接
ws: WebSocketApp
ws_thread: FunctionThread
