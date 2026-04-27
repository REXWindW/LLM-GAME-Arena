"""
二维井字棋游戏模块
"""
from games import register_game
from games.base import BaseGame
from .game import TicTacToeGame

# 注册游戏
register_game(TicTacToeGame)