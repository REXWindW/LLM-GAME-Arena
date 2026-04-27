"""
骗子酒馆 (Liar's Bar) 游戏核心逻辑
心理博弈卡牌游戏：通过欺骗与质疑击败对手
"""
import random
import re
from typing import List, Dict, Optional, Any
from games.base import BaseGame


class LiarBarGame(BaseGame):
    """骗子酒馆游戏类"""

    game_id = "liarsbar"
    game_name = "骗子酒馆"
    game_description = "心理博弈卡牌游戏，通过欺骗与质疑击败对手"

    # 牌型定义
    CARD_TYPES = ['King', 'Queen', 'Ace', 'Joker']
    TARGET_CARDS = ['King', 'Queen', 'Ace']  # 目标牌候选（不含Joker）

    # 牌组配置
    DECK_CONFIG = {
        'King': 6,
        'Queen': 6,
        'Ace': 6,
        'Joker': 2
    }

    MAX_ROUNDS = 20
    INITIAL_HAND_SIZE = 5
    INITIAL_REPUTATION = 3

    def __init__(self):
        self.reset()

    def reset(self):
        """重置游戏状态"""
        # 玩家手牌
        self.hands: Dict[str, List[str]] = {'X': [], 'O': []}

        # 信誉值
        self.reputation: Dict[str, int] = {
            'X': self.INITIAL_REPUTATION,
            'O': self.INITIAL_REPUTATION
        }

        # 当前目标牌
        self.target_card: str = random.choice(self.TARGET_CARDS)

        # 回合阶段: 'play' | 'challenge'
        self.phase: str = 'play'

        # 当前回合数据
        self.current_round: Dict[str, Any] = {
            'player': 'X',           # 出牌者
            'statement': None,       # 发言内容
            'played_cards': [],      # 实际打出的牌（隐藏）
            'card_indices': [],      # 选择的卡牌索引
            'claimed_count': 0,      # 声明的目标牌数量
            'challenged': False,     # 是否被质疑
            'challenge_result': None # 质疑结果
        }

        # 对话历史
        self.dialogue_history: List[Dict[str, str]] = []

        # 最近的开牌结果（用于前端显示）
        self.last_reveal_result: Optional[Dict[str, Any]] = None

        # 游戏状态
        self.current_player: str = 'X'
        self.winner: Optional[str] = None
        self.is_draw: bool = False
        self.round_number: int = 0

        # 统计数据
        self.stats: Dict[str, Dict[str, int]] = {
            'X': {
                'lies_told': 0,          # 说谎次数
                'successful_lies': 0,    # 成功欺骗次数
                'challenges_made': 0,    # 质疑次数
                'correct_challenges': 0, # 正确质疑次数
                'times_caught': 0,       # 被抓说谎次数
                'times_fooled': 0,       # 被骗次数
                'total_plays': 0         # 总出牌次数
            },
            'O': {
                'lies_told': 0,
                'successful_lies': 0,
                'challenges_made': 0,
                'correct_challenges': 0,
                'times_caught': 0,
                'times_fooled': 0,
                'total_plays': 0
            }
        }

        # 发牌
        self._deal_cards()

    def _deal_cards(self):
        """发牌"""
        # 构建牌组
        deck = []
        for card_type, count in self.DECK_CONFIG.items():
            deck.extend([card_type] * count)

        # 洗牌
        random.shuffle(deck)

        # 发牌（每人5张）
        self.hands['X'] = deck[:self.INITIAL_HAND_SIZE]
        self.hands['O'] = deck[self.INITIAL_HAND_SIZE:self.INITIAL_HAND_SIZE * 2]

    # ==================== BaseGame 必须实现的接口 ====================

    def get_board_visual(self) -> str:
        """返回棋盘可视化（用于AI prompt）"""
        visual = f"目标牌: {self.target_card}\n"
        visual += f"回合: {self.round_number}/{self.MAX_ROUNDS}\n"
        visual += f"X 信誉: {self.reputation['X']}/3, O 信誉: {self.reputation['O']}/3\n"
        visual += f"X 手牌数: {len(self.hands['X'])}, O 手牌数: {len(self.hands['O'])}\n"

        if self.dialogue_history:
            visual += "\n对话历史:\n"
            for entry in self.dialogue_history[-5:]:  # 最近5条
                visual += f"  {entry['player']}: \"{entry['statement']}\"\n"

        return visual

    def get_available_moves(self) -> List[Any]:
        """获取所有合法操作（根据当前阶段）"""
        if self.phase == 'play':
            # 出牌阶段：返回可选卡牌索引
            player = self.current_round['player']
            return list(range(len(self.hands[player])))
        elif self.phase == 'challenge':
            # 质疑阶段：返回可用操作
            return ['believe', 'challenge']
        return []

    def is_valid_move(self, move: Any) -> bool:
        """检查操作是否有效"""
        if self.phase == 'play':
            # 检查卡牌索引是否有效
            if isinstance(move, list):
                hand = self.hands[self.current_round['player']]
                return all(0 <= i < len(hand) for i in move)
            return False
        elif self.phase == 'challenge':
            return move in ['believe', 'challenge']
        return False

    def get_invalid_reason(self, move: Any) -> str:
        """获取无效操作原因"""
        if self.phase == 'play':
            hand = self.hands[self.current_round['player']]
            if isinstance(move, list):
                for i in move:
                    if i < 0 or i >= len(hand):
                        return f"卡牌索引 {i} 超出范围（0-{len(hand)-1})"
            return "无效的卡牌选择"
        elif self.phase == 'challenge':
            return "只能选择 'believe' 或 'challenge'"
        return "当前阶段不允许此操作"

    def make_move(self, move: Any, player: str) -> bool:
        """执行操作（简化版，用于兼容BaseGame）"""
        # Liar's Bar 的操作较为复杂，建议使用专用方法
        # 此方法用于 AI vs AI 自动对战时调用
        if self.phase == 'play' and player == self.current_round['player']:
            # 出牌阶段
            if isinstance(move, dict):
                card_indices = move.get('cards', [])
                claimed = move.get('claimed', len(card_indices))
                statement = move.get('statement', '')

                self.make_statement(player, statement)
                return self.play_cards(player, card_indices, claimed)
        elif self.phase == 'challenge':
            # 质疑阶段
            opponent = 'O' if self.current_round['player'] == 'X' else 'X'
            if player == opponent:
                return self.respond(player, move)

        return False

    def is_game_over(self) -> bool:
        """游戏是否结束"""
        # 信誉值归零
        if self.reputation['X'] <= 0 or self.reputation['O'] <= 0:
            self.winner = 'X' if self.reputation['O'] <= 0 else 'O'
            return True

        # 手牌耗尽
        if len(self.hands['X']) == 0:
            self.winner = 'X'
            return True
        if len(self.hands['O']) == 0:
            self.winner = 'O'
            return True

        # 最大回合数
        if self.round_number >= self.MAX_ROUNDS:
            self._determine_winner_by_score()
            return True

        return False

    def _determine_winner_by_score(self):
        """根据分数判定胜负"""
        if self.reputation['X'] > self.reputation['O']:
            self.winner = 'X'
        elif self.reputation['O'] > self.reputation['X']:
            self.winner = 'O'
        elif len(self.hands['X']) < len(self.hands['O']):
            self.winner = 'X'
        elif len(self.hands['O']) < len(self.hands['X']):
            self.winner = 'O'
        else:
            self.is_draw = True
            self.winner = None

    def get_winner(self) -> Optional[str]:
        """获取获胜者"""
        return self.winner

    def get_current_player(self) -> str:
        """获取当前玩家（出牌者）"""
        if self.phase == 'play':
            return self.current_round['player']
        elif self.phase == 'challenge':
            # 质疑阶段，当前操作者是对手
            return 'O' if self.current_round['player'] == 'X' else 'X'
        return self.current_round['player']

    def get_frontend_state(self, for_player: Optional[str] = None) -> Dict[str, Any]:
        """
        获取前端渲染状态

        Args:
            for_player: 指定玩家可见完整信息，None 表示公开信息
        """
        state = {
            'phase': self.phase,
            'current_player': self.current_round['player'],
            'target_card': self.target_card,
            'round_number': self.round_number,
            'is_game_over': self.is_game_over(),
            'winner': self.winner,
            'is_draw': self.is_draw,

            # 双方公开信息
            'reputation': self.reputation.copy(),
            'cards_remaining': {
                'X': len(self.hands['X']),
                'O': len(self.hands['O'])
            },

            # 对话历史
            'dialogue_history': self.dialogue_history.copy(),

            # 当前回合公开信息
            'current_claim': {
                'player': self.current_round['player'],
                'claimed_count': self.current_round['claimed_count'],
                'statement': self.current_round['statement']
            }
        }

        # 如果指定了玩家，返回其私有信息
        if for_player and for_player in self.hands:
            state['my_hand'] = self.hands[for_player].copy()
            state['my_stats'] = self.stats[for_player].copy()

        # 质疑结果（如果已开牌）
        if self.current_round.get('challenge_result'):
            state['reveal'] = self.current_round['challenge_result']
        elif self.last_reveal_result:
            state['reveal'] = self.last_reveal_result

        return state

    # ==================== Liar's Bar 专用方法 ====================

    def get_phase(self) -> str:
        """获取当前阶段"""
        return self.phase

    def get_available_actions(self) -> List[str]:
        """根据当前阶段返回可用操作"""
        if self.phase == 'play':
            return ['speak', 'select_cards']
        elif self.phase == 'challenge':
            return ['believe', 'challenge']
        return []

    def make_statement(self, player: str, statement: str) -> bool:
        """
        玩家发言

        Args:
            player: 玩家标识 ('X' 或 'O')
            statement: 发言内容

        Returns:
            是否成功
        """
        if self.phase != 'play':
            return False

        if player != self.current_round['player']:
            return False

        self.current_round['statement'] = statement

        # 记录到对话历史
        self.dialogue_history.append({
            'player': player,
            'statement': statement,
            'round': self.round_number
        })

        return True

    def play_cards(self, player: str, card_indices: List[int], claimed_count: int) -> bool:
        """
        出牌

        Args:
            player: 玩家标识
            card_indices: 选择的卡牌索引列表
            claimed_count: 声明的目标牌数量

        Returns:
            是否成功
        """
        if self.phase != 'play':
            return False

        if player != self.current_round['player']:
            return False

        hand = self.hands[player]

        # 验证索引
        if not all(0 <= i < len(hand) for i in card_indices):
            return False

        # 验证数量（1-3张）
        if len(card_indices) < 1 or len(card_indices) > 3:
            return False

        # 验证声明数量（不能超过实际出牌数）
        if claimed_count > len(card_indices) or claimed_count < 0:
            return False

        # 记录出牌
        played_cards = [hand[i] for i in card_indices]
        self.current_round['played_cards'] = played_cards
        self.current_round['card_indices'] = card_indices
        self.current_round['claimed_count'] = claimed_count

        # 从手牌移除
        for i in sorted(card_indices, reverse=True):
            hand.pop(i)

        # 更新统计
        self.stats[player]['total_plays'] += 1

        # 检查是否说谎
        is_lying = self._check_lying(played_cards)
        if is_lying:
            self.stats[player]['lies_told'] += 1

        # 切换到质疑阶段
        self.phase = 'challenge'

        return True

    def _check_lying(self, played_cards: List[str]) -> bool:
        """检查是否说谎"""
        for card in played_cards:
            if card != self.target_card and card != 'Joker':
                return True
        return False

    def _count_valid_cards(self, played_cards: List[str]) -> int:
        """计算有效目标牌数量"""
        count = 0
        for card in played_cards:
            if card == self.target_card or card == 'Joker':
                count += 1
        return count

    def respond(self, player: str, action: str) -> bool:
        """
        响应出牌（相信或质疑）

        Args:
            player: 响应者
            action: 'believe' 或 'challenge'

        Returns:
            是否成功
        """
        if self.phase != 'challenge':
            return False

        # 只有对手可以响应
        opponent = 'O' if self.current_round['player'] == 'X' else 'X'
        if player != opponent:
            return False

        if action not in ['believe', 'challenge']:
            return False

        # 更新统计
        challenger = player
        claimer = self.current_round['player']

        if action == 'challenge':
            self.stats[challenger]['challenges_made'] += 1

            # 开牌验证
            result = self.reveal_and_resolve()
            self.current_round['challenge_result'] = result
            self.last_reveal_result = result  # 保存结果供前端显示

            if result['was_lying']:
                # 质疑成功
                self.stats[challenger]['correct_challenges'] += 1
                self.stats[claimer]['times_caught'] += 1
            else:
                # 质疑失败
                self.stats[challenger]['times_fooled'] += 1
        else:
            # 选择相信
            # 检查出牌者是否说谎且成功
            was_lying = self._check_lying(self.current_round['played_cards'])
            if was_lying:
                self.stats[claimer]['successful_lies'] += 1
                self.stats[challenger]['times_fooled'] += 1

        # 进入下一回合
        self._next_round()

        return True

    def reveal_and_resolve(self) -> Dict[str, Any]:
        """
        开牌并结算

        Returns:
            质疑结果
        """
        played_cards = self.current_round['played_cards']
        claimed_count = self.current_round['claimed_count']
        claimer = self.current_round['player']
        challenger = 'O' if claimer == 'X' else 'X'

        # 计算实际有效牌数
        actual_valid = self._count_valid_cards(played_cards)

        # 判断是否说谎
        was_lying = self._check_lying(played_cards)

        # 结算信誉值
        if was_lying:
            # 说谎被抓
            self.reputation[claimer] -= 1
            reputation_change = {'player': claimer, 'change': -1}
        else:
            # 质疑失败
            self.reputation[challenger] -= 1
            reputation_change = {'player': challenger, 'change': -1}

        result = {
            'played_cards': played_cards,
            'claimed_count': claimed_count,
            'actual_valid': actual_valid,
            'was_lying': was_lying,
            'reputation_change': reputation_change,
            'winner': challenger if was_lying else claimer
        }

        return result

    def _next_round(self):
        """进入下一回合"""
        self.round_number += 1

        # 切换出牌者
        next_player = 'O' if self.current_round['player'] == 'X' else 'X'

        # 重置回合数据
        self.current_round = {
            'player': next_player,
            'statement': None,
            'played_cards': [],
            'card_indices': [],
            'claimed_count': 0,
            'challenged': False,
            'challenge_result': None
        }

        # 切换到出牌阶段
        self.phase = 'play'
        self.current_player = next_player

    # ==================== LLM Prompt 相关 ====================

    def get_llm_prompt(self, symbol: str, enable_thinking: bool = True) -> str:
        """生成 AI prompt"""
        if self.phase == 'play':
            return self._get_play_phase_prompt(symbol, enable_thinking)
        elif self.phase == 'challenge':
            return self._get_challenge_phase_prompt(symbol, enable_thinking)
        return ""

    def _get_play_phase_prompt(self, symbol: str, enable_thinking: bool) -> str:
        """出牌阶段 prompt"""
        opponent = 'O' if symbol == 'X' else 'X'
        my_hand = self.hands[symbol]
        my_reputation = self.reputation[symbol]
        opp_reputation = self.reputation[opponent]

        # 计算对手历史数据
        opp_stats = self.stats[opponent]
        total_plays = max(1, opp_stats['total_plays'])
        opp_lie_rate = opp_stats['lies_told'] / total_plays if total_plays > 0 else 0

        # 分析手牌中目标牌数量
        target_count = sum(1 for c in my_hand if c == self.target_card or c == 'Joker')

        prompt = f"""You are playing Liar's Bar (骗子酒馆), a card game of deception and trust.

## Game Rules
- Target card this round: **{self.target_card}**
- Joker can be used as any target card
- Each player has 5 cards and 3 reputation points
- Lose all reputation = lose the game
- Successfully play all cards = win the game

## Current State
- Round: {self.round_number}/{self.MAX_ROUNDS}
- Your reputation: {my_reputation}/3
- Opponent reputation: {opp_reputation}/3
- Your hand: {my_hand}
- Cards remaining: You have {len(my_hand)} cards, opponent has unknown cards
- Valid target cards in your hand: {target_count} (including Joker)

## Opponent Behavior Pattern
- Lie rate: {opp_lie_rate:.1%}
- Times caught lying: {opp_stats['times_caught']}
- Successful bluffs: {opp_stats['successful_lies']}

## Your Turn - Play Phase
You need to:
1. Say something to opponent (can be truth, bluff, or misdirection)
2. Select 1-3 cards to play (secretly)
3. Claim how many target cards ({self.target_card}) you played (publicly)

## Previous Dialogue
{self._format_dialogue_history()}
"""

        if enable_thinking:
            prompt += """
First, analyze your strategy in <thinking> tags, then provide your response.

<thinking>
Consider:
- Should you lie? What cards do you actually have vs what you claim?
- What statement would be most convincing?
- How many cards should you play? (1-3)
- What claim is believable?
- Risk assessment based on opponent's challenge history
</thinking>

<statement>
[Your spoken words to opponent - be creative and strategic]
</statement>

<cards>
[Card indices to play, e.g., 0,2 for first and third card - select 1-3 cards]
</cards>

<claimed>
[Number of target cards you claim to have played, 0-3 - can be truth or bluff]
</claimed>"""
        else:
            prompt += """
Provide your response directly:

<statement>
[Your statement]
</statement>

<cards>
[Card indices]
</cards>

<claimed>
[Claimed count]
</claimed>"""

        return prompt

    def _get_challenge_phase_prompt(self, symbol: str, enable_thinking: bool) -> str:
        """质疑阶段 prompt"""
        opponent = 'O' if symbol == 'X' else 'X'
        claimer = self.current_round['player']

        prompt = f"""You are playing Liar's Bar (骗子酒馆). Now you must decide whether to believe or challenge.

## Current Round
- Player {claimer} just played cards and claimed: **{self.current_round['claimed_count']} {self.target_card}(s)**
- Their statement: "{self.current_round['statement']}"

## Game State
- Round: {self.round_number}/{self.MAX_ROUNDS}
- Your reputation: {self.reputation[symbol]}/3
- Opponent reputation: {self.reputation[opponent]}/3
- Your hand: {self.hands[symbol]}
- Cards remaining: You have {len(self.hands[symbol])} cards

## Opponent History (Player {claimer})
- Previous lies detected: {self.stats[claimer]['times_caught']}
- Successful bluffs: {self.stats[claimer]['successful_lies']}
- Total lies told: {self.stats[claimer]['lies_told']}
- Total plays: {self.stats[claimer]['total_plays']}
- Lie rate: {self.stats[claimer]['lies_told'] / max(1, self.stats[claimer]['total_plays']):.1%}

## Decision
- **BELIEVE**: Accept their claim, game continues
- **CHALLENGE**: Reveal their cards
  - If they lied → they lose 1 reputation
  - If they told truth → YOU lose 1 reputation

## Dialogue History
{self._format_dialogue_history()}
"""

        if enable_thinking:
            prompt += """
Analyze and decide:

<thinking>
Consider:
- Is their statement believable? Tone, content, timing
- Does their claim match typical behavior?
- What's the risk vs reward?
- Your reputation situation - can you afford to be wrong?
- Statistical probability based on their history
</thinking>

<decision>
[believe or challenge]
</decision>"""
        else:
            prompt += """
<decision>
[believe or challenge]
</decision>"""

        return prompt

    def _format_dialogue_history(self) -> str:
        """格式化对话历史"""
        if not self.dialogue_history:
            return "(No previous dialogue)"

        formatted = []
        for entry in self.dialogue_history[-5:]:
            formatted.append(f"  {entry['player']}: \"{entry['statement']}\"")

        return "\n".join(formatted)

    def parse_llm_response(self, response: str) -> Any:
        """解析 AI 响应"""
        if self.phase == 'play':
            return self._parse_play_response(response)
        elif self.phase == 'challenge':
            return self._parse_challenge_response(response)
        return None

    def _parse_play_response(self, response: str) -> Dict[str, Any]:
        """解析出牌阶段响应"""
        result = {
            'statement': '',
            'cards': [],
            'claimed': 1
        }

        # 提取 statement
        match = re.search(r'<statement>(.*?)</statement>', response, re.DOTALL)
        if match:
            result['statement'] = match.group(1).strip()
        else:
            # Fallback: 尝试提取第一句话
            lines = response.strip().split('\n')
            for line in lines:
                if line and not line.startswith('<') and len(line) > 10:
                    result['statement'] = line[:100]  # 截取前100字符
                    break

        # 提取 cards
        match = re.search(r'<cards>(.*?)</cards>', response, re.DOTALL)
        if match:
            cards_str = match.group(1).strip()
            numbers = re.findall(r'\d+', cards_str)
            result['cards'] = [int(n) for n in numbers if int(n) < len(self.hands[self.current_round['player']])]

        # 提取 claimed
        match = re.search(r'<claimed>(.*?)</claimed>', response, re.DOTALL)
        if match:
            claimed_str = match.group(1).strip()
            numbers = re.findall(r'\d+', claimed_str)
            if numbers:
                result['claimed'] = int(numbers[0])

        # Fallback: 如果没有提取到卡牌，随机选择1-3张
        if not result['cards']:
            hand_size = len(self.hands[self.current_round['player']])
            num_cards = min(3, max(1, hand_size))
            result['cards'] = random.sample(range(hand_size), min(num_cards, hand_size))

        # 确保 claimed 在合理范围
        if result['claimed'] > len(result['cards']):
            result['claimed'] = len(result['cards'])
        if result['claimed'] < 0:
            result['claimed'] = 1

        return result

    def _parse_challenge_response(self, response: str) -> str:
        """解析质疑阶段响应"""
        match = re.search(r'<decision>(.*?)</decision>', response, re.DOTALL)
        if match:
            decision = match.group(1).strip().lower()
            if 'challenge' in decision:
                return 'challenge'
            elif 'believe' in decision:
                return 'believe'

        # Fallback: 根据关键词判断
        response_lower = response.lower()
        if 'challenge' in response_lower or '质疑' in response_lower:
            return 'challenge'

        return 'believe'

    def extract_thinking(self, response: str) -> str:
        """从响应中提取 thinking 内容"""
        match = re.search(r'<thinking>(.*?)</thinking>', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def get_illegal_move_prompt(self, symbol: str, attempted_move: Any, reason: str) -> str:
        """生成非法操作重试 prompt"""
        if self.phase == 'play':
            return f"""Your previous play was invalid: {reason}

Please try again. Your hand: {self.hands[symbol]}
Valid indices: 0 to {len(self.hands[symbol])-1}
You must select 1-3 cards.

<cards>
[Valid card indices]
</cards>

<claimed>
[Number of target cards claimed, 0-{len(self.hands[symbol])}]
</claimed>"""
        elif self.phase == 'challenge':
            return f"""Invalid decision. You must choose 'believe' or 'challenge'.

<decision>
[believe or challenge]
</decision>"""
        return ""

    def get_random_valid_move(self) -> Any:
        """随机选择一个合法操作"""
        if self.phase == 'play':
            hand_size = len(self.hands[self.current_round['player']])
            if hand_size == 0:
                return {'cards': [], 'claimed': 0, 'statement': 'I have no cards left.'}

            num_cards = min(3, max(1, hand_size))
            cards = random.sample(range(hand_size), num_cards)
            return {
                'cards': cards,
                'claimed': len(cards),  # 默认诚实声明
                'statement': f"I'm playing {num_cards} cards this round."
            }
        elif self.phase == 'challenge':
            return random.choice(['believe', 'challenge'])
        return None

    # ==================== 统计相关 ====================

    def get_game_stats(self) -> Dict[str, Any]:
        """获取游戏统计数据"""
        return {
            'rounds_played': self.round_number,
            'player_stats': self.stats.copy(),
            'dialogue_count': len(self.dialogue_history)
        }

    def calculate_advanced_stats(self, player: str) -> Dict[str, float]:
        """计算高级统计指标"""
        stats = self.stats[player]
        total_plays = max(1, stats['total_plays'])
        total_lies = stats['lies_told']
        total_challenges = stats['challenges_made']

        return {
            'lie_rate': total_lies / total_plays if total_plays > 0 else 0,
            'deception_success_rate': stats['successful_lies'] / max(1, total_lies),
            'challenge_accuracy': stats['correct_challenges'] / max(1, total_challenges),
            'trust_rate': (total_plays - total_challenges) / max(1, total_plays),
            'caught_rate': stats['times_caught'] / max(1, total_lies),
            'fooled_rate': stats['times_fooled'] / max(1, total_plays)
        }