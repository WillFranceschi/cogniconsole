import sys
import json


def run(bot, short_memory):
    
    bot.default_output_callback(f"AI output error. Generated output:")
    bot.default_output_callback(json.dumps(short_memory["ai_output"]))
    sys.exit(0)