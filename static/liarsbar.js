/**
 * 骗子酒馆 (Liar's Bar) 前端逻辑
 * 心理博弈卡牌游戏
 */

// ==================== 状态管理 ====================

let liarsbarState = {
    sessionId: null,
    phase: 'play',           // 'play' | 'challenge'
    myPlayer: null,          // 'X' 或 'O'
    myHand: [],              // 我的手牌
    targetCard: null,        // 目标牌
    reputation: {X: 3, O: 3},// 信誉值
    dialogueHistory: [],     // 对话历史
    currentClaim: null,      // 当前声明
    roundNumber: 0,
    isMyTurn: false,
    selectedCards: [],       // 已选择的卡牌索引
    enableThinking: true,
    thinkingHistory: []
};

// ==================== 初始化 ====================

function initLiarsbarGame(sessionId, player, enableThinking = true) {
    liarsbarState.sessionId = sessionId;
    liarsbarState.myPlayer = player;
    liarsbarState.enableThinking = enableThinking;
    liarsbarState.selectedCards = [];

    // 获取初始状态
    fetchLiarsbarState();

    // 显示游戏面板
    showLiarsbarPanel();
}

function showLiarsbarPanel() {
    document.getElementById('tictactoe-panel').classList.add('hidden');
    document.getElementById('liarsbar-panel').classList.remove('hidden');
}

// ==================== API 调用 ====================

async function fetchLiarsbarState() {
    const response = await fetch(`/api/liarsbar/get_hand/${liarsbarState.sessionId}/${liarsbarState.myPlayer}`);
    const data = await response.json();

    if (data.error) {
        console.error('获取状态失败:', data.error);
        return;
    }

    updateLiarsbarState(data);
    renderLiarsbarUI();
}

function updateLiarsbarState(data) {
    liarsbarState.phase = data.phase;
    liarsbarState.myHand = data.my_hand || [];
    liarsbarState.targetCard = data.target_card;
    liarsbarState.reputation = data.reputation;
    liarsbarState.dialogueHistory = data.dialogue_history || [];
    liarsbarState.currentClaim = data.current_claim;
    liarsbarState.roundNumber = data.round_number;

    // 判断是否是我的回合
    if (liarsbarState.phase === 'play') {
        liarsbarState.isMyTurn = (data.current_player === liarsbarState.myPlayer);
    } else if (liarsbarState.phase === 'challenge') {
        // 质疑阶段，对手操作
        const claimer = data.current_claim?.player;
        liarsbarState.isMyTurn = (claimer !== liarsbarState.myPlayer);
    }
}

// ==================== UI 渲染 ====================

function renderLiarsbarUI() {
    renderGameInfo();
    renderReputation();
    renderMyHand();
    renderDialogueHistory();
    renderPhasePanel();
    renderThinkingHistory();
}

function renderGameInfo() {
    const infoEl = document.getElementById('liarsbar-info');
    if (!infoEl) return;

    infoEl.innerHTML = `
        <div class="game-info-item">
            <span class="label">目标牌:</span>
            <span class="target-card">${liarsbarState.targetCard}</span>
        </div>
        <div class="game-info-item">
            <span class="label">回合:</span>
            <span class="round-number">${liarsbarState.roundNumber}/20</span>
        </div>
        <div class="game-info-item">
            <span class="label">你是:</span>
            <span class="player-badge ${liarsbarState.myPlayer}">${liarsbarState.myPlayer}</span>
        </div>
    `;
}

function renderReputation() {
    const repEl = document.getElementById('reputation-display');
    if (!repEl) return;

    const maxRep = 3;
    repEl.innerHTML = `
        <div class="reputation-item player-x">
            <span class="player-label">X</span>
            <div class="reputation-bar">
                ${Array(maxRep).fill(0).map((_, i) =>
                    `<span class="rep-point ${i < liarsbarState.reputation.X ? 'active' : ''}">●</span>`
                ).join('')}
            </div>
        </div>
        <div class="reputation-item player-o">
            <span class="player-label">O</span>
            <div class="reputation-bar">
                ${Array(maxRep).fill(0).map((_, i) =>
                    `<span class="rep-point ${i < liarsbarState.reputation.O ? 'active' : ''}">●</span>`
                ).join('')}
            </div>
        </div>
    `;
}

