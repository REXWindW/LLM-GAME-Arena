"""
Flask后端主程序 - LLM-GAME-Arena
重构版本：支持游戏注册器，多游戏支持
"""
from flask import Flask, render_template, jsonify, request
from datetime import datetime

# 导入游戏模块（自动注册）
import games
import games.tictactoe
import games.tictactoe3d

from games import get_game_class, get_game_list
from leaderboard import leaderboard
from llm_client import get_llm_move_with_retry
from logger import log_game_event, log_move, logger

app = Flask(__name__)

# 存储当前活跃的游戏会话
# 格式: {game_session_id: {'game': game_instance, 'game_type': str, 'players': dict, ...}}
active_sessions = {}


@app.route('/')
def index():
    """主页 - 显示游戏选择"""
    games_list = get_game_list()
    return render_template('index.html', games=games_list)


@app.route('/api/games')
def api_games():
    """获取可用游戏列表"""
    return jsonify(get_game_list())


@app.route('/api/new_game', methods=['POST'])
def new_game():
    """
    创建新游戏
    """
    data = request.json
    game_type = data.get('game_type', 'tictactoe')
    mode = data.get('mode', 'ai_vs_ai')
    player_x = data.get('player_x', 'Player X')
    player_o = data.get('player_o', 'Player O')
    enable_thinking = data.get('enable_thinking', True)  # thinking开关

    logger.info(f"New game request: type={game_type}, mode={mode}, X={player_x}, O={player_o}, thinking={enable_thinking}")

    # 获取游戏类并创建实例
    game_class = get_game_class(game_type)
    if game_class is None:
        logger.error(f"Unknown game type: {game_type}")
        return jsonify({'error': f'未知的游戏类型: {game_type}'}), 400

    game = game_class()

    # 确定哪方是AI
    if mode == 'ai_vs_ai':
        x_is_ai = True
        o_is_ai = True
    else:
        x_is_ai = data.get('x_is_ai', False)
        o_is_ai = data.get('o_is_ai', False)

    # 创建游戏会话
    session_id = str(len(active_sessions) + 1)
    active_sessions[session_id] = {
        'game': game,
        'game_type': game_type,
        'mode': mode,
        'player_x': player_x,
        'player_o': player_o,
        'x_is_ai': x_is_ai,
        'o_is_ai': o_is_ai,
        'enable_thinking': enable_thinking,
        'thinking_history': []  # 记录所有thinking
    }

    log_game_event(session_id, "created", {
        'game_type': game_type,
        'mode': mode,
        'X': player_x,
        'O': player_o,
        'X_is_AI': x_is_ai,
        'O_is_AI': o_is_ai,
        'thinking': enable_thinking
    })

    return jsonify({
        'session_id': session_id,
        'game_type': game_type,
        'state': game.get_frontend_state(),
        'enable_thinking': enable_thinking,
        'players': {
            'x': player_x,
            'o': player_o
        }
    })


@app.route('/api/make_move', methods=['POST'])
def make_move():
    """
    人类玩家落子
    """
    data = request.json
    session_id = data.get('session_id')
    move = data.get('move')

    if session_id not in active_sessions:
        logger.error(f"Session not found: {session_id}")
        return jsonify({'error': '游戏会话不存在'}), 404

    session = active_sessions[session_id]
    game = session['game']
    player = game.get_current_player()

    if game.is_game_over():
        return jsonify({'error': '游戏已结束'}), 400

    logger.info(f"Human move request: session={session_id}, move={move}, player={player}")

    if game.make_move(move, player):
        log_move(session_id, player, move, True)

        # 记录当前状态
        logger.info(f"After human move: current_player={game.get_current_player()}, x_is_ai={session['x_is_ai']}, o_is_ai={session['o_is_ai']}")

        result = {'state': game.get_frontend_state()}

        # 如果游戏未结束且下一个是AI，自动让AI落子
        if not game.is_game_over():
            current_player = game.get_current_player()
            logger.info(f"Next player: {current_player}, checking if AI should move...")

            if current_player == 'X' and session['x_is_ai']:
                logger.info(f"X is AI, calling _ai_move")
                ai_result = _ai_move(session_id)
                result = ai_result
            elif current_player == 'O' and session['o_is_ai']:
                logger.info(f"O is AI, calling _ai_move")
                ai_result = _ai_move(session_id)
                result = ai_result
            else:
                logger.info(f"Human turn, not calling AI")

        # 检查游戏结束并更新排行榜
        if game.is_game_over():
            _update_leaderboard(session_id)
            log_game_event(session_id, "ended", {
                'winner': game.get_winner(),
                'is_draw': game.is_draw
            })

        return jsonify(result)

    reason = game.get_invalid_reason(move)
    log_move(session_id, player, move, False, reason)
    return jsonify({'error': '无效的落子', 'reason': reason}), 400


