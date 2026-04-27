# 如何添加新游戏

本文档描述如何在 LLM-GAME-Arena 中添加新游戏。

## 步骤概览

### 1. 创建游戏模块

在 `games/` 目录下创建新文件夹：

```
games/your_game/
├── __init__.py      # 注册游戏
└── game.py          # 游戏逻辑
```

### 2. 实现 BaseGame 接口

在 `game.py` 中继承 `BaseGame` 类，实现所有必要方法：

```python
from games.base import BaseGame

class YourGame(BaseGame):
    game_id = "your_game"           # 唯一ID
    game_name = "你的游戏"           # 显示名称
    game_description = "游戏描述"    # 简短描述

    def reset(self):
        """重置游戏状态"""
        pass

    def get_board_visual(self) -> str:
        """返回棋盘可视化字符串（用于AI理解）"""
        pass

    def get_available_moves(self) -> list:
        """返回当前可用落子列表"""
        pass

    def is_valid_move(self, move) -> bool:
        """检查落子是否合法"""
        pass

    def get_invalid_reason(self, move) -> str:
        """返回落子非法的原因"""
        pass

    def make_move(self, move, player: str) -> bool:
        """执行落子"""
        pass

    def is_game_over(self) -> bool:
        """游戏是否结束"""
        pass

    def get_winner(self) -> str:
        """获取获胜者"""
        pass

    def get_current_player(self) -> str:
        """获取当前玩家"""
        pass

    def get_frontend_state(self) -> dict:
        """返回前端渲染所需的状态"""
        pass

    def get_llm_prompt(self, symbol: str) -> str:
        """生成AI prompt"""
        pass

    def get_illegal_move_prompt(self, symbol: str, attempted_move, reason: str) -> str:
        """生成非法落子重试prompt"""
        pass

    def parse_llm_response(self, response: str):
        """解析AI响应，提取落子"""
        pass

    def get_random_valid_move(self):
        """随机选择合法落子（fallback）"""
        pass
```

### 3. 注册游戏

在 `games/your_game/__init__.py` 中：

```python
from games import register_game
from games.base import BaseGame
from .game import YourGame

register_game(YourGame)
```

### 4. 添加前端UI

在 `templates/index.html` 中：
- 添加游戏选择卡片
- 添加棋盘HTML结构

在 `static/style.css` 中：
- 添加棋盘样式

在 `static/game.js` 中：
- 添加棋盘渲染和交互逻辑

## 关键设计原则

### Prompt 设计（重要！）

**核心原则：不给策略提示，只给规则和状态**

```python
def get_llm_prompt(self, symbol: str) -> str:
    return f"""You are playing {game_name} as player {symbol}.

RULES:
{规则描述}

Current state:
{当前棋盘状态}

Available moves: {可用落子列表}

Think step by step, then provide your move.

Format:
<thinking>
Your analysis here...
</thinking>

<answer>
Your final move here
</answer>
"""
```

**不要做的事：**
- ❌ 不要提供"策略建议"（如"优先占中心"）
- ❌ 不要告诉AI"你应该怎么做"
- ❌ 不要给出具体走法示例（可能引导AI）

**应该做的事：**
- ✅ 清晰描述游戏规则
- ✅ 清晰展示当前状态
- ✅ 列出可用落子
- ✅ 让AI自主思考决策

### 响应解析

使用 `<thinking>` 和 `<answer>` 格式：

```python
def parse_llm_response(self, response: str):
    if response is None:
        return None
    
    # 优先提取 <answer> 标签内容
    import re
    answer_match = re.search(r'<answer>(.*?)</answer>', response, re.DOTALL)
    if answer_match:
        return self._parse_move(answer_match.group(1).strip())
    
    # fallback: 直接解析整个响应
    return self._parse_move(response)
```

### 棋盘可视化

AI需要能理解棋盘状态，可视化要清晰：

```python
def get_board_visual(self) -> str:
    # 使用表格或网格形式
    # 标注每个位置的坐标和当前值
    # 空位用 'empty' 或 '.' 表示
```

## 测试新游戏

1. 启动服务器：`python app.py`
2. 打开浏览器：`http://localhost:5000`
3. 选择新游戏进行测试
4. 检查AI是否能正确理解和落子
5. 测试非法落子重试机制