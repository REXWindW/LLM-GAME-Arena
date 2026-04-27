"""
日志模块 - 每次启动清空日志文件
"""
import os
import logging
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), 'game.log')


def setup_logger():
    """设置日志器，每次启动清空日志文件"""
    # 清空日志文件
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            f.write(f"=== Log started at {datetime.now().isoformat()} ===\n")

    # 创建logger
    logger = logging.getLogger('llm-game')
    logger.setLevel(logging.DEBUG)

    # 文件handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)

    # 格式
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    file_handler.setFormatter(formatter)

    # 添加handler
    logger.addHandler(file_handler)

    return logger


# 全局logger实例
logger = setup_logger()


def log_api_request(model: str, prompt: str, response: str = None, error: str = None):
    """记录API请求"""
    logger.info(f"API Request | Model: {model}")
    logger.debug(f"Prompt: {prompt[:200]}..." if len(prompt) > 200 else f"Prompt: {prompt}")
    if response:
        logger.info(f"Response: {response}")
    if error:
        logger.error(f"Error: {error}")


def log_game_event(session_id: str, event: str, details: dict = None):
    """记录游戏事件"""
    msg = f"Game {session_id} | {event}"
    if details:
        msg += f" | {details}"
    logger.info(msg)


def log_move(session_id: str, player: str, move: any, valid: bool, reason: str = None):
    """记录落子"""
    status = "VALID" if valid else "INVALID"
    msg = f"Game {session_id} | Move: {player} -> {move} | {status}"
    if reason:
        msg += f" | Reason: {reason}"
    logger.info(msg)