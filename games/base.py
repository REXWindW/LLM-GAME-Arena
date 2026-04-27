"""
游戏基类 - 所有游戏必须实现这些接口
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, List


class BaseGame(ABC):
    """游戏基类"""

    @property
    @abstractmethod
    def game_id(self) -> str:
        """游戏唯一标识"""
        pass

    @property
    @abstractmethod
    def game_name(self) -> str:
        """游戏显示名称"""
        pass

    @property
    @abstractmethod
    def game_description(self) -> str:
        """游戏描述"""
        pass

    @abstractmethod
    def get_board_visual(self) -> str:
        """获取棋盘可视化字符串（用于AI prompt）"""
        pass

    @abstractmethod
    def get_available_moves(self) -> List[Any]:
        """获取所有合法落子"""
        pass

    @abstractmethod
    def is_valid_move(self, move: Any) -> bool:
        """检查落子是否有效"""
        pass

    @abstractmethod
    def get_invalid_reason(self, move: Any) -> str:
        """获取落子无效的原因"""
        pass

    @abstractmethod
    def make_move(self, move: Any, player: str) -> bool:
        """执行落子"""
        pass

    @abstractmethod
    def is_game_over(self) -> bool:
        """游戏是否结束"""
        pass

    @abstractmethod
    def get_winner(self) -> Optional[str]:
        """获取获胜者"""
        pass

    @abstractmethod
    def get_current_player(self) -> str:
        """获取当前玩家"""
        pass

    @abstractmethod
    def get_frontend_state(self) -> dict:
        """获取前端渲染所需的状态"""
        pass

    @abstractmethod
    def get_llm_prompt(self, symbol: str, enable_thinking: bool = True) -> str:
        """生成AI prompt

        Args:
            symbol: 当前玩家符号
            enable_thinking: 是否启用thinking模式（True则要求<thinking>标签）
        """
        pass

    @abstractmethod
    def extract_thinking(self, response: str) -> str:
        """从响应中提取thinking内容

        Args:
            response: LLM原始响应

        Returns:
            thinking内容，如果没有则返回空字符串
        """
        pass

    @abstractmethod
    def get_illegal_move_prompt(self, symbol: str, attempted_move: Any, reason: str) -> str:
        """生成非法落子重试prompt"""
        pass

    @abstractmethod
    def parse_llm_response(self, response: str) -> Any:
        """解析AI响应，返回落子"""
        pass

    @abstractmethod
    def get_random_valid_move(self) -> Any:
        """随机选择一个合法落子"""
        pass

    @abstractmethod
    def reset(self):
        """重置游戏"""
        pass