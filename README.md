<p align="center">
  <img src="figures/head_image.png" alt="LLM-GAME-Arena" width="600">
</p>

<h1 align="center">LLM-GAME-Arena ⚔️</h1>

<p align="center">
  <strong>AI模型对战竞技场</strong>
</p>

<p align="center">
  让不同的AI模型互相博弈，看看谁的策略更强！
</p>

<p align="center">
  <a href="#游戏功能">游戏功能</a> •
  <a href="#quick-start">快速开始</a> •
  <a href="#支持的模型">模型支持</a>
</p>

---

## 🎮 游戏功能

### 支持的游戏

| 游戏 | 描述 |
|------|------|
| **井字棋** | 经典二维井字棋，三连线获胜。简单有趣，适合快速对战。 |
| **三维井字棋** | 立体棋盘，三层堆叠。重力规则：只有下层有棋子支撑才能在上方落子。更复杂的策略，考验AI的空间思维。 |

### 游戏模式

| 模式 | 说明 |
|------|------|
| **模型 vs 模型** | 输入两个AI模型名称，观看它们自动对战。点击"自动对战"一键完成整局。 |
| **人类 vs 模型** | 输入你的名字和对手模型，选择先手或后手，与AI实时对战。 |

### 排行榜系统

- 📊 自动记录每次对战的胜负
- 🏆 积分 = 胜场 - 负场
- 📜 点击玩家可展开查看历史对局详情
- 🎯 按积分排名，看看哪个模型最强

### 观察AI思考 🧠

这是本项目最有趣的功能！

- ✅ **开启Thinking模式**：在游戏设置中勾选"观察AI思考"
- 📝 **实时查看**：每次AI落子后，显示其思考过程
- 🔍 **探究AI智慧**：看看不同模型如何分析局势、制定策略
- 📜 **思考历史**：整局对战的thinking历史都保存下来

**我们不给AI任何策略提示**，只提供规则和当前状态，让AI自主思考决策。这样可以：
- 评测AI的原生策略能力
- 观察不同模型的思维差异
- 发现AI是否能自主找到最优策略

### AI智能落子

- 🤖 模型会收到清晰的规则说明和棋盘状态
- ⚠️ 如果AI落子非法（如违反重力规则），系统会提醒它重新思考
- 🎲 多次失败后自动选择合法位置，保证游戏流畅进行

---

## 🚀 Quick Start

### 1. 克隆项目

```bash
git clone https://github.com/your-username/llm-game-arena.git
cd llm-game-arena
```

### 2. 创建环境

```bash
conda create -n llm-game python=3.10 -y
conda activate llm-game
pip install -r requirements.txt
```

### 3. 配置API

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的API配置
```

`.env` 文件内容示例：

```env
API_ENDPOINT=https://api.whatai.cc/v1/chat/completions
API_KEY=your-api-key-here
```

> 💡 **支持的API平台**：任何OpenAI格式兼容的API均可使用，如 [OpenRouter](https://openrouter.ai)、[WhatAI](https://whatai.cc) 等。

### 4. 启动服务

```bash
conda activate llm-game
python app.py
```

打开浏览器访问：**http://localhost:5000**

### 5. 开始游戏

1. 选择一个游戏（井字棋 🎯 或 三维井字棋 📦）
2. 选择对战模式
3. 输入模型名称（如 `gpt-4`、`claude-3-opus`、`deepseek-v3`）
4. 开始对战！

---

## 🤖 支持的模型

取决于你的API转发平台，通常支持：

| 类型 | 模型示例 |
|------|----------|
| OpenAI | `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo` |
| Anthropic | `claude-3-opus`, `claude-3-sonnet`, `claude-3-haiku` |
| Google | `gemini-pro`, `gemini-1.5-flash` |
| Meta | `llama-3-70b`, `llama-3-8b` |
| DeepSeek | `deepseek-chat`, `deepseek-coder` |
| Mistral | `mistral-large`, `mistral-medium` |
| 其他 | 请参考你的API平台文档 |

---

## 📁 项目结构

```
llm-game-arena/
├── app.py                 # Flask后端主程序
├── games/                 # 游戏模块（可扩展）
│   ├── tictactoe/         # 二维井字棋
│   └── tictactoe3d/       # 三维井字棋
├── templates/             # HTML模板
├── static/                # CSS/JS/图片
├── .env                   # API配置（请勿提交）
└── README.md
```

---

## 📝 License

MIT License

---

<p align="center">
  如果觉得有趣，欢迎 ⭐ Star！
</p>