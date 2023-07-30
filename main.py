import json
from google.cloud import storage
import chess
import os
from io import StringIO
import chess.engine
import chess.pgn
import pandas as pd
from src.move import best_move, mainline_move, eval_delta, move_accuracy, move_eval, assign_move_type
from google.cloud import bigquery


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
        r"./stk15_lin/stockfish-ubuntu-20.04-x86-64"
    )
    depth = 8

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
            "move_num": num,
            "str_ml": str_ml,
            "eval_ml": eval_ml,
            "str_bm": str_bm,
            "eval_bm": eval_bm,
            "evaldiff": evaldiff,
            "move_acc": move_acc,
            "move_type": move_type,
        }
        move_data.append(move_dict)

    df = pd.DataFrame(move_data)

    dict_base = {
        "username": data["username"],
        "pgn": data["pgn"],
    }

    bq_dict = {**data["headers"], **dict_base}

    bq_client = bigquery.Client()
    job_config = bigquery.LoadJobConfig()

    job = bq_client.load_table_from_dataframe(
        df, "united-axle-390115.chess_data.test_table_2", job_config=job_config
    )
    job.result()

    table = bq_client.get_table("united-axle-390115.chess_data.test_table_2")
    print(
        f"Loaded {table.num_rows} rows and {len(table.schema)} columns to 'united-axle-390115.chess_data.test_table_2'"
    )
