import sys
import json


def run(bot, short_memory=None):
    # Check if off_context_inquiries in player_progress passed max_off_context_messages in player_mission
    player_mission = short_memory["player"]["mission"]
    player_progress = short_memory["player"]["progress"]

    # Prepare prompt.
    off_context_inquiries = player_progress["off_context_inquiries"]
    max_off_context_messages = player_mission["max_off_context_messages"]
    rendered_prompt = bot.render_prompt(
        "prompt.md",
        off_context_inquiries=off_context_inquiries,    max_off_context_messages=max_off_context_messages
    )

    # Request a new reply.
    bot.default_output_callback(f"Boss says: ")
    bot.prompt_ai(rendered_prompt, stream=True)
    bot.default_output_callback(f"\n\n========== GAME OVER! ==========\n\n")

    bot.next_node("boot", "")
