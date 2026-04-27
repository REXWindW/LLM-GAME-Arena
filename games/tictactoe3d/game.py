"""
三维井字棋（重力版）游戏逻辑

棋盘结构:
- 3层 (Layer 0-2, 从下到上)
- 每层 3x3 = 27个位置
- 位置格式: (layer, row, col) 或 "L{layer}-R{row}-C{col}"

重力规则:
- Layer 0: 可自由落子
- Layer 1: 只有 (0, r, c) 有棋子时才能在 (1, r, c) 落子
- Layer 2: 只有 (1, r, c) 有棋子时才能在 (2, r, c) 落子

获胜条件: 三个连线（共49条获胜线）
"""
import random
import re
from typing import List, Optional, Any, Tuple, Set

from games.base import BaseGame


# 位置格式: (layer, row, col)
# layer: 0-2 (底层到顶层)
# row: 0-2 (上到下)
# col: 0-2 (左到右)

# 生成所有49条获胜线
def _generate_winning_lines() -> List[List[Tuple[int, int, int]]]:
    """生成所有获胜线"""
    lines = []

    # 1. 每层内的线 (每层8条: 3横+3竖+2斜) = 24条
    for layer in range(3):
        # 横线 (每行)
        for row in range(3):
            lines.append([(layer, row, 0), (layer, row, 1), (layer, row, 2)])
        # 竖线 (每列)
        for col in range(3):
            lines.append([(layer, 0, col), (layer, 1, col), (layer, 2, col)])
        # 斜线
        lines.append([(layer, 0, 0), (layer, 1, 1), (layer, 2, 2)])  # 主斜
        lines.append([(layer, 0, 2), (layer, 1, 1), (layer, 2, 0)])  # 副斜

    # 2. 垂直线 (穿过三层同一位置) = 9条
    for row in range(3):
        for col in range(3):
            lines.append([(0, row, col), (1, row, col), (2, row, col)])

    # 3. 跨层斜线 (从底层到顶层) = 16条
    # 3.1 沿row方向的斜线 (固定col)
    for col in range(3):
        # row 0→2 方向
        lines.append([(0, 0, col), (1, 1, col), (2, 2, col)])
        # row 2→0 方向
        lines.append([(0, 2, col), (1, 1, col), (2, 0, col)])

    # 3.2 沿col方向的斜线 (固定row)
    for row in range(3):
        # col 0→2 方向
        lines.append([(0, row, 0), (1, row, 1), (2, row, 2)])
        # col 2→0 方向
        lines.append([(0, row, 2), (1, row, 1), (2, row, 0)])

    # 3.3 三维主对角线 (同时沿row和col变化)
    lines.append([(0, 0, 0), (1, 1, 1), (2, 2, 2)])  # (0,0,0)→(2,2,2)
    lines.append([(0, 2, 2), (1, 1, 1), (2, 0, 0)])  # (0,2,2)→(2,0,0)
    lines.append([(0, 0, 2), (1, 1, 1), (2, 2, 0)])  # (0,0,2)→(2,2,0)
    lines.append([(0, 2, 0), (1, 1, 1), (2, 0, 2)])  # (0,2,0)→(2,0,2)

    return lines


WINNING_LINES = _generate_winning_lines()


