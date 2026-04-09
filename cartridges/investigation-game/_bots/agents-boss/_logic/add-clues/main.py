import sys
import json


def run(bot, short_memory):

    player_mission = short_memory["player"]["mission"]
    player_progress = short_memory["player"]["progress"]
    trigger_message = bot.get_trigger_message()

    # Check if the player is in a current non-empty location. If not, reply back telling clues cannot be accepted if he is not visiting a location to gather clues.
    def check_valid_location():
        if player_progress["current_location"][1] == "":
            rendered_prompt = bot.render_prompt("invalid-location.md")

            bot.default_output_callback("\nBoss says: ")
            bot.prompt_ai(rendered_prompt, stream=True)
            bot.default_output_callback("\n\n")
            return False
        
        return True
    
    if not check_valid_location():
        return
    
    # Get the clue or list of clues the player is sending.
    def get_player_clues_list():
        # Using an older prompt as the newer prompt standard is not working properly.
        rendered_prompt = bot.render_prompt("get-clues.md", trigger_message=trigger_message)

        ai_output = bot.prompt_ai(rendered_prompt).strip()

        attempts = 0 # If user fails to send clues, the boss will complain and add to the number of "off_context_inquiries".

        while ai_output == "_" and attempts < 3:
            attempts += 1

            players_reply = bot.prompt_user("\nNarrator: Please provide a clue. If you have more than one, separate them by a comma (e.g.: broken glass, residue, red stain, etc.).\n> ")

            rendered_prompt = bot.render_prompt("get-clues.md", trigger_message=players_reply).strip()

            ai_output = bot.prompt_ai(rendered_prompt).strip()

        if attempts >= 3:
            player_progress["off_context_inquiries"] += 1
            bot.memory_save("player-progress.json", json.dumps(player_progress))

            rendered_prompt = bot.render_prompt("repeated-empty-clues.md")

            bot.default_output_callback("\nBoss says: ")
            bot.prompt_ai(rendered_prompt, stream=True)
            bot.default_output_callback("\n\n")

            return False
        
        player_clues = [item.strip() for item in ai_output.split(",") if item]
        return player_clues
    
    player_clues = get_player_clues_list()
    if not player_clues:
        return
    
    # Check if any clues that the player passed are valid.
    def filter_relevant_clues():
        all_clues = player_mission["cities"][player_progress["current_location"][0]]["location_clues"][player_progress["current_location"][1]]["investigation_results"]

        clues = all_clues[::2]   # even indexes (clues)
        flags = all_clues[1::2]  # odd indexes (booleans)

        true_clues = [clue for clue, flag in zip(clues, flags) if flag]

        # Let's inquire the LLM asking it to match loosely similar clues (fuzzy).
        # For that we need to compare 2 lists. Since LLM's are not good at doing this logically, we separate the logic and only ask the fuzzy logic from it.
        relevant_clues = []
        for true_clue in true_clues:
            for player_clue in player_clues:

                rendered_prompt = bot.render_prompt("validate-clues.md", reference_term=true_clue, input_term=player_clue)

                ai_output = bot.prompt_ai(rendered_prompt).strip()

                # If match, simply push it to validClueList. In case of repeated items, those will be filtered afterwards.
                if ai_output == "1":
                    relevant_clues.append(true_clue)
        
        return relevant_clues

    def validate_filtered_clues():
        filtered_clues = filter_relevant_clues()

        previously_added_clues = player_progress["clue_list"].get(player_progress["current_location"][0], [])

        validated_clue_list = list(set(filtered_clues) | set(previously_added_clues))

        # If previous clue list is same length as filteredClueList, no new valid clues were added.
        if len(previously_added_clues) == len(validated_clue_list):
            # ... boss should complain about no new clues.
            rendered_prompt = bot.render_prompt("no-relevant-clues-added.md")

            bot.default_output_callback("\nBoss says: ")
            bot.prompt_ai(rendered_prompt, stream=True)
            bot.default_output_callback("\n\n")
            
            return False
        else:
            # ... new clues were added to the case.
            player_progress["clue_list"][player_progress["current_location"][0]] = validated_clue_list
            bot.memory_save("player-progress.json", json.dumps(player_progress))

            rendered_prompt = bot.render_prompt("relevant-clues-added.md")

            bot.default_output_callback("\nBoss says: ")
            bot.prompt_ai(rendered_prompt, stream=True)
            bot.default_output_callback("\n\n")

            return True

    if not validate_filtered_clues():
        return
    
    # If after adding clues, we check that the "total_clues_needed" per city, parameter is met, we can then move on on the "city progression graph/array" effectively unlocking the next city or group of cities.
    def check_new_city_unlocked():
        current_progression_graph_pointer = player_mission["progression_graph"].index(player_progress["current_location"][0])
        
        total_clues_in_cur_city = len(player_progress["clue_list"][player_progress["current_location"][0]])
        clues_per_city = player_mission["cities"][player_progress["current_location"][0]]["total_clues_needed"]
        if total_clues_in_cur_city < clues_per_city:
            return
        
        if current_progression_graph_pointer == player_progress["progression_graph_pointer"]:
            player_progress["progression_graph_pointer"] += 1

            rendered_prompt = bot.render_prompt(
                "new-city-travel-unlocked.md",
                current_city=player_progress["current_location"][0],
                new_city=player_mission["progression_graph"][player_progress["progression_graph_pointer"]]
                )

            bot.default_output_callback("\nBoss says: ")
            bot.prompt_ai(rendered_prompt, stream=True)
            bot.default_output_callback("\n\n")
        else:
            # If the graph pointer is different it means the player should have already traveled.
            player_progress["off_context_inquiries"] += 1

            rendered_prompt = bot.render_prompt(
                "go-to-another-city.md",
                current_city=player_progress["current_location"][0],
                new_city=player_mission["progression_graph"][player_progress["progression_graph_pointer"]]
                )

            bot.default_output_callback("\nBoss says: ")
            bot.prompt_ai(rendered_prompt, stream=True)
            bot.default_output_callback("\n\n")
        
        bot.memory_save("player-progress.json", json.dumps(player_progress))

    check_new_city_unlocked()