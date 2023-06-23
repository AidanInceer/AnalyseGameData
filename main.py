import json
from google.cloud import storage
import chess
import os
from io import StringIO
import chess.engine
import chess.pgn
import pandas as pd
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

    dict_base = {
        "username": data["username"],
        "total_moves": len(chess_game.mainline_moves()),
        "moves_list": list(chess_game.mainline_moves()),
    }

    bq_dict = {**data["headers"], **dict_base}
    df = pd.DataFrame(bq_dict)

    bq_client = bigquery.Client()
    job_config = bigquery.LoadJobConfig()

    job = bq_client.load_table_from_dataframe(
        df, "chess_data_table", job_config=job_config
    )
    job.result()

    table = bq_client.get_table("chess_data_table")
    print(
        f"Loaded {table.num_rows} rows and {len(table.schema)} columns to chess_data_table"
    )
