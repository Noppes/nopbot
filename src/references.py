import os

token = os.environ.get("NOPBOT_TOKEN", "")
message_history_channel_id = int(os.environ.get("NOPBOT_HISTORY_MESSAGE_CHANNEL", 0))
message_mcstatus_channel_id = int(os.environ.get("NOPBOT_MCSTATUS_MESSAGE_CHANNEL", 0))
message_gaming_channel_id = int(os.environ.get("NOPBOT_GAMING_MESSAGE_CHANNEL", 0))

openai_key = os.environ.get("OPENAI_KEY", "")
openai_prompt = os.environ.get("OPENAI_PROMPT", "")