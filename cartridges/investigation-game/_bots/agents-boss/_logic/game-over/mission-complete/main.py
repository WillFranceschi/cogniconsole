def run(bot, short_memory):

    player_mission = short_memory["player"]["mission"]
    player_progress = short_memory["player"]["progress"]
    
    # Get the collected clues
    collected_clues = ""

    for key, clues in player_progress.get("clue_list", {}).items():
        collected_clues += f"- {key}: "
        collected_clues += ", ".join(str(clue) for clue in clues)
        collected_clues += "\n"

    progression = player_mission.get("progression_graph", [])
    winner_city = progression[-1] if progression else None


    rendered_prompt = bot.render_prompt(
        "game-ending-narration.md",
        case=player_mission["case"],
        winner_city=winner_city,
        criminal_name=player_mission["criminal_name"],
        case_description=player_mission["description"],
        collected_clues=collected_clues,
        mission_max_days=player_mission["mission_max_days"],
        mission_total_days=player_progress["case_days"] 
    )

    bot.default_output_callback("\nNarrator says: ")
    bot.prompt_ai(rendered_prompt, stream=True)
    bot.default_output_callback("\n\n")

    # Let's allow the boss to make a final joke.
    rendered_prompt = bot.render_prompt(
        "boss-final-message.md",
        case=player_mission["case"],
        winner_city=winner_city,
        criminal_name=player_mission["criminal_name"],
        case_description=player_mission["description"],
        collected_clues=collected_clues,
        mission_max_days=player_mission["mission_max_days"],
        mission_total_days=player_progress["case_days"] 
    )

    bot.default_output_callback("\Boss says: ")
    bot.prompt_ai(rendered_prompt, stream=True)
    bot.default_output_callback("\n\n========== THE END! ==========")

    bot.next_node("boot", "")
