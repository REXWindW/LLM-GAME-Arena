# Prompt 设计原则

本文档描述 LLM-GAME-Arena 的 Prompt 设计思路。

## 核心目标

我们的目标是**评测大模型的游戏策略能力**，而非让AI执行我们预设的策略。

这意味着：
- 我们想知道：不同模型在同样的游戏规则下，会有什么不同的策略？
- 我们不想：给AI策略建议，导致所有模型的决策趋同
- 我们期待：观察AI的"原生智慧"，看它们能否自主发现最优策略

## Thinking 观察模式

项目支持开启/关闭Thinking观察：

**开启时**：Prompt要求AI使用 `<thinking>` 和 `<answer>` 格式
```
<thinking>
AI的思考过程...
</thinking>

<answer>
最终决策
</answer>
```

**关闭时**：Prompt要求AI直接输出答案

前端会实时显示所有AI的thinking内容，让用户探究：
- AI是如何分析当前局势的？
- AI是如何制定策略的？
- 不同模型的思考方式有何差异？

## 设计原则

### 1. 只给规则，不给策略

**错误示例（不要这样做）：**
```
Strategy tips:
- Always try to control the center (position 5)
- Block your opponent when they have 2 in a row
- Corners are good opening moves
```

这样做的问题：
1. 我们给出的策略未必是最优的
2. 不同模型本可能有不同的策略倾向，但会被我们的提示引导趋同
3. 无法真实评测模型的策略思维能力

**正确示例：**
```
Goal: Get 3 of your marks in a row to win.

Current board state:
[显示棋盘状态]

Available moves: [1, 3, 7]

Think and decide your move.
```

### 2. 清晰展示状态

AI需要能准确理解当前局势。状态展示要：
- 格式清晰、易于理解
- 包含所有必要信息（位置、值、坐标）
- 不遗漏任何关键信息

**好的状态展示：**
```
Current Board:
Position:  1   2   3    |    Value: X | O | empty
Position:  4   5   6    |    Value: empty | X | empty
Position:  7   8   9    |    Value: O | empty | empty
```

### 3. 使用 Thinking-Answer 格式

让模型使用 `<thinking>` 和 `<answer>` 标签：

```
Think step by step about your strategy.
Use this format:

<thinking>
Analyze the current situation:
- What positions are available?
- Are there any winning opportunities?
- Are there any threats from opponent?
- What is the best strategic choice?

</thinking>

<answer>
Your final move (just the position code)
</answer>
```

这样做的好处：
1. 模型可以进行深度思考
2. 我们可以观察模型的思考过程
3. 提取答案更准确

### 4. 简洁但不遗漏

Prompt要简洁，但不能遗漏关键信息：
- 游戏规则
- 当前状态
- 可用落子
- 输出格式要求

**不要添加：**
- 策略建议
- 具体走法示例（可能引导AI）
- 过多的解释

### 5. 一致性

不同游戏的Prompt风格保持一致：
- 使用相同的状态展示格式风格
- 使用相同的输出格式要求
- 使用相同的思考引导（但不给策略）

## 非法落子重试

当AI给出非法落子时，重试Prompt也要遵循同样原则：

```
Your move "{attempted_move}" is not valid.

Reason: {具体的非法原因}

Current state: {重新展示状态}
Available moves: {重新列出可用落子}

Think again and provide a valid move.

<thinking>
Your analysis...
</thinking>

<answer>
Valid move from available list
</answer>
```

不要在重试时给策略提示。

## 解析响应

从 `<answer>` 标签提取答案：

```python
import re

def parse_llm_response(response: str):
    if response is None:
        return None
    
    # 优先提取 <answer>
    match = re.search(r'<answer>(.*?)</answer>', response, re.DOTALL | re.IGNORECASE)
    if match:
        content = match.group(1).strip()
        return parse_move_format(content)
    
    # Fallback: 尝试直接解析
    return parse_move_format(response)
```

## 为什么不给策略？

假设我们告诉AI"优先占中心"，会有以下问题：

1. **策略未必最优**：在某些情况下，边角开局可能更好，我们的提示可能是错的

2. **失去评测意义**：如果所有模型都按我们的策略走，我们无法评测它们的策略能力

3. **掩盖真实能力**：模型可能有自己的策略见解，被我们的提示覆盖了

4. **游戏复杂度高时更明显**：三维井字棋等复杂游戏，策略空间大，我们很难给出最优策略

## 期待观察的内容

通过不给策略提示，我们可以观察：

- 不同模型是否有不同的策略倾向？
- 模型能否自主发现最优策略？
- 模型的思考深度如何？
- 模型在复杂游戏中的表现差异？

这才是真正的"AI模型评测"意义所在。