"""
排行榜数据管理 - JSON存储
"""
import json
import os
from datetime import datetime
from typing import List, Dict
from threading import Lock

DATA_FILE = os.path.join(os.path.dirname(__file__), 'leaderboard.json')
HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'game_history.json')


class Leaderboard:
    def __init__(self):
        self._lock = Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """确保数据文件存在"""
        if not os.path.exists(DATA_FILE):
            self._write_data({}, DATA_FILE)
        if not os.path.exists(HISTORY_FILE):
            self._write_data([], HISTORY_FILE)

    def _read_data(self, file_path: str = DATA_FILE) -> Dict:
        """读取JSON数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {} if file_path == DATA_FILE else []

    def _write_data(self, data, file_path: str = DATA_FILE):
        """写入JSON数据"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def record_game(self, winner: str, loser: str, is_draw: bool = False, game_type: str = 'tictactoe'):
        """
        记录一局游戏结果

        Args:
            winner: 获胜者名称（模型名或人类玩家名）
            loser: 失败者名称
            is_draw: 是否平局
            game_type: 游戏类型
        """
        with self._lock:
            # 更新统计数据
            data = self._read_data(DATA_FILE)

            for player in [winner, loser]:
                if player not in data:
                    data[player] = {'wins': 0, 'losses': 0, 'draws': 0}

            if is_draw:
                data[winner]['draws'] += 1
                data[loser]['draws'] += 1
            else:
                data[winner]['wins'] += 1
                data[loser]['losses'] += 1

            self._write_data(data, DATA_FILE)

            # 记录历史对局
            history = self._read_data(HISTORY_FILE)
            game_record = {
                'timestamp': datetime.now().isoformat(),
                'game_type': game_type,
                'winner': winner if not is_draw else None,
                'loser': loser if not is_draw else None,
                'players': [winner, loser],
                'result': 'draw' if is_draw else 'win'
            }
            history.append(game_record)
            # 只保留最近100条记录
            if len(history) > 100:
                history = history[-100:]
            self._write_data(history, HISTORY_FILE)

    def get_player_stats(self, name: str) -> Dict:
        """获取指定玩家的统计数据"""
        with self._lock:
            data = self._read_data(DATA_FILE)
            if name in data:
                stats = data[name]
                stats['name'] = name
                stats['score'] = stats['wins'] - stats['losses']
                return stats
            return {'name': name, 'wins': 0, 'losses': 0, 'draws': 0, 'score': 0}

    def get_player_history(self, name: str, limit: int = 20) -> List[Dict]:
        """获取指定玩家的历史对局"""
        with self._lock:
            history = self._read_data(HISTORY_FILE)
            player_games = []

            for game in history:
                if name in game['players']:
                    record = {
                        'timestamp': game['timestamp'],
                        'game_type': game['game_type'],
                        'opponent': game['players'][0] if game['players'][1] == name else game['players'][1],
                        'result': 'draw' if game['result'] == 'draw' else ('win' if game['winner'] == name else 'lose')
                    }
                    player_games.append(record)

            # 按时间降序
            player_games.sort(key=lambda x: x['timestamp'], reverse=True)
            return player_games[:limit]

    def get_leaderboard(self, limit: int = 50) -> List[Dict]:
        """
        获取排行榜（按score降序排列）

        Returns:
            List of dicts with keys: name, wins, losses, draws, score
        """
        with self._lock:
            data = self._read_data(DATA_FILE)

            leaderboard = []
            for name, stats in data.items():
                entry = {
                    'name': name,
                    'wins': stats['wins'],
                    'losses': stats['losses'],
                    'draws': stats.get('draws', 0),
                    'score': stats['wins'] - stats['losses']
                }
                leaderboard.append(entry)

            # 按score降序，wins降序排序
            leaderboard.sort(key=lambda x: (x['score'], x['wins']), reverse=True)

            return leaderboard[:limit]

    def clear_leaderboard(self):
        """清空排行榜和历史"""
        with self._lock:
            self._write_data({}, DATA_FILE)
            self._write_data([], HISTORY_FILE)


# 全局实例
leaderboard = Leaderboard()