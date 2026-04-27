/**
 * LLM-GAME-Arena 前端游戏逻辑
 * 支持多游戏：二维井字棋 + 三维井字棋
 */

// 状态
let currentGameType = null;
let currentSessionId = null;
let currentMode = 'ai_vs_ai';
let isHumanTurn = false;
let humanSide = 'X';

// DOM元素
const gameSelectPanel = document.getElementById('game-select-panel');
const setupPanel = document.getElementById('setup-panel');
const gamePanel = document.getElementById('game-panel');
const leaderboardPanel = document.getElementById('leaderboard-panel');

const gameCards = document.querySelectorAll('.game-card');
const selectedGameTitle = document.getElementById('selected-game-title');

const modeRadios = document.querySelectorAll('input[name="mode"]');
const humanSideRadios = document.querySelectorAll('input[name="human-side"]');

const aiVsAiInputs = document.getElementById('ai-vs-ai-inputs');
const humanVsAiInputs = document.getElementById('human-vs-ai-inputs');
const playerXInput = document.getElementById('player-x');
const playerOInput = document.getElementById('player-o');
const humanNameInput = document.getElementById('human-name');
const aiModelInput = document.getElementById('ai-model');

const backBtn = document.getElementById('back-btn');
const startBtn = document.getElementById('start-btn');
const autoPlayBtn = document.getElementById('auto-play-btn');
const newGameBtn = document.getElementById('new-game-btn');
const refreshLeaderboardBtn = document.getElementById('refresh-leaderboard');

const xNameSpan = document.getElementById('x-name');
const oNameSpan = document.getElementById('o-name');
const currentTurnSpan = document.getElementById('current-turn');
const gameStatusSpan = document.getElementById('game-status');
const aiStatusDiv = document.getElementById('ai-status');

// Thinking相关
const enableThinkingCheckbox = document.getElementById('enable-thinking');
const thinkingPanel = document.getElementById('thinking-panel');
const thinkingHistory = document.getElementById('thinking-history');

// 棋盘元素
const tictactoeBoard = document.getElementById('tictactoe-board');
const tictactoe3dBoard = document.getElementById('tictactoe3d-board');
const cells2D = document.querySelectorAll('.cell');
const cells3D = document.querySelectorAll('.cell-3d');

const leaderboardBody = document.getElementById('leaderboard-body');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initGameSelection();
    initModeSelector();
    initGameControls();
    initBoards();
    loadLeaderboard();
});

// 游戏选择
function initGameSelection() {
    gameCards.forEach(card => {
        card.addEventListener('click', () => {
            currentGameType = card.dataset.game;
            const gameName = card.querySelector('h3').textContent;
            selectedGameTitle.textContent = `${gameName} - 游戏设置`;

            gameSelectPanel.classList.add('hidden');
            setupPanel.classList.remove('hidden');
        });
    });
}

// 模式选择器
function initModeSelector() {
    modeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            currentMode = e.target.value;
            updatePlayerInputs();
        });
    });

    humanSideRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            humanSide = e.target.value;
        });
    });

    updatePlayerInputs();
}

function updatePlayerInputs() {
    if (currentMode === 'ai_vs_ai') {
        aiVsAiInputs.classList.remove('hidden');
        humanVsAiInputs.classList.add('hidden');
        autoPlayBtn.classList.remove('hidden');
    } else {
        aiVsAiInputs.classList.add('hidden');
        humanVsAiInputs.classList.remove('hidden');
        autoPlayBtn.classList.add('hidden');
    }
}

// 游戏控制按钮
function initGameControls() {
    backBtn.addEventListener('click', () => {
        setupPanel.classList.add('hidden');
        gameSelectPanel.classList.remove('hidden');
        currentGameType = null;
    });

    startBtn.addEventListener('click', startGame);
    autoPlayBtn.addEventListener('click', autoPlay);
    newGameBtn.addEventListener('click', () => {
        gamePanel.classList.add('hidden');
        gameSelectPanel.classList.remove('hidden');
        currentGameType = null;
        resetBoards();
    });
    refreshLeaderboardBtn.addEventListener('click', loadLeaderboard);
}

