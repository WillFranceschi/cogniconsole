import sys
import json


def run(bot, short_memory):

    player_mission = short_memory["player"]["mission"]
    player_progress = short_memory["player"]["progress"]
    trigger_message = bot.get_trigger_message()

    # Getting the list of possible locations slugs/names to visit.
    location_slugs = []
    location_names = []
    for key, value in player_mission["cities"][player_progress["current_location"][0]]["location_clues"].items():
        location_slugs.append(key)
        location_names.append(value["name"])

    # First we find out which location the player wants to visit.
    def check_location_slug():

        rendered_prompt = bot.render_prompt("check-location-slugs.md", location_slugs=", ".join(location_slugs), trigger_message=trigger_message)
        ai_output = bot.prompt_ai(rendered_prompt)
        players_location_slug = ai_output.strip()
    
        # If no location slug was found...
        if players_location_slug == "_":
            rendered_prompt = bot.render_prompt("no-location-mentioned.md", location_names=", ".join(location_names))

            player_progress["off_context_inquiries"] += 1
            bot.memory_save("player-progress.json", json.dumps(player_progress))

            bot.default_output_callback("\nBoss says: ")
            bot.prompt_ai(rendered_prompt, stream=True)
            bot.default_output_callback("\n\n")
            return False
        
        # If a location slug was found, check if it is valid and then move the player to that location. If it is not valid we send to _llm-error node
        if players_location_slug not in location_slugs:
            short_memory["ai_error"] = {}
            short_memory["ai_error"]["message"] = "AI model could identify a location slug."
            short_memory["ai_error"]["trigger_message"] = trigger_message
            short_memory["ai_error"]["ai_output"] = ai_output

            bot.next_node("outboundaries/ai_errors/visit-location", short_memory)
            return False
    
        return players_location_slug

    # We also must check if the location provided had been already visited.
    players_location_slug = check_location_slug()
    if not players_location_slug:
        return
    location_index = location_slugs.index(players_location_slug)
    
    def check_location_already_visited():

        if players_location_slug in player_progress["location_visit_history"]:

            rendered_prompt = bot.render_prompt("location-already-visited.md", location_name=location_names[location_index])

            player_progress["off_context_inquiries"] += 1
            bot.memory_save("player-progress.json", json.dumps(player_progress))

            bot.default_output_callback("\nBoss says: ")
            bot.prompt_ai(rendered_prompt, stream=True)
            bot.default_output_callback("\n\n")

            return True
        
        return False
    
    if check_location_already_visited():
        return
    
    # Now that we have a valid slug, we update player's current location and create a scenario for that location. For that, we will need a list of clues on that location so the player can add the clues to their list.
    clue_list = player_mission["cities"][player_progress["current_location"][0]]["location_clues"][players_location_slug]["investigation_results"][0::2]

    # Now, we update player location and location history. Also, we output a message with a scenario where the clues are mentioned square brackets.
    player_progress["current_location"][1] = players_location_slug
    player_progress["location_visit_history"].append(players_location_slug)
    player_progress["case_days"] += 1
    bot.memory_save("player-progress.json", json.dumps(player_progress))

    rendered_prompt = bot.render_prompt("visiting-location.md", location_name=location_names[location_index], case_description=player_mission["description"], clue_list=", ".join(clue_list))

    bot.default_output_callback("\nNarrator: ")
    bot.prompt_ai(rendered_prompt, stream=True)
    bot.default_output_callback("\n\n")