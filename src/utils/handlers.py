def handle_request(pubsub_message: dict) -> dict:
    return pubsub_message["message"]["data"]