// 棋盘点击
function initBoards() {
    // 二维井字棋
    cells2D.forEach(cell => {
        cell.addEventListener('click', () => {
            if (!isHumanTurn || !currentSessionId || currentGameType !== 'tictactoe') return;
            if (cell.classList.contains('taken')) return;

            const pos = parseInt(cell.dataset.pos);
            humanMove(pos);
        });
    });

    // 三维井字棋
    cells3D.forEach(cell => {
        cell.addEventListener('click', () => {
            if (!isHumanTurn || !currentSessionId || currentGameType !== 'tictactoe3d') return;
            if (cell.classList.contains('taken') || cell.classList.contains('blocked')) return;

            const pos = cell.dataset.pos;
            humanMove(pos);
        });
    });
}

// 开始游戏
async function startGame() {
    if (!currentGameType) {
        alert('请先选择游戏');
        return;
    }

    let playerX, playerO, xIsAi, oIsAi;
    const enableThinking = enableThinkingCheckbox.checked;

    if (currentMode === 'ai_vs_ai') {
        playerX = playerXInput.value || 'gpt-4';
        playerO = playerOInput.value || 'claude-3-opus';
        xIsAi = true;
        oIsAi = true;
    } else {
        const humanName = humanNameInput.value || 'Human';
        const aiModel = aiModelInput.value || 'gpt-4';

        if (humanSide === 'X') {
            playerX = humanName;
            playerO = aiModel;
            xIsAi = false;
            oIsAi = true;
        } else {
            playerX = aiModel;
            playerO = humanName;
            xIsAi = true;
            oIsAi = false;
        }
    }

    try {
        const response = await fetch('/api/new_game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                game_type: currentGameType,
                mode: currentMode,
                player_x: playerX,
                player_o: playerO,
                x_is_ai: xIsAi,
                o_is_ai: oIsAi,
                enable_thinking: enableThinking
            })
        });

        const data = await response.json();
        if (data.error) {
            alert(data.error);
            return;
        }

        currentSessionId = data.session_id;
        xNameSpan.textContent = data.players.x;
        oNameSpan.textContent = data.players.o;

        setupPanel.classList.add('hidden');
        gamePanel.classList.remove('hidden');

        // 显示thinking面板（如果启用）
        if (enableThinking) {
            thinkingPanel.classList.remove('hidden');
            thinkingHistory.innerHTML = '<div class="thinking-empty">等待AI思考...</div>';
        } else {
            thinkingPanel.classList.add('hidden');
        }

        // 显示对应棋盘
        showBoard(currentGameType);
        resetBoards();
        updateGameState(data.state);

        // AI vs AI模式：显示自动对战按钮
        if (currentMode === 'ai_vs_ai') {
            autoPlayBtn.classList.remove('hidden');
        } else {
            isHumanTurn = (humanSide === 'X');
            if (!isHumanTurn) {
                requestAIMove();
            }
        }

    } catch (error) {
        console.error('开始游戏失败:', error);
        alert('开始游戏失败，请检查网络连接');
    }
}

// 显示对应棋盘
function showBoard(gameType) {
    tictactoeBoard.classList.add('hidden');
    tictactoe3dBoard.classList.add('hidden');

    if (gameType === 'tictactoe') {
        tictactoeBoard.classList.remove('hidden');
    } else if (gameType === 'tictactoe3d') {
        tictactoe3dBoard.classList.remove('hidden');
    }
}

// 人类落子
async function humanMove(position) {
    isHumanTurn = false;

    // 立即在界面上显示人类落子
    previewMove(position);

    try {
        const response = await fetch('/api/make_move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSessionId, move: position })
        });

        const data = await response.json();
        if (data.error) {
            // 落子失败，撤销预览
            undoPreview(position);
            alert(data.error);
            isHumanTurn = true;
            return;
        }

        // 更新为服务器确认的状态
        updateBoard(data.state);

        // 更新thinking历史（如果后端已处理AI落子）
        if (data.thinking_history) {
            updateThinkingHistory(data.thinking_history);
        }

        if (data.state.is_game_over) {
            showGameResult(data.state);
        } else {
            // AI已在后端处理落子，现在轮到人类
            isHumanTurn = true;
        }

    } catch (error) {
        console.error('落子失败:', error);
        undoPreview(position);
        isHumanTurn = true;
    }
}

// 预览落子（立即显示）
function previewMove(position) {
    if (currentGameType === 'tictactoe') {
        const cell = document.querySelector(`.cell[data-pos="${position}"]`);
        if (cell) {
            const currentPlayer = currentTurnSpan.textContent.charAt(0);
            cell.textContent = currentPlayer;
            cell.classList.add(currentPlayer, 'taken');
        }
    } else if (currentGameType === 'tictactoe3d') {
        const cell = document.querySelector(`.cell-3d[data-pos="${position}"]`);
        if (cell) {
            const currentPlayer = currentTurnSpan.textContent.charAt(0);
            cell.textContent = currentPlayer;
            cell.classList.add(currentPlayer, 'taken');
        }
    }
}

