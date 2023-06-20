import json
from google.cloud import storage
import chess
import chessdotcom
from io import StringIO
import chess.engine
import chess.pgn


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

    print(f"headers: {data['headers']}.")
    print(f"username: {data['username']}.")

    for num, move in board.mainline_moves():
        print(f"{num}: {move}")
