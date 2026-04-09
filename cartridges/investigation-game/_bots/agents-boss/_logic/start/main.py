import sys
import json


def run(bot, short_memory):
    
    player_mission = json.loads(bot.asset_load("louvre-heist.json"))
    player_progress = json.loads(bot.memory_load("player-progress.json"))
    trigger_message = bot.get_trigger_message()

    # Short memory initialization.
    short_memory = {
        "player": {
            "mission": player_mission,
            "progress": player_progress
        }
    }

    # Everytime the player sends a message we need to check if it exceeded mission_max_days and max_off_context_messages. If that's the case, its game over.
    def check_game_over(player_progress, player_mission):
        if player_progress["case_days"] > player_mission["mission_max_days"]:
            bot.next_node("game-over/mission-expired", short_memory)
            return True

        if player_progress["off_context_inquiries"] > player_mission["max_off_context_messages"]:
            bot.next_node("game-over/too-many-off-context-messages", short_memory)
            return True

        return False
    
    if check_game_over(player_progress, player_mission):
        return

    # Inject prompt with player's inquiry.
    # Using an older prompt as the newer prompt standard is not working properly.
    rendered_prompt = bot.render_prompt("prompt.md", player_inquiry=trigger_message)

    # Confirm with LLM what the user asked.
    ai_output = bot.prompt_ai(rendered_prompt)

    # Go to specific node based on the json "a" key.
    # Note this is the first instance where we are implementing decision making logic. Meaning here we choose the next node based on the LLM's answer.
    if ai_output == "t":
        bot.next_node("travel", short_memory)
    elif ai_output == "v":
        bot.next_node("visit-location", short_memory)
    elif ai_output == "c":
        bot.next_node("add-clues", short_memory)
    elif ai_output == "o":
        bot.next_node("outboundaries/start", short_memory)
    else:
        short_memory["ai_output"] = ai_output
        bot.next_node("errors/ai/log", short_memory)