// 撤销预览
function undoPreview(position) {
    if (currentGameType === 'tictactoe') {
        const cell = document.querySelector(`.cell[data-pos="${position}"]`);
        if (cell) {
            cell.textContent = '';
            cell.classList.remove('X', 'O', 'taken');
        }
    } else if (currentGameType === 'tictactoe3d') {
        const cell = document.querySelector(`.cell-3d[data-pos="${position}"]`);
        if (cell) {
            cell.textContent = '';
            cell.classList.remove('X', 'O', 'taken');
        }
    }
}

// 请求AI落子
async function requestAIMove() {
    aiStatusDiv.classList.remove('hidden');

    try {
        const response = await fetch('/api/ai_move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSessionId })
        });

        const data = await response.json();
        aiStatusDiv.classList.add('hidden');

        updateBoard(data.state);

        // 更新thinking历史
        if (data.thinking_history) {
            updateThinkingHistory(data.thinking_history);
        }

        if (data.state.is_game_over) {
            showGameResult(data.state);
        } else {
            if (currentMode === 'human_vs_ai') {
                isHumanTurn = true;
            }
        }

    } catch (error) {
        console.error('AI落子失败:', error);
        aiStatusDiv.classList.add('hidden');
    }
}

// 自动对战 (AI vs AI)
async function autoPlay() {
    autoPlayBtn.disabled = true;
    aiStatusDiv.classList.remove('hidden');

    try {
        const response = await fetch('/api/auto_play', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                max_moves: 50
            })
        });

        const data = await response.json();
        aiStatusDiv.classList.add('hidden');
        autoPlayBtn.disabled = false;

        updateBoard(data.state);

        if (data.state.is_game_over) {
            showGameResult(data.state);
        }

        console.log('对战过程:', data.moves_log);

    } catch (error) {
        console.error('自动对战失败:', error);
        aiStatusDiv.classList.add('hidden');
        autoPlayBtn.disabled = false;
    }
}

// 更新棋盘显示
function updateBoard(state) {
    // 更新回合显示
    if (state.current_player) {
        currentTurnSpan.textContent = state.current_player + '方回合';
    }

    if (currentGameType === 'tictactoe') {
        update2DBoard(state.board);
    } else if (currentGameType === 'tictactoe3d') {
        update3DBoard(state.layers);
    }
}

// 更新二维棋盘
function update2DBoard(board) {
    cells2D.forEach(cell => {
        const pos = cell.dataset.pos;
        const symbol = board[pos];

        cell.textContent = symbol === ' ' ? '' : symbol;
        cell.classList.remove('X', 'O', 'taken', 'winning');

        if (symbol !== ' ') {
            cell.classList.add(symbol, 'taken');
        }
    });
}

// 更新三维棋盘
function update3DBoard(layers) {
    layers.forEach(layerData => {
        layerData.cells.forEach((row) => {
            row.forEach((cellData) => {
                const pos = cellData.position;
                const cell = document.querySelector(`.cell-3d[data-pos="${pos}"]`);

                if (cell) {
                    cell.textContent = cellData.value === ' ' ? '' : cellData.value;
                    cell.classList.remove('X', 'O', 'taken', 'blocked', 'winning');

                    if (cellData.value !== ' ') {
                        cell.classList.add(cellData.value, 'taken');
                    } else if (!cellData.has_support) {
                        cell.classList.add('blocked');
                    }
                }
            });
        });
    });
}

// 重置棋盘
function resetBoards() {
    cells2D.forEach(cell => {
        cell.textContent = '';
        cell.classList.remove('X', 'O', 'taken', 'winning');
    });

    cells3D.forEach(cell => {
        cell.textContent = '';
        cell.classList.remove('X', 'O', 'taken', 'blocked', 'winning');
    });

    gameStatusSpan.textContent = '';
}

// 更新游戏状态
function updateGameState(state) {
    updateBoard(state);
}

