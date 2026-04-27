"""
游戏模块 - 注册器和基类
"""
from typing import Dict, Type

# 游戏注册表
_game_registry: Dict[str, Type] = {}


def register_game(game_class: Type):
    """注册游戏类"""
    _game_registry[game_class.game_id] = game_class
    return game_class


def get_game_class(game_id: str) -> Type:
    """获取游戏类"""
    return _game_registry.get(game_id)


def get_all_games() -> Dict[str, Type]:
    """获取所有注册的游戏"""
    return _game_registry.copy()


def get_game_list() -> list:
    """获取游戏列表（用于前端显示）"""
    return [
        {
            'id': game_class.game_id,
            'name': game_class.game_name,
            'description': game_class.game_description
        }
        for game_class in _game_registry.values()
    ]