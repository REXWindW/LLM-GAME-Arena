"""
LLM API客户端 - 支持非法操作重试
"""
import requests
import time
import re
import urllib3
from typing import Optional, Any

from config import API_ENDPOINT, API_KEY, TIMEOUT_SECONDS, MAX_RETRIES
from logger import log_api_request

# 禁用SSL警告（某些API代理可能有SSL问题）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def call_llm(model: str, prompt: str, temperature: float = 0.1) -> Optional[str]:
    """
    调用LLM API获取响应

    Args:
        model: 模型名称
        prompt: 发送的prompt
        temperature: 温度参数

    Returns:
        LLM的响应文本，失败时返回None
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 50
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                API_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=TIMEOUT_SECONDS,
                verify=True  # 保持SSL验证
            )

            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                log_api_request(model, prompt, content)
                return content.strip()
            else:
                error_msg = f"API错误 (状态码 {response.status_code}): {response.text}"
                log_api_request(model, prompt, error=error_msg)
                print(error_msg)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2)

        except requests.Timeout:
            error_msg = f"API超时 ({TIMEOUT_SECONDS}秒)"
            log_api_request(model, prompt, error=error_msg)
            print(error_msg)
            if attempt < MAX_RETRIES - 1:
                time.sleep(2)

        except requests.exceptions.SSLError as e:
            error_msg = f"SSL错误: {e}"
            log_api_request(model, prompt, error=error_msg)
            print(error_msg)
            if attempt < MAX_RETRIES - 1:
                time.sleep(2)

        except requests.RequestException as e:
            error_msg = f"API请求异常: {e}"
            log_api_request(model, prompt, error=error_msg)
            print(error_msg)
            if attempt < MAX_RETRIES - 1:
                time.sleep(2)

    return None


def get_llm_move_with_retry(game, model: str, symbol: str, enable_thinking: bool = True,
                              max_illegal_retries: int = 2) -> dict:
    """
    带非法操作重试的LLM落子

    Args:
        game: 游戏实例（实现BaseGame接口）
        model: 模型名称
        symbol: 当前玩家符号 ('X' 或 'O')
        enable_thinking: 是否启用thinking模式
        max_illegal_retries: 非法操作最大重试次数

    Returns:
        dict with keys: 'move', 'thinking', 'raw_response'
    """
    from logger import log_move, logger

    result = {'move': None, 'thinking': '', 'raw_response': ''}

    # 第一次尝试
    prompt = game.get_llm_prompt(symbol, enable_thinking)
    response = call_llm(model, prompt)
    result['raw_response'] = response or ''

    if response is not None:
        result['thinking'] = game.extract_thinking(response)
        move = game.parse_llm_response(response)
        if move is not None and game.is_valid_move(move):
            result['move'] = move
            logger.info(f"LLM {model} ({symbol}) valid move: {move}")
            return result

    # 非法操作重试
    for retry in range(max_illegal_retries):
        attempted_move = game.parse_llm_response(response) if response else "unknown"
        reason = game.get_invalid_reason(attempted_move) if attempted_move != "unknown" else "Could not parse response"
        logger.warning(f"LLM {model} ({symbol}) invalid move: {attempted_move}, reason: {reason}")

        retry_prompt = game.get_illegal_move_prompt(symbol, attempted_move, reason)
        response = call_llm(model, retry_prompt)
        result['raw_response'] = response or ''

        if response is not None:
            result['thinking'] = game.extract_thinking(response)
            move = game.parse_llm_response(response)
            if move is not None and game.is_valid_move(move):
                result['move'] = move
                logger.info(f"LLM {model} ({symbol}) valid move after retry: {move}")
                return result

    # 所有重试失败，随机选择合法位置
    random_move = game.get_random_valid_move()
    result['move'] = random_move
    logger.warning(f"LLM {model} ({symbol}) failed after retries, using random: {random_move}")
    print(f"LLM {model} failed after retries, using random move")
    return result