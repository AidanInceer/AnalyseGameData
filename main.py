import base64
import json
from io import StringIO

import chess
import chess.engine
import chess.pgn
import pandas as pd
from flask import Flask, request

from src.move import (
    assign_move_type,
    best_move,
    eval_delta,
    mainline_move,
    move_accuracy,
)

# from google.cloud import bigquery


app = Flask(__name__)


@app.route("/", methods=["POST"])
def index():
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]
    data = json.loads((base64.b64decode(pubsub_message["data"]).decode("utf-8")))

    game_pgn = StringIO(data["pgn"])
    chess_game = chess.pgn.read_game(game_pgn)
    board = chess_game.board()

    engine = chess.engine.SimpleEngine.popen_uci(
        r"./lib/stk15_lin/stockfish-ubuntu-20.04-x86-64"
    )
    depth = 5

    move_data = []
    for num, move in enumerate(chess_game.mainline_moves()):
        str_bm, eval_bm = best_move(board, engine, depth)
        str_ml, eval_ml = mainline_move(move, board, engine, depth)
        evaldiff = eval_delta(num, eval_bm, eval_ml)
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
        base_dict = {
            "username": data["username"],
            "pgn": data["pgn"],
        }
        game_dict = {**data["headers"], **base_dict, **move_dict}

        move_data.append(game_dict)

    df = pd.DataFrame(move_data)
    print(df)

    return ("", 204)

    # data = {"pgn": "A"}

    # bq_client = bigquery.Client()
    # job_config = bigquery.LoadJobConfig()

    # job = bq_client.load_table_from_dataframe(
    #     df, "united-axle-390115.chess_data.test_table_3", job_config=job_config
    # )
    # job.result()

    # table = bq_client.get_table("united-axle-390115.chess_data.test_table_3")
    # print(
    #     f"Loaded {table.num_rows} rows and {len(table.schema)}"
    #     "columns to 'united-axle-390115.chess_data.test_table_3'"
    # )
