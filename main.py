import json
import requests
from google.cloud import storage

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

    print(f"=============================================================")
    print(f"username: {data['username']}.")
    print(f"game_num: {data['game_num']}.")
    print(f"pgn: {data['pgn']}.")
    print(f"headers: {data['headers']}.")
