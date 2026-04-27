# AGENT 文档

本目录包含 LLM-GAME-Arena 项目的开发维护文档。

## 文档索引

| 文档 | 描述 |
|------|------|
| [ADD_GAME.md](ADD_GAME.md) | 如何添加新游戏 |
| [PROMPT_DESIGN.md](PROMPT_DESIGN.md) | Prompt设计原则与思路 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 项目架构说明 |

## 项目目标

LLM-GAME-Arena 的核心目标是**评测大模型的游戏策略能力**，而非让AI执行预设策略。

因此：
- Prompt 不提供策略建议
- Prompt 只描述规则和当前状态
- 让大模型自主思考、自主决策
- 观察不同模型的策略差异