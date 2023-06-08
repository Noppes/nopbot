import os

token = os.environ.get("NOPBOT_TOKEN", "")
message_channel_id = int(os.environ.get("NOPBOT_MESSAGE_CHANNEL", 0))