# 项目架构

## 目录结构

```
llm-game-arena/
├── app.py                 # Flask后端主程序
├── config.py              # 配置（从.env读取）
├── llm_client.py          # LLM API调用
├── leaderboard.py         # 排行榜数据管理
├── logger.py              # 日志系统
│
├── games/                 # 游戏模块（可扩展）
│   ├── __init__.py        # 游戏注册器
│   ├── base.py            # 游戏基类
│   ├── tictactoe/         # 二维井字棋
│   └── tictactoe3d/       # 三维井字棋
│
├── templates/
│   └── index.html         # 主页面
│
├── static/
│   ├── style.css          # 样式
│   └── game.js            # 前端逻辑
│
├── AGENT/                 # 开发维护文档
│   ├── README.md
│   ├── ADD_GAME.md
│   ├── PROMPT_DESIGN.md
│   └── ARCHITECTURE.md
│
├── .env                   # API配置（不提交）
├── .env.example           # 配置模板
├── .gitignore
├── requirements.txt
└── README.md
```

## 核心模块

### games/base.py - 游戏基类

所有游戏必须实现 `BaseGame` 接口。关键方法：

| 方法 | 用途 |
|------|------|
| `get_llm_prompt()` | 生成AI Prompt（核心） |
| `parse_llm_response()` | 解析AI响应 |
| `get_board_visual()` | 棋盘可视化（AI理解） |
| `get_available_moves()` | 可用落子列表 |

### llm_client.py - LLM调用

- `call_llm()` - 基础API调用
- `get_llm_move_with_retry()` - 带非法重试的落子

### app.py - Flask路由

| 路由 | 功能 |
|------|------|
| `/api/new_game` | 创建新游戏 |
| `/api/make_move` | 人类落子 |
| `/api/ai_move` | AI落子 |
| `/api/auto_play` | AI自动对战 |
| `/api/leaderboard` | 排行榜 |
| `/api/player_history` | 玩家历史 |

## 数据流

```
人类落子:
前端 → /api/make_move → 后端验证 → 更新状态 → 检查AI回合 → /api/ai_move → LLM调用

AI落子:
1. get_llm_prompt() → 生成Prompt
2. call_llm() → 调用API
3. parse_llm_response() → 解析响应
4. 验证合法性 → 有效则执行，无效则重试
```

## 添加新游戏

参考 `AGENT/ADD_GAME.md`。

核心步骤：
1. 在 `games/` 下创建模块
2. 实现 `BaseGame` 接口
3. 注册游戏
4. 添加前端UI

## 扩展设计

项目设计为易于扩展：
- 新游戏只需实现接口，无需修改核心代码
- Prompt风格统一，便于评测对比
- 前端复用通用组件