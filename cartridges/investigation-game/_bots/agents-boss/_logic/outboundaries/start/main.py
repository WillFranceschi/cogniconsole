import json

def run(bot, short_memory):

    player_mission = short_memory["player"]["mission"]
    player_progress = short_memory["player"]["progress"]
    trigger_message = bot.get_trigger_message()

    player_progress["off_context_inquiries"] += 1

    bot.memory_save("player-progress.json", json.dumps(player_progress))

    rendered_prompt = bot.render_prompt("prompt.md",
                                        trigger_message=trigger_message,
                                        off_context_inquiries=player_progress["off_context_inquiries"],
                                        max_off_context_messages=player_mission["max_off_context_messages"])
    bot.default_output_callback("\nBoss says: ")
    bot.prompt_ai(rendered_prompt, stream=True)
    bot.default_output_callback("\n\n")

    # print("node_outboundaries/start")

    # return
    # response = bot.prompt_user("What is the meaning of life")
    # print(f"user said: {response}")
    # print(bot.get_trigger_message())
    # print(msg)