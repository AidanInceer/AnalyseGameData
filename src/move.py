import math

import chess
import chess.engine
import chess.pgn
from chess import Board


def mainline_move(
    move: chess.Move,
    board: Board,
    engine: chess.engine.SimpleEngine,
    edepth: int,
) -> tuple:
    """Analysis of the actual chess move played - returns the evaluation.

    Args:
        move (chess.Move): Move.
        board (Board): Current game board.
        engine (chess.engine.SimpleEngine): Engine for analysis.

    Returns:
        tuple: Move string and Move evaluation.
    """
    str_ml = str(move)
    board.push_san(san=str_ml)
    eval_ml_init = engine.analyse(
        board=board,
        limit=chess.engine.Limit(depth=edepth),
        game=object(),
    )
    eval_ml = move_eval(move=eval_ml_init)
    return str_ml, eval_ml


def best_move(board: Board, engine: chess.engine.SimpleEngine, edepth: int) -> tuple:
    """Analysis of the best chess move played - returns the evaluation.

    Args:
        board (Board): Current game board.
        engine (chess.engine.SimpleEngine): Engine for analysis.

    Returns:
        tuple: Best move string and best move evaluation.
    """
    best_move = engine.play(
        board=board,
        limit=chess.engine.Limit(depth=edepth),
        game=object(),
    )
    str_bm = str(best_move.move)
    board.push_san(san=str_bm)
    eval_bm_init = engine.analyse(
        board=board,
        limit=chess.engine.Limit(depth=edepth),
        game=object(),
    )
    eval_bm = move_eval(move=eval_bm_init)
    board.pop()
    return str_bm, eval_bm


def move_eval(move: chess.Move) -> int:
    """Filters the evaluation to remove checkmate and converts to int.

    Args:
        move (chess.Move): A chess move.

    Returns:
        get_eval (int): Integer of the move eval.
    """
    get_eval = str(move["score"].white())
    if "#" in get_eval:
        get_eval = get_eval[1:]
    return int(get_eval)


def eval_delta(move_num: int, eval_bm: float, eval_ml: float) -> float:
    """Different between best move and mainline move.

    Args:
        move_num (int): Move number.
        eval_bm (float): Best move evaluation.
        eval_ml (float): Mainline move evaluation.

    Returns:
        eval_diff (float): Different between main and best move.
    """
    if move_num % 2 == 0:
        return round(abs(eval_bm - eval_ml), 3)
    return round(abs(eval_ml - eval_bm), 3)


def move_accuracy(eval_diff: float) -> float:
    """Move accuracy calulation through inverse sigmoid function.

    Args:
        eval_diff (float): Different between main and best move.

    Returns:
        move_acc (float): Returns an accuracy between 0-100.
    """
    m, v = 0, 1.5
    return round(math.exp(-0.00003 * ((eval_diff - m) / v) ** 2) * 100, 1)


def assign_move_type(move_acc: float) -> int:
    """Calculate the move type of a move.

    Args:
        move_acc (_type_): Accuracy between 0-100.

    Returns:
        int: Type of move
            - best = 2,
            - excellent = 1,
            - good = 0,
            - inacc = -1,
            - mistake = -2,
            - blunder = -3,
            - missed win = -4
    """
    if move_acc == 100:
        return 2
    elif 99.5 <= move_acc < 100:
        return 1
    elif 87.5 <= move_acc < 99.5:
        return 0
    elif 58.6 <= move_acc < 87.5:
        return -1
    elif 30 <= move_acc < 58.6:
        return -2
    elif 2 <= move_acc < 30:
        return -3
    else:
        return -4


# import json
# from google.cloud import storage
# import chess
# import os
# from io import StringIO
# import chess.engine
# import chess.pgn
# import pandas as pd
# from src.move import mainline_move, best_move, eval_delta, move_accuracy, assign_move_type


# def analyse_game_data(event, context):
#     """Triggered by a change to a Cloud Storage bucket.
#     Args:
#          event (dict): Event payload.
#          context (google.cloud.functions.Context): Metadata for the event.
#     """
#     bucket_name = event["bucket"]
#     blob_name = event["name"]
#     print(bucket_name)
#     print(blob_name)

#     storage_client = storage.Client()

#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(blob_name)
#     contents = blob.download_as_string()

#     data = json.loads(contents.decode("utf-8"))

#     game_pgn = StringIO(data["pgn"])
#     chess_game = chess.pgn.read_game(game_pgn)
#     board = chess_game.board()

#     engine = chess.engine.SimpleEngine.popen_uci(
#         f"{os.getcwd()}\lib\stkfsh_15\stk_15.exe"
#     )
#     depth = 8

#     print(f"headers: {data['headers']}.")
#     print(f"username: {data['username']}.")

#     move_data = []
#     for num, move in enumerate(chess_game.mainline_moves()):
#         str_bm, eval_bm = best_move(
#             board,
#             engine,
#             depth
#         )
#         str_ml, eval_ml = mainline_move(
#             move,
#             board,
#             engine,
#             depth
#         )
#         evaldiff = eval_delta(
#             num, eval_bm, eval_ml
#         )
#         move_acc = move_accuracy(evaldiff)
#         move_type = assign_move_type(move_acc)

#         move_dict = {
#             "move_num":num,
#             "str_ml":str_ml,
#             "eval_ml":eval_ml,
#             "str_bm":str_bm,
#             "eval_bm":eval_bm,
#             "evaldiff":evaldiff,
#             "move_acc":move_acc,
#             "move_type":move_type,
#         }
#         move_data.append(move_dict)

#     df = pd.DataFrame(move_data)

#     print(df)

#     return 0
