import sys
import json
import random


def run(bot, short_memory):

    player_mission = short_memory["player"]["mission"]
    player_progress = short_memory["player"]["progress"]
    trigger_message = bot.get_trigger_message()

    # First we need to check if the player has the total clues needed on current city.
    def check_min_clues():
        # Get current city needed clues.
        clues_needed = player_mission["cities"][player_progress["current_location"][0]]["total_clues_needed"]

        # Get clues found clues so far.
        clues_found = len(player_progress["clue_list"].get(player_progress["current_location"][0], []))

        if clues_found >= clues_needed:
            return True
        
        # If the minimum amount of clues was not collected, tell the player they still need to find more clues before travelling to another city.
        player_progress["off_context_inquiries"] += 1
        bot.memory_save("player-progress.json", json.dumps(player_progress))

        rendered_prompt = bot.render_prompt(
            "not-enough-clues.md",
            current_city=player_mission["cities"][player_progress["current_location"][0]]["name"]
            )

        bot.default_output_callback("\nBoss says: ")
        bot.prompt_ai(rendered_prompt, stream=True)
        bot.default_output_callback("\n\n")

        return False
    
    if not check_min_clues():
        return
    
    # If the player has the minimum amount of clues, now we need to filter to which city the player wants to travel.
    def get_desired_city_slug():
        rendered_prompt = bot.render_prompt("get-city-name.md", trigger_message=trigger_message)

        return bot.prompt_ai(rendered_prompt).strip()
    
    desired_city_slug = get_desired_city_slug()

    # Let's check if the player is trying to travel to the same city they are in.
    def check_same_city_request():
        if desired_city_slug == player_progress["current_location"][0]:
            player_progress["off_context_inquiries"] += 1
            bot.memory_save("player-progress.json", json.dumps(player_progress))

            rendered_prompt = bot.render_prompt(
                "same-city-scold.md",
                city=player_mission["cities"][desired_city_slug]["name"]
                )

            bot.default_output_callback("\nBoss says: ")
            bot.prompt_ai(rendered_prompt, stream=True)
            bot.default_output_callback("\n\n")

            return True
        
        return False
    
    if check_same_city_request():
        return
    
    # The LLM might not have identified a city slug, then, returning _. This means an invalid output, we need to treat it.
    def check_city_slug_valid():
        if desired_city_slug == "_":
            rendered_prompt = bot.render_prompt("invalid-city-slug.md")

            bot.default_output_callback("\nBoss says: ")
            bot.prompt_ai(rendered_prompt, stream=True)
            bot.default_output_callback("\n\n")

            return False
        
        return True
    
    if not check_city_slug_valid():
        return
    
    # The player is only allowed to travel to one other specific city indicated by the "progression_graph_pointer" key. Let's check if the city slug generated above matched the city the player can travel to next.
    def check_travel_allowed():
        next_city_slug = player_mission["progression_graph"][player_progress["progression_graph_pointer"]]

        if next_city_slug == desired_city_slug:
            return True
        
        player_progress["off_context_inquiries"] += 1
        bot.memory_save("player-progress.json", json.dumps(player_progress))

        rendered_prompt = bot.render_prompt(
            "city-not-allowed.md",
            requested_city=desired_city_slug,
            city_allowed=next_city_slug
            )

        bot.default_output_callback("\nBoss says: ")
        bot.prompt_ai(rendered_prompt, stream=True)
        bot.default_output_callback("\n\n")

        return False
    
    if not check_travel_allowed():
        return
    
    # Now, if the player requested to travel to the correct city, we update the player progress accordingly and narrate how was the travel.

    # In case the travel city is the last (final) city, we move to the game endinge node.
    if player_progress["progression_graph_pointer"] == len(player_mission["progression_graph"]) - 1:
        bot.next_node("game-over/mission-complete", short_memory)
        return
    
    # First we need to update the "case_days" key. In this case we ask the LLM to suggest a number of days based on the travel route and we can spicy it up with some "luck factor", meaning we can, let's say, add a random amount of days to simulate things going well or wrong during the trip.


    # Let's, then, first ask the LLM to suggest normal amount of days.
    rendered_prompt = bot.render_prompt(
        "average-travel-days.md",
        departure=player_progress["current_location"][0],
        arrival=player_mission["progression_graph"][player_progress["progression_graph_pointer"]]
        )
    average_days = bot.prompt_ai(rendered_prompt).strip()

    try:
        average_days = int(average_days)
    except (TypeError, ValueError):
        average_days = 3

    # Now that we have the avarage time, let's add the rando luck factor by adding 0 to 5 random days to the trip.
    delay_days = random.randint(0, 5)
    
    # Based on that, now we create a narrative prompt telling the player what happened during the travel.
    rendered_prompt = bot.render_prompt(
        "travel-narration.md",
        average_days=average_days,
        unluck_delay=delay_days,
        departure=player_progress["current_location"],
        arrival=player_mission["progression_graph"][player_progress["progression_graph_pointer"]]
        )

    bot.default_output_callback("\nNarrator: ")
    bot.prompt_ai(rendered_prompt, stream=True)
    bot.default_output_callback("\n\n")

    # Let's update game info.
    player_progress["case_days"] = player_progress["case_days"] + average_days + delay_days

    player_progress["current_location"] = [
        player_mission["progression_graph"][player_progress["progression_graph_pointer"]],
        ""
    ]

    bot.memory_save("player-progress.json", json.dumps(player_progress))

    # We also need to inform the player of places they can visit once they arrive in the city.
    location_list = []
    for dict in player_mission["cities"][player_progress["current_location"][0]]["location_clues"].values():
        location_list.append(dict["name"])

    rendered_prompt = bot.render_prompt(
        "new-locations-to-visit.md",
        current_city=player_progress["current_location"][0],
        new_locations=", ".join(location_list)
        )

    bot.default_output_callback("\nBoss says: ")
    bot.prompt_ai(rendered_prompt, stream=True)
    bot.default_output_callback("\n\n")