@app.route('/api/ai_move', methods=['POST'])
def ai_move():
    """
    AI落子请求

    请求参数:
    - session_id: 游戏会话ID
    """
    data = request.json
    session_id = data.get('session_id')

    if session_id not in active_sessions:
        return jsonify({'error': '游戏会话不存在'}), 404

    result = _ai_move(session_id)

    # 检查游戏结束并更新排行榜
    game = active_sessions[session_id]['game']
    if game.is_game_over():
        _update_leaderboard(session_id)

    return jsonify(result)


def _ai_move(session_id: str) -> dict:
    """
    内部函数：执行AI落子（支持非法操作重试）
    """
    session = active_sessions[session_id]
    game = session['game']
    enable_thinking = session.get('enable_thinking', True)

    if game.is_game_over():
        return {'state': game.get_frontend_state(), 'game_over': True}

    current_player = game.get_current_player()
    model = session['player_x'] if current_player == 'X' else session['player_o']

    logger.info(f"_ai_move: current_player={current_player}, model={model}, thinking={enable_thinking}")

    # 验证当前玩家确实是AI
    if current_player == 'X' and not session['x_is_ai']:
        logger.error(f"Bug: X should be AI but x_is_ai=False")
        return {'state': game.get_frontend_state(), 'error': 'Not AI turn'}
    if current_player == 'O' and not session['o_is_ai']:
        logger.error(f"Bug: O should be AI but o_is_ai=False")
        return {'state': game.get_frontend_state(), 'error': 'Not AI turn'}

    # 使用带重试的LLM落子
    result = get_llm_move_with_retry(game, model, current_player, enable_thinking)
    move = result['move']
    thinking = result['thinking']

    # 记录thinking历史
    thinking_record = {
        'player': current_player,
        'model': model,
        'move': move,
        'thinking': thinking,
        'timestamp': datetime.now().isoformat()
    }
    session['thinking_history'].append(thinking_record)

    if move is not None:
        game.make_move(move, current_player)

    return {
        'state': game.get_frontend_state(),
        'ai_move': move,
        'model': model,
        'thinking': thinking,
        'thinking_history': session['thinking_history']
    }


@app.route('/api/auto_play', methods=['POST'])
def auto_play():
    """
    AI vs AI 模式自动对战

    请求参数:
    - session_id: 游戏会话ID
    - max_moves: 最大步数限制 (默认50)
    """
    data = request.json
    session_id = data.get('session_id')
    max_moves = data.get('max_moves', 50)

    if session_id not in active_sessions:
        return jsonify({'error': '游戏会话不存在'}), 404

    session = active_sessions[session_id]
    game = session['game']

    moves_log = []

    enable_thinking = session.get('enable_thinking', True)

    for _ in range(max_moves):
        if game.is_game_over():
            break

        current_player = game.get_current_player()
        model = session['player_x'] if current_player == 'X' else session['player_o']

        result = get_llm_move_with_retry(game, model, current_player, enable_thinking)
        move = result['move']

        if move is not None:
            game.make_move(move, current_player)
            moves_log.append({
                'player': current_player,
                'model': model,
                'move': move,
                'thinking': result.get('thinking', '')
            })

    # 更新排行榜
    if game.is_game_over():
        _update_leaderboard(session_id)

    return jsonify({
        'state': game.get_frontend_state(),
        'moves_log': moves_log
    })


@app.route('/api/game_state/<session_id>')
def get_game_state(session_id):
    """获取游戏状态"""
    if session_id not in active_sessions:
        return jsonify({'error': '游戏会话不存在'}), 404

    game = active_sessions[session_id]['game']
    return jsonify(game.get_frontend_state())


@app.route('/api/leaderboard')
def get_leaderboard():
    """获取排行榜"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify(leaderboard.get_leaderboard(limit))


@app.route('/api/player_stats/<name>')
def get_player_stats(name):
    """获取指定玩家统计"""
    return jsonify(leaderboard.get_player_stats(name))


def _update_leaderboard(session_id: str):
    """
    更新排行榜（游戏结束后）
    """
    session = active_sessions[session_id]
    game = session['game']
    game_type = session['game_type']

    player_x = session['player_x']
    player_o = session['player_o']

    if game.is_draw:
        leaderboard.record_game(player_x, player_o, is_draw=True, game_type=game_type)
    elif game.get_winner() == 'X':
        leaderboard.record_game(player_x, player_o, is_draw=False, game_type=game_type)
    elif game.get_winner() == 'O':
        leaderboard.record_game(player_o, player_x, is_draw=False, game_type=game_type)


@app.route('/api/player_history/<name>')
def get_player_history(name):
    """获取指定玩家的历史对局"""
    limit = request.args.get('limit', 20, type=int)
    return jsonify(leaderboard.get_player_history(name, limit))


if __name__ == '__main__':
    app.run(debug=True, port=5000)