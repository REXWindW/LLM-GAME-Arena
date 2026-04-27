#!/usr/bin/env python3
"""
清空本地 JSON 记录文件
- game_history.json: 游戏历史记录
- leaderboard.json: 排行榜数据
"""
import json
import os

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 要清空的文件
FILES = {
    'game_history.json': [],           # 空数组
    'leaderboard.json': {}              # 空对象
}


def clear_records():
    for filename, empty_value in FILES.items():
        filepath = os.path.join(SCRIPT_DIR, filename)

        if os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(empty_value, f, indent=2)
            print(f"✓ 已清空: {filename}")
        else:
            print(f"✗ 文件不存在: {filename}")

    print("\n所有记录已清空!")


if __name__ == '__main__':
    confirm = input("确定要清空所有游戏记录吗? (y/N): ")
    if confirm.lower() == 'y':
        clear_records()
    else:
        print("已取消")