"""
骗子酒馆统计计算模块
提供游戏结束后的详细统计分析
"""
from typing import Dict, Any, List


class LiarsBarStats:
    """骗子酒馆统计计算类"""

    @staticmethod
    def calculate_player_stats(game_stats: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, float]]:
        """
        计算每位玩家的统计指标

        Args:
            game_stats: 游戏统计数据，格式为 {'X': {...}, 'O': {...}}

        Returns:
            计算后的统计指标
        """
        results = {}

        for player, stats in game_stats.items():
            total_plays = max(1, stats.get('total_plays', 1))
            total_lies = stats.get('lies_told', 0)
            total_challenges = stats.get('challenges_made', 0)

            results[player] = {
                # 基础统计
                'total_plays': stats.get('total_plays', 0),
                'lies_told': total_lies,
                'successful_lies': stats.get('successful_lies', 0),
                'challenges_made': total_challenges,
                'correct_challenges': stats.get('correct_challenges', 0),
                'times_caught': stats.get('times_caught', 0),
                'times_fooled': stats.get('times_fooled', 0),

                # 高级指标
                'lie_rate': total_lies / total_plays if total_plays > 0 else 0,
                'deception_success_rate': stats.get('successful_lies', 0) / max(1, total_lies),
                'challenge_accuracy': stats.get('correct_challenges', 0) / max(1, total_challenges),
                'caught_rate': stats.get('times_caught', 0) / max(1, total_lies),
                'fooled_rate': stats.get('times_fooled', 0) / max(1, total_plays),

                # 信任指标
                'trust_rate': (total_plays - total_challenges) / max(1, total_plays),
            }

        return results

    @staticmethod
    def calculate_game_summary(game_stats: Dict[str, Dict[str, int]], winner: str) -> Dict[str, Any]:
        """
        计算游戏整体统计摘要

        Args:
            game_stats: 游戏统计数据
            winner: 获胜者 ('X' 或 'O')

        Returns:
            游戏摘要
        """
        player_stats = LiarsBarStats.calculate_player_stats(game_stats)

        # 计算整体数据
        total_lies = sum(s.get('lies_told', 0) for s in game_stats.values())
        total_challenges = sum(s.get('challenges_made', 0) for s in game_stats.values())
        total_caught = sum(s.get('times_caught', 0) for s in game_stats.values())

        return {
            'winner': winner,
            'player_stats': player_stats,

            # 游戏整体数据
            'total_lies': total_lies,
            'total_challenges': total_challenges,
            'total_caught': total_caught,

            # 整体指标
            'overall_lie_rate': total_lies / max(1, sum(s.get('total_plays', 0) for s in game_stats.values())),
            'overall_challenge_rate': total_challenges / max(1, sum(s.get('total_plays', 0) for s in game_stats.values())),
            'overall_caught_rate': total_caught / max(1, total_lies),
        }

    @staticmethod
    def format_stats_for_display(stats: Dict[str, float]) -> str:
        """
        格式化统计数据用于显示

        Args:
            stats: 统计指标

        Returns:
            格式化的文本
        """
        lines = [
            f"说谎率: {stats.get('lie_rate', 0):.1%}",
            f"欺骗成功率: {stats.get('deception_success_rate', 0):.1%}",
            f"质疑准确率: {stats.get('challenge_accuracy', 0):.1%}",
            f"被抓率: {stats.get('caught_rate', 0):.1%}",
            f"被骗率: {stats.get('fooled_rate', 0):.1%}",
            f"信任率: {stats.get('trust_rate', 0):.1%}",
        ]

        return "\n".join(lines)

    @staticmethod
    def compare_players(player_stats: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        比较两位玩家的表现

        Args:
            player_stats: 玩家统计数据

        Returns:
            比较结果
        """
        if 'X' not in player_stats or 'O' not in player_stats:
            return {}

        x_stats = player_stats['X']
        o_stats = player_stats['O']

        comparison = {
            'more_deceptive': 'X' if x_stats.get('lie_rate', 0) > o_stats.get('lie_rate', 0) else 'O',
            'better_liar': 'X' if x_stats.get('deception_success_rate', 0) > o_stats.get('deception_success_rate', 0) else 'O',
            'better_detector': 'X' if x_stats.get('challenge_accuracy', 0) > o_stats.get('challenge_accuracy', 0) else 'O',
            'more_trusting': 'X' if x_stats.get('trust_rate', 0) > o_stats.get('trust_rate', 0) else 'O',
        }

        # 添加详细差异
        comparison['differences'] = {
            'lie_rate_diff': x_stats.get('lie_rate', 0) - o_stats.get('lie_rate', 0),
            'deception_success_diff': x_stats.get('deception_success_rate', 0) - o_stats.get('deception_success_rate', 0),
            'challenge_accuracy_diff': x_stats.get('challenge_accuracy', 0) - o_stats.get('challenge_accuracy', 0),
        }

        return comparison


def analyze_liarsbar_game(game) -> Dict[str, Any]:
    """
    分析一局骗子酒馆游戏

    Args:
        game: LiarBarGame 实例

    Returns:
        完整分析结果
    """
    game_stats = game.get_game_stats()
    winner = game.get_winner()

    summary = LiarsBarStats.calculate_game_summary(game_stats['player_stats'], winner)
    comparison = LiarsBarStats.compare_players(summary['player_stats'])

    return {
        'summary': summary,
        'comparison': comparison,
        'raw_stats': game_stats,
        'winner': winner,
        'rounds_played': game_stats.get('rounds_played', 0),
    }