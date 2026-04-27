"""
二维井字棋游戏逻辑
"""
import random
import re
from typing import List, Optional, Any

from games.base import BaseGame


# 棋盘位置映射 (1-9)
#  1 | 2 | 3
# -----------
#  4 | 5 | 6
# -----------
#  7 | 8 | 9

WINNING_COMBINATIONS = [
    (1, 2, 3), (4, 5, 6), (7, 8, 9),  # 横
    (1, 4, 7), (2, 5, 8), (3, 6, 9),  # 竖
    (1, 5, 9), (3, 5, 7)              # 斜
]


class TicTacToeGame(BaseGame):
    """二维井字棋游戏"""

    game_id = "tictactoe"
    game_name = "井字棋"
    game_description = "经典二维井字棋，三连线获胜"

    def __init__(self):
        self.reset()

    def reset(self):
        """重置游戏"""
        self.board = {i: ' ' for i in range(1, 10)}
        self.current_player = 'X'
        self.winner: Optional[str] = None
        self.is_draw = False

    def get_board_visual(self) -> str:
        """返回可视化的棋盘字符串"""
        b = self.board
        return f"""
 1 | 2 | 3    {b[1]} | {b[2]} | {b[3]}
-----------  -----------
 4 | 5 | 6    {b[4]} | {b[5]} | {b[6]}
-----------  -----------
 7 | 8 | 9    {b[7]} | {b[8]} | {b[9]}
""".strip()

    def get_available_moves(self) -> List[int]:
        """返回可用位置列表"""
        return [pos for pos, val in self.board.items() if val == ' ']

    def is_valid_move(self, move: Any) -> bool:
        """检查落子是否有效"""
        if isinstance(move, int):
            return move in range(1, 10) and self.board.get(move) == ' '
        return False

    def get_invalid_reason(self, move: Any) -> str:
        """获取落子无效的原因"""
        if not isinstance(move, int):
            return f"Invalid format: expected a number 1-9, got '{move}'"
        if move not in range(1, 10):
            return f"Position {move} is out of range (valid: 1-9)"
        if self.board.get(move) != ' ':
            return f"Position {move} is already occupied"
        return "Unknown error"

    def make_move(self, move: Any, player: str) -> bool:
        """执行落子"""
        if not self.is_valid_move(move):
            return False

        self.board[move] = player

        # 检查获胜
        if self._check_winner(player):
            self.winner = player
        elif not self.get_available_moves():
            self.is_draw = True
        else:
            self.current_player = 'O' if self.current_player == 'X' else 'X'

        return True

    def _check_winner(self, player: str) -> bool:
        """检查指定玩家是否获胜"""
        for combo in WINNING_COMBINATIONS:
            if all(self.board[pos] == player for pos in combo):
                return True
        return False

    def is_game_over(self) -> bool:
        """游戏是否结束"""
        return self.winner is not None or self.is_draw

    def get_winner(self) -> Optional[str]:
        """获取获胜者"""
        return self.winner

    def get_current_player(self) -> str:
        """获取当前玩家"""
        return self.current_player

    def get_frontend_state(self) -> dict:
        """获取前端渲染所需的状态"""
        return {
            'board': self.board.copy(),
            'board_visual': self.get_board_visual(),
            'current_player': self.current_player,
            'winner': self.winner,
            'is_draw': self.is_draw,
            'is_game_over': self.is_game_over(),
            'available_moves': self.get_available_moves()
        }

    def get_llm_prompt(self, symbol: str, enable_thinking: bool = True) -> str:
        """生成AI prompt"""
        opponent = 'O' if symbol == 'X' else 'X'
        available = self.get_available_moves()
        b = self.board

        board_state = f"""
 {b[1]} | {b[2]} | {b[3]}
---------
 {b[4]} | {b[5]} | {b[6]}
---------
 {b[7]} | {b[8]} | {b[9]}
(Empty cells shown as spaces. Positions: 1-9)"""

        if enable_thinking:
            return f"""You are playing Tic-Tac-Toe as {symbol}. Opponent: {opponent}.

RULES: Get 3 {symbol} in a row (horizontal, vertical, or diagonal).

Current board:{board_state}

Available moves: {available}

First, think about your strategy inside <thinking> tags, then give your move inside <answer> tags.

<thinking>
Analyze the board. Consider:
- Do you have a winning move?
- Does opponent have a threat to block?
- What is the best position?
</thinking>

<answer>
[position number]
</answer>"""
        else:
            return f"""You are playing Tic-Tac-Toe as {symbol}. Opponent: {opponent}.

Current board:{board_state}

Available moves: {available}

Reply with ONLY one number from {available}."""

    def get_illegal_move_prompt(self, symbol: str, attempted_move: Any, reason: str) -> str:
        """生成非法落子重试prompt"""
        available = self.get_available_moves()
        b = self.board

        return f"""Your previous move "{attempted_move}" is INVALID.

Reason: {reason}

Current board state:
 {b[1]} | {b[2]} | {b[3]}
---------
 {b[4]} | {b[5]} | {b[6]}
---------
 {b[7]} | {b[8]} | {b[9]}

Available moves: {available}

Provide a valid move.

<thinking>
Reconsider your strategy...
</thinking>

<answer>
[valid position from available list]
</answer>"""

    def extract_thinking(self, response: str) -> str:
        """从响应中提取thinking内容"""
        if response is None:
            return ""
        match = re.search(r'<thinking>(.*?)</thinking>', response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def parse_llm_response(self, response: str) -> Any:
        """解析AI响应"""
        if response is None:
            return None

        # 优先提取 <answer> 标签内容
        match = re.search(r'<answer>(.*?)</answer>', response, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            # 从answer内容中提取数字
            num_match = re.search(r'\d+', content)
            if num_match:
                return int(num_match.group())

        # Fallback: 直接提取数字
        match = re.search(r'\d+', response)
        if match:
            return int(match.group())

        return None

    def get_random_valid_move(self) -> Any:
        """随机选择合法落子"""
        return random.choice(self.get_available_moves())