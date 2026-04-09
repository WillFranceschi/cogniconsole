import sys
import json
from types import SimpleNamespace


def run(bot, short_memory):
    
    # Print initial instructions.
    bot.default_output_callback(
    "\nNarrator says: You are an investigative agent working for a secret and highly respected intelligence agency.\n"
    "You are logged into the encrypted messaging app, allowing you to communicate securely with your immediate superior.\n"
    )

    bot.default_output_callback(
    "\nNarrator says: He is a straight forward kind of person who will only accept well messages directly related to the case you are currently working on.\n"
    "Messages you can send to him:\n"
    )

    bot.default_output_callback(
    "- Visit location: You can visit a list of locations given by you boss.\n"
    "- Add clue: You can request your boss to log clues you found when visiting locations. But be aware not all clues are relevant.\n"
    "- Travel to another city: You can request to travel to another city based on the clues you collected on the current city you are in.\n"
    )

    while True:
        user_input = input("\nType \"start\" to begin your investigation: \n").strip().lower()
        
        if user_input == "start":
            break
    
    player_mission = json.loads(bot.asset_load("louvre-heist.json"))
    player_progress = json.loads(bot.memory_load("template_player-progress.json"))

    # Getting the list of possible locations slugs/names to visit.
    location_names = []
    for key, value in player_mission["cities"][player_progress["current_location"][0]]["location_clues"].items():
        location_names.append(value["name"])

    # Making sure the game will start with the default initial player data.
    bot.memory_save("player-progress.json", json.dumps(player_progress))

    rendered_prompt = bot.render_prompt(
        "give-the-mission.md",
        case_title=player_mission["case"],
        case_description=player_mission["description"],
        current_city=player_progress["current_location"][0],
        locations_list=", ".join(location_names)
    )

    bot.default_output_callback("\nBoss says: ")
    bot.prompt_ai(rendered_prompt, stream=True)
    bot.default_output_callback("\n\n")

    bot.set_starting_node("start")
