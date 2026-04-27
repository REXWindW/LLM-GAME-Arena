"""
三维井字棋（重力版）游戏模块
"""
from games import register_game
from games.base import BaseGame
from .game import TicTacToe3DGame

# 注册游戏
register_game(TicTacToe3DGame)