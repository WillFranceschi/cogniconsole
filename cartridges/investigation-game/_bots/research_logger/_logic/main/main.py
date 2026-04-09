import sys
import json
from datetime import datetime, timezone


def run(bot, short_memory):

    # Get text_buffer reference created on boot node.
    internal_utils = bot.api("internal_utils")

    # Prepare to prompt bot_agents_boss.
    bot_agents_boss = bot.get_linked_bot("agents_boss")

    current_utc = datetime.now(timezone.utc)
    formatted_utc = current_utc.strftime("%y%m%d-%H%M%S")

    text_to_file = f"_* {formatted_utc}\n" + f"Player says: {bot.get_trigger_message()}\n"
    bot.memory_save(f"log_{internal_utils.session_formatted_utc}", text_to_file, True)

    bot_agents_boss.prompt(bot.get_trigger_message())

    text_to_file = "".join(internal_utils.text_buffer)
    bot.memory_save(f"log_{internal_utils.session_formatted_utc}", text_to_file, True)

    internal_utils.text_buffer.clear()