function renderMyHand() {
    const handEl = document.getElementById('my-hand');
    if (!handEl) return;

    handEl.innerHTML = liarsbarState.myHand.map((card, index) => `
        <div class="card-item ${liarsbarState.selectedCards.includes(index) ? 'selected' : ''}
                    ${card === 'Joker' ? 'joker' : ''}
                    ${card === liarsbarState.targetCard ? 'target' : ''}"
             data-index="${index}"
             onclick="toggleCardSelection(${index})">
            <span class="card-type">${card}</span>
            ${card === liarsbarState.targetCard ? '<span class="card-badge">目标</span>' : ''}
            ${card === 'Joker' ? '<span class="card-badge joker-badge">万能</span>' : ''}
        </div>
    `).join('');

    // 更新选中数量显示
    const countEl = document.getElementById('selected-count');
    if (countEl) {
        countEl.textContent = `已选择 ${liarsbarState.selectedCards.length} 张 (最多3张)`;
    }
}

function toggleCardSelection(index) {
    if (liarsbarState.phase !== 'play' || !liarsbarState.isMyTurn) return;

    const idx = liarsbarState.selectedCards.indexOf(index);

    if (idx > -1) {
        // 取消选择
        liarsbarState.selectedCards.splice(idx, 1);
    } else if (liarsbarState.selectedCards.length < 3) {
        // 添加选择（最多3张）
        liarsbarState.selectedCards.push(index);
    }

    renderMyHand();
}

function renderDialogueHistory() {
    const dialogueEl = document.getElementById('dialogue-history');
    if (!dialogueEl) return;

    if (liarsbarState.dialogueHistory.length === 0) {
        dialogueEl.innerHTML = '<div class="no-dialogue">暂无对话</div>';
        return;
    }

    dialogueEl.innerHTML = liarsbarState.dialogueHistory.map(entry => `
        <div class="dialogue-entry ${entry.player}">
            <span class="dialogue-player">${entry.player}</span>
            <span class="dialogue-text">"${entry.statement}"</span>
        </div>
    `).join('');

    // 滚动到最新
    dialogueEl.scrollTop = dialogueEl.scrollHeight;
}

function renderPhasePanel() {
    const playPanel = document.getElementById('play-phase-panel');
    const challengePanel = document.getElementById('challenge-phase-panel');

    if (liarsbarState.phase === 'play') {
        playPanel?.classList.remove('hidden');
        challengePanel?.classList.add('hidden');

        // 更新出牌按钮状态
        const playBtn = document.getElementById('play-cards-btn');
        if (playBtn) {
            playBtn.disabled = !liarsbarState.isMyTurn || liarsbarState.selectedCards.length === 0;
        }
    } else if (liarsbarState.phase === 'challenge') {
        playPanel?.classList.add('hidden');
        challengePanel?.classList.remove('hidden');

        // 显示当前声明信息
        renderClaimInfo();
    }
}

function renderClaimInfo() {
    const claimEl = document.getElementById('claim-info');
    if (!claimEl || !liarsbarState.currentClaim) return;

    const claim = liarsbarState.currentClaim;
    claimEl.innerHTML = `
        <div class="claim-statement">
            <span class="claimer ${claim.player}">${claim.player}</span> 说：
            "${claim.statement || '(未发言)'}"
        </div>
        <div class="claim-count">
            声明打出 <strong>${claim.claimed_count}</strong> 张 <strong>${liarsbarState.targetCard}</strong>
        </div>
    `;

    // 更新质疑按钮状态
    const believeBtn = document.getElementById('believe-btn');
    const challengeBtn = document.getElementById('challenge-btn');

    if (believeBtn && challengeBtn) {
        believeBtn.disabled = !liarsbarState.isMyTurn;
        challengeBtn.disabled = !liarsbarState.isMyTurn;
    }
}

