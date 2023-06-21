import json
from google.cloud import storage
import chess
from io import StringIO
import chess.engine
import chess.pgn
import pandas as pd
from src.move import mainline_move, best_move, eval_delta, move_accuracy, assign_move_type


def analyse_game_data(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    bucket_name = event["bucket"]
    blob_name = event["name"]
    print(bucket_name)
    print(blob_name)

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    contents = blob.download_as_string()

    data = json.loads(contents.decode("utf-8"))

    game_pgn = StringIO(data["pgn"])
    chess_game = chess.pgn.read_game(game_pgn)
    board = chess_game.board()

    engine = chess.engine.SimpleEngine.popen_uci(
        r"/lib/stkfsh_15/stk_15.exe"
    )
    depth = 8

    print(f"headers: {data['headers']}.")
    print(f"username: {data['username']}.")

    move_data = []
    for num, move in enumerate(chess_game.mainline_moves()):
        str_bm, eval_bm = best_move(
            board,
            engine,
            depth
        )
        str_ml, eval_ml = mainline_move(
            move,
            board,
            engine,
            depth
        )
        evaldiff = eval_delta(
            num, eval_bm, eval_ml
        )
        move_acc = move_accuracy(evaldiff)
        move_type = assign_move_type(move_acc)

        move_dict = {
            "move_num":num,
            "str_ml":str_ml,
            "eval_ml":eval_ml,
            "str_bm":str_bm,
            "eval_bm":eval_bm,
            "evaldiff":evaldiff,
            "move_acc":move_acc,
            "move_type":move_type,
        }
        move_data.append(move_dict)

    df = pd.DataFrame(move_data)
    
    print(df)

    return 0