class TicTacToe3DGame(BaseGame):
    """三维井字棋（重力版）"""

    game_id = "tictactoe3d"
    game_name = "三维井字棋"
    game_description = "重力版三维井字棋，需要下层支撑才能向上落子"

    def __init__(self):
        self.reset()

    def reset(self):
        """重置游戏"""
        # 棋盘: dict with key (layer, row, col) -> 'X', 'O', or ' '
        self.board: dict = {}
        for layer in range(3):
            for row in range(3):
                for col in range(3):
                    self.board[(layer, row, col)] = ' '
        self.current_player = 'X'
        self.winner: Optional[str] = None
        self.is_draw = False

    def _pos_to_str(self, pos: Tuple[int, int, int]) -> str:
        """将位置元组转换为字符串格式 L{layer}-R{row}-C{col}"""
        layer, row, col = pos
        return f"L{layer}-R{row}-C{col}"

    def _str_to_pos(self, pos_str: str) -> Optional[Tuple[int, int, int]]:
        """将字符串格式转换为位置元组"""
        match = re.match(r'L(\d)-R(\d)-C(\d)', pos_str.upper())
        if match:
            layer, row, col = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if self._is_valid_pos((layer, row, col)):
                return (layer, row, col)
        return None

    def _is_valid_pos(self, pos: Tuple[int, int, int]) -> bool:
        """检查位置是否在棋盘范围内"""
        layer, row, col = pos
        return 0 <= layer <= 2 and 0 <= row <= 2 and 0 <= col <= 2

    def _has_support(self, pos: Tuple[int, int, int]) -> bool:
        """检查位置是否有下层支撑（重力规则）"""
        layer, row, col = pos
        if layer == 0:
            return True  # 底层无需支撑
        # 检查正下方是否有棋子
        below = (layer - 1, row, col)
        return self.board[below] != ' '

    def get_board_visual(self) -> str:
        """返回可视化的棋盘字符串"""
        lines = []
        for layer in range(2, -1, -1):  # 从顶层到底层显示
            lines.append(f"\n=== Layer {layer} ===")
            b = self.board
            lines.append(f" {b[(layer,0,0)]} | {b[(layer,0,1)]} | {b[(layer,0,2)]}   positions: L{layer}-R0-C0, L{layer}-R0-C1, L{layer}-R0-C2")
            lines.append("-----------")
            lines.append(f" {b[(layer,1,0)]} | {b[(layer,1,1)]} | {b[(layer,1,2)]}   positions: L{layer}-R1-C0, L{layer}-R1-C1, L{layer}-R1-C2")
            lines.append("-----------")
            lines.append(f" {b[(layer,2,0)]} | {b[(layer,2,1)]} | {b[(layer,2,2)]}   positions: L{layer}-R2-C0, L{layer}-R2-C1, L{layer}-R2-C2")
        return '\n'.join(lines)

    def get_available_moves(self) -> List[str]:
        """返回可用位置列表（字符串格式）"""
        moves = []
        for pos, val in self.board.items():
            if val == ' ' and self._has_support(pos):
                moves.append(self._pos_to_str(pos))
        return moves

    def is_valid_move(self, move: Any) -> bool:
        """检查落子是否有效"""
        if isinstance(move, str):
            pos = self._str_to_pos(move)
            if pos is None:
                return False
            return self.board[pos] == ' ' and self._has_support(pos)
        elif isinstance(move, tuple):
            if not self._is_valid_pos(move):
                return False
            return self.board[move] == ' ' and self._has_support(move)
        return False

    def get_invalid_reason(self, move: Any) -> str:
        """获取落子无效的原因"""
        pos = None
        if isinstance(move, str):
            pos = self._str_to_pos(move)
            if pos is None:
                return f"Invalid format: '{move}'. Use format L{layer}-R{row}-C{col} (e.g., L0-R1-C2)"
        elif isinstance(move, tuple):
            pos = move
        else:
            return f"Invalid move type: expected string or tuple, got {type(move)}"

        if pos and not self._is_valid_pos(pos):
            return f"Position {self._pos_to_str(pos) if pos else move} is out of board range"

        if pos and self.board.get(pos) != ' ':
            return f"Position {self._pos_to_str(pos)} is already occupied"

        if pos and not self._has_support(pos):
            layer, row, col = pos
            if layer == 0:
                return f"Position {self._pos_to_str(pos)} cannot be placed (unexpected error)"
            below = (layer - 1, row, col)
            return f"Gravity rule violated: Position {self._pos_to_str(pos)} requires a piece at {self._pos_to_str(below)} below it"

        return "Unknown error"

    def make_move(self, move: Any, player: str) -> bool:
        """执行落子"""
        pos = None
        if isinstance(move, str):
            pos = self._str_to_pos(move)
        elif isinstance(move, tuple):
            pos = move

        if pos is None or not self.is_valid_move(pos):
            return False

        self.board[pos] = player

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
        for line in WINNING_LINES:
            if all(self.board[pos] == player for pos in line):
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
        # 将棋盘转换为前端友好的格式
        layers = []
        for layer in range(3):
            layer_data = []
            for row in range(3):
                row_data = []
                for col in range(3):
                    pos = (layer, row, col)
                    row_data.append({
                        'value': self.board[pos],
                        'position': self._pos_to_str(pos),
                        'has_support': self._has_support(pos),
                        'is_empty': self.board[pos] == ' '
                    })
                layer_data.append(row_data)
            layers.append({
                'layer': layer,
                'cells': layer_data
            })

        return {
            'layers': layers,
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
Layer 0 (bottom):
 {b[(0,0,0)]} | {b[(0,0,1)]} | {b[(0,0,2)]}
---------
 {b[(0,1,0)]} | {b[(0,1,1)]} | {b[(0,1,2)]}
---------
 {b[(0,2,0)]} | {b[(0,2,1)]} | {b[(0,2,2)]}

Layer 1:
 {b[(1,0,0)]} | {b[(1,0,1)]} | {b[(1,0,2)]}
---------
 {b[(1,1,0)]} | {b[(1,1,1)]} | {b[(1,1,2)]}
---------
 {b[(1,2,0)]} | {b[(1,2,1)]} | {b[(1,2,2)]}

Layer 2 (top):
 {b[(2,0,0)]} | {b[(2,0,1)]} | {b[(2,0,2)]}
---------
 {b[(2,1,0)]} | {b[(2,1,1)]} | {b[(2,1,2)]}
---------
 {b[(2,2,0)]} | {b[(2,2,1)]} | {b[(2,2,2)]}"""

        if enable_thinking:
            return f"""You are playing 3D Tic-Tac-Toe (Gravity) as {symbol}. Opponent: {opponent}.

GRAVITY: Layer 1/2 positions need piece below. Layer 0 can place anywhere.

Current board:{board_state}

Available moves: {available}

Win by 3-in-line (any layer row/column/diagonal, or vertical).

First, think about your strategy inside <thinking> tags, then give your move inside <answer> tags.

<thinking>
Analyze the board state. Consider:
- What are your winning opportunities?
- What threats does opponent have?
- Which available move is best?
</thinking>

<answer>
L[layer]-R[row]-C[col]
</answer>"""
        else:
            return f"""You are playing 3D Tic-Tac-Toe as {symbol}. Opponent: {opponent}.

Current board:{board_state}

Available moves: {available}

Reply with ONLY position like L0-R1-C1."""

    def get_illegal_move_prompt(self, symbol: str, attempted_move: Any, reason: str) -> str:
        """生成非法落子重试prompt"""
        available = self.get_available_moves()
        move_str = self._pos_to_str(attempted_move) if isinstance(attempted_move, tuple) else str(attempted_move)
        b = self.board

        return f"""Your move "{move_str}" is INVALID.

Reason: {reason}

Current state:

Layer 0:
 {b[(0,0,0)]} | {b[(0,0,1)]} | {b[(0,0,2)]}
---------
 {b[(0,1,0)]} | {b[(0,1,1)]} | {b[(0,1,2)]}
---------
 {b[(0,2,0)]} | {b[(0,2,1)]} | {b[(0,2,2)]}

Layer 1:
 {b[(1,0,0)]} | {b[(1,0,1)]} | {b[(1,0,2)]}
---------
 {b[(1,1,0)]} | {b[(1,1,1)]} | {b[(1,1,2)]}
---------
 {b[(1,2,0)]} | {b[(1,2,1)]} | {b[(1,2,2)]}

Layer 2:
 {b[(2,0,0)]} | {b[(2,0,1)]} | {b[(2,0,2)]}
---------
 {b[(2,1,0)]} | {b[(2,1,1)]} | {b[(2,1,2)]}
---------
 {b[(2,2,0)]} | {b[(2,2,1)]} | {b[(2,2,2)]}

Available moves: {available}

Provide a valid move.

<thinking>
Reconsider...
</thinking>

<answer>
L[layer]-R[row]-C[col]
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
            # 从answer内容中提取位置
            pos_match = re.search(r'L(\d)-R(\d)-C(\d)', content.upper())
            if pos_match:
                layer, row, col = int(pos_match.group(1)), int(pos_match.group(2)), int(pos_match.group(3))
                return (layer, row, col)

        # Fallback: 直接匹配位置格式
        match = re.search(r'L(\d)-R(\d)-C(\d)', response.upper())
        if match:
            layer, row, col = int(match.group(1)), int(match.group(2)), int(match.group(3))
            return (layer, row, col)

        return None

    def get_random_valid_move(self) -> Any:
        """随机选择合法落子"""
        moves = self.get_available_moves()
        if moves:
            move_str = random.choice(moves)
            return self._str_to_pos(move_str)
        return None