function renderThinkingHistory() {
    const thinkingEl = document.getElementById('thinking-history');
    if (!thinkingEl) return;

    if (liarsbarState.thinkingHistory.length === 0) {
        thinkingEl.innerHTML = '<div class="no-thinking">暂无思考记录</div>';
        return;
    }

    thinkingEl.innerHTML = liarsbarState.thinkingHistory.map(entry => `
        <div class="thinking-entry ${entry.player}">
            <div class="thinking-header">
                <span class="thinking-player">${entry.player}</span>
                <span class="thinking-model">${entry.model}</span>
                <span class="thinking-phase">${entry.phase === 'play' ? '出牌' : '质疑'}</span>
            </div>
            <div class="thinking-content">
                ${entry.thinking || '(无思考内容)'}
            </div>
            ${entry.phase === 'play' ? `
                <div class="thinking-action">
                    声明: ${entry.claimed} 张 | 发言: "${entry.statement?.substring(0, 50) || ''}"
                </div>
            ` : `
                <div class="thinking-action">
                    决策: ${entry.decision}
                </div>
            `}
        </div>
    `).join('');
}

// ==================== 用户操作 ====================

async function submitStatement() {
    const inputEl = document.getElementById('statement-input');
    const statement = inputEl?.value.trim();

    if (!statement) {
        alert('请输入发言内容');
        return;
    }

    const response = await fetch('/api/liarsbar/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: liarsbarState.sessionId,
            player: liarsbarState.myPlayer,
            statement: statement
        })
    });

    const data = await response.json();
    if (data.error) {
        alert('发言失败: ' + data.error);
        return;
    }

    // 清空输入
    inputEl.value = '';

    // 更新状态
    updateLiarsbarState(data.state);
    renderDialogueHistory();
}

async function playCards() {
    if (liarsbarState.selectedCards.length === 0) {
        alert('请至少选择1张牌');
        return;
    }

    if (liarsbarState.selectedCards.length > 3) {
        alert('最多只能选择3张牌');
        return;
    }

    // 获取声明数量
    const claimedInput = document.getElementById('claimed-count-input');
    const claimedCount = parseInt(claimedInput?.value || liarsbarState.selectedCards.length);

    if (claimedCount < 0 || claimedCount > liarsbarState.selectedCards.length) {
        alert('声明数量必须在 0 到 ' + liarsbarState.selectedCards.length + ' 之间');
        return;
    }

    // 获取发言（如果有）
    const statementInput = document.getElementById('statement-input');
    const statement = statementInput?.value.trim();

    // 如果有发言，先发送
    if (statement) {
        await submitStatement();
    }

    const response = await fetch('/api/liarsbar/play_cards', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: liarsbarState.sessionId,
            player: liarsbarState.myPlayer,
            cards: liarsbarState.selectedCards,
            claimed_count: claimedCount
        })
    });

    const data = await response.json();
    if (data.error) {
        alert('出牌失败: ' + data.error);
        return;
    }

    // 清空选择
    liarsbarState.selectedCards = [];

    // 更新状态
    updateLiarsbarState(data.state);

    // 如果有AI响应，更新思考历史
    if (data.ai_response?.thinking) {
        liarsbarState.thinkingHistory.push({
            player: data.ai_response.ai_decision ? 'O' : 'X',
            model: 'AI',
            phase: 'challenge',
            decision: data.ai_response.ai_decision,
            thinking: data.ai_response.thinking
        });
    }

    renderLiarsbarUI();

    // 检查游戏结束
    if (data.game_over) {
        showGameOver(data.winner, data.stats);
    }
}

