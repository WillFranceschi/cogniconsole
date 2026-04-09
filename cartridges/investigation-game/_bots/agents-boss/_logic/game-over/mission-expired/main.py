import sys
import json


def run(bot, short_memory = None):

    # Check if case_days passed mission days limit
    player_mission = short_memory["player"]["mission"]

    # Prepare prompt.
    case_description = player_mission["description"]
    days_limit = player_mission["mission_max_days"]
    rendered_prompt = bot.render_prompt("prompt.md", case_description=case_description, days_limit=days_limit)

    # Request a new reply.
    bot.default_output_callback(f"Boss says: ")
    bot.prompt_ai(rendered_prompt, stream=True)
    bot.default_output_callback("\n\n========== GAME OVER! ==========\n\n")

    bot.next_node("boot", "")