// 显示游戏结果
function showGameResult(state) {
    if (state.is_draw) {
        gameStatusSpan.textContent = '平局！';
    } else {
        const winnerName = state.winner === 'X' ? xNameSpan.textContent : oNameSpan.textContent;
        gameStatusSpan.textContent = `${winnerName} (${state.winner}) 获胜！`;
    }

    // 高亮获胜格子（如果有）
    if (state.winning_positions) {
        state.winning_positions.forEach(pos => {
            if (currentGameType === 'tictactoe') {
                document.querySelector(`.cell[data-pos="${pos}"]`)?.classList.add('winning');
            } else {
                document.querySelector(`.cell-3d[data-pos="${pos}"]`)?.classList.add('winning');
            }
        });
    }

    loadLeaderboard();
}

// 加载排行榜
async function loadLeaderboard() {
    try {
        const response = await fetch('/api/leaderboard');
        const data = await response.json();

        leaderboardBody.innerHTML = '';

        if (data.length === 0) {
            leaderboardBody.innerHTML = '<tr><td colspan="6">暂无记录</td></tr>';
            return;
        }

        data.forEach((entry, index) => {
            const row = document.createElement('tr');
            row.className = 'leaderboard-row';
            row.dataset.name = entry.name;
            row.innerHTML = `
                <td>${index + 1}</td>
                <td class="player-name-cell">
                    <span class="player-name">${entry.name}</span>
                    <span class="expand-icon">▶</span>
                </td>
                <td>${entry.wins}</td>
                <td>${entry.losses}</td>
                <td>${entry.draws}</td>
                <td>${entry.score}</td>
            `;
            row.addEventListener('click', () => togglePlayerHistory(entry.name, row));
            leaderboardBody.appendChild(row);
        });

    } catch (error) {
        console.error('加载排行榜失败:', error);
    }
}

// 展开/收起玩家历史
async function togglePlayerHistory(name, row) {
    const nextRow = row.nextElementSibling;

    // 如果已经展开，收起
    if (nextRow && nextRow.classList.contains('history-row')) {
        nextRow.remove();
        row.querySelector('.expand-icon').textContent = '▶';
        return;
    }

    // 展开历史
    row.querySelector('.expand-icon').textContent = '▼';

    try {
        const response = await fetch(`/api/player_history/${encodeURIComponent(name)}`);
        const history = await response.json();

        const historyRow = document.createElement('tr');
        historyRow.className = 'history-row';

        if (history.length === 0) {
            historyRow.innerHTML = `<td colspan="6" class="history-content">暂无对局记录</td>`;
        } else {
            const historyHtml = history.map(game => {
                const date = new Date(game.timestamp).toLocaleString('zh-CN', {
                    month: 'numeric',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                const gameTypeLabel = game.game_type === 'tictactoe3d' ? '3D' : '2D';
                const resultClass = game.result === 'win' ? 'result-win' : (game.result === 'lose' ? 'result-lose' : 'result-draw');
                const resultText = game.result === 'win' ? '胜' : (game.result === 'lose' ? '负' : '平');

                return `<div class="history-item">
                    <span class="history-date">${date}</span>
                    <span class="history-game">${gameTypeLabel}</span>
                    <span class="history-vs">vs</span>
                    <span class="history-opponent">${game.opponent}</span>
                    <span class="history-result ${resultClass}">${resultText}</span>
                </div>`;
            }).join('');

            historyRow.innerHTML = `<td colspan="6" class="history-content">${historyHtml}</td>`;
        }

        row.after(historyRow);

    } catch (error) {
        console.error('加载历史失败:', error);
    }
}

// 更新Thinking历史
function updateThinkingHistory(history) {
    if (!history || history.length === 0) {
        thinkingHistory.innerHTML = '<div class="thinking-empty">等待AI思考...</div>';
        return;
    }

    const html = history.map(item => {
        const thinkingContent = item.thinking || '(无思考内容)';
        const moveStr = currentGameType === 'tictactoe' ? item.move : format3DMove(item.move);

        return `<div class="thinking-item">
            <div class="thinking-header">
                <span class="thinking-player ${item.player}">${item.player} (${item.model})</span>
                <span class="thinking-move">落子: ${moveStr}</span>
            </div>
            <div class="thinking-content">${escapeHtml(thinkingContent)}</div>
        </div>`;
    }).join('');

    thinkingHistory.innerHTML = html;
}

// 格式化3D位置
function format3DMove(move) {
    if (!move) return 'unknown';
    if (typeof move === 'string') return move;
    if (Array.isArray(move) || (move && move.length === 3)) {
        return `L${move[0]}-R${move[1]}-C${move[2]}`;
    }
    return String(move);
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}