def handle_request(pubsub_message: dict):
    return pubsub_message["message"]["data"]