async function respondToClaim(action) {
    // action: 'believe' 或 'challenge'

    const response = await fetch('/api/liarsbar/respond', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: liarsbarState.sessionId,
            player: liarsbarState.myPlayer,
            action: action
        })
    });

    const data = await response.json();
    if (data.error) {
        alert('响应失败: ' + data.error);
        return;
    }

    // 显示开牌结果（如果质疑）
    if (data.reveal) {
        showRevealModal(data.reveal);
    }

    // 更新状态
    updateLiarsbarState(data.state);

    // 更新思考历史
    if (data.ai_play?.thinking) {
        liarsbarState.thinkingHistory.push({
            player: data.ai_play.player || 'AI',
            model: 'AI',
            phase: 'play',
            thinking: data.ai_play.thinking,
            statement: data.ai_play.ai_statement,
            claimed: data.ai_play.ai_claimed
        });
    }

    renderLiarsbarUI();

    // 检查游戏结束
    if (data.game_over) {
        showGameOver(data.winner, data.stats);
    }
}

// ==================== 弹窗 ====================

function showRevealModal(reveal) {
    const modal = document.getElementById('reveal-modal');
    const content = document.getElementById('reveal-content');

    if (!modal || !content) return;

    content.innerHTML = `
        <div class="reveal-cards">
            <span class="reveal-label">实际打出的牌:</span>
            <div class="reveal-card-list">
                ${reveal.played_cards.map(card => `
                    <span class="reveal-card ${card === liarsbarState.targetCard ? 'target' : ''} ${card === 'Joker' ? 'joker' : ''}">${card}</span>
                `).join('')}
            </div>
        </div>
        <div class="reveal-result ${reveal.was_lying ? 'lie' : 'truth'}">
            <span class="reveal-status">${reveal.was_lying ? '说谎！' : '诚实'}</span>
            <span class="reveal-detail">
                声明: ${reveal.claimed_count} 张 ${liarsbarState.targetCard}
                | 实际有效: ${reveal.actual_valid} 张
            </span>
        </div>
        <div class="reputation-change">
            ${reveal.reputation_change.player} 信誉值 ${reveal.reputation_change.change > 0 ? '+' : ''}${reveal.reputation_change.change}
        </div>
    `;

    modal.classList.remove('hidden');

    // 3秒后自动关闭
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 3000);
}

function showGameOver(winner, stats) {
    const modal = document.getElementById('game-over-modal');
    const content = document.getElementById('game-over-content');

    if (!modal || !content) return;

    const isWin = winner === liarsbarState.myPlayer;

    content.innerHTML = `
        <div class="game-over-title ${isWin ? 'win' : 'lose'}">
            ${isWin ? '你赢了！' : '你输了...'}
        </div>
        <div class="game-over-winner">
            获胜者: ${winner || '平局'}
        </div>
        ${stats ? `
            <div class="game-stats">
                <h4>统计数据</h4>
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-label">回合数</span>
                        <span class="stat-value">${stats.rounds_played}</span>
                    </div>
                </div>
            </div>
        ` : ''}
    `;

    modal.classList.remove('hidden');
}

function closeRevealModal() {
    document.getElementById('reveal-modal')?.classList.add('hidden');
}

function closeGameOverModal() {
    document.getElementById('game-over-modal')?.classList.add('hidden');
}

// ==================== 工具函数 ====================

function getCardClass(card) {
    if (card === 'Joker') return 'joker-card';
    if (card === liarsbarState.targetCard) return 'target-card';
    return 'normal-card';
}

// 导出函数供全局使用
window.initLiarsbarGame = initLiarsbarGame;
window.toggleCardSelection = toggleCardSelection;
window.submitStatement = submitStatement;
window.playCards = playCards;
window.respondToClaim = respondToClaim;
window.closeRevealModal = closeRevealModal;
window.closeGameOverModal = closeGameOverModal;