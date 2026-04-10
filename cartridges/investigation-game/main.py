import os
import sys
from pathlib import Path

# Ensure /project is in sys.path if coding without cogniconsole package installed.
# Caution! The next path is hardcoded and is a hack.
# sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# print(str(Path(__file__).resolve().parent.parent.parent))

# exit(0)

from cogniconsole.bot import Bot

def main():
    # Cartridge directory path
    cartridge_dir = Path(__file__).parent

    # Setting up default ML model.
    default_ml_model_api = os.getenv("COGNICONSOLE_DEFAULT_MODEL_API")

    if default_ml_model_api == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            print(
                "\nError: OPENAI_API_KEY environment variable not found.\n"
                "Please set your OpenAI API key before running Cogniconsole:\n"
                "export OPENAI_API_KEY='sk-...' (bash/zsh)\n"
            )
            sys.exit(1)
    
    elif default_ml_model_api == "ollama":
        ollama_model = os.getenv("COGNICONSOLE_OLLAMA_DEFAULT_MODEL")
        flag = False
        if not ollama_model:
            print(
                "\nError: COGNICONSOLE_OLLAMA_DEFAULT_MODEL environment variable not found.\n"
                "Please set the default Ollama model before running Cogniconsole.\n"
                "Example:\n"
                "export COGNICONSOLE_OLLAMA_DEFAULT_MODEL='deepseek-r1:latest'\n"
            )
            flag = True
        
        ollama_url = os.getenv("COGNICONSOLE_OLLAMA_DEFAULT_API_URL")
        if not ollama_url:
            print(
                "\nError: COGNICONSOLE_OLLAMA_DEFAULT_API_URL environment variable not found.\n"
                "Please set the default Ollama API URL before running Cogniconsole.\n"
                "Example:\n"
                "export COGNICONSOLE_OLLAMA_DEFAULT_API_URL='http://192.168.8.126:11434/api/generate'\n"
            )
            flag = True
        
        if flag:
            sys.exit(1)

    # Instantiate bot
    metabot = Bot(
        cartridges_path=cartridge_dir.parent,  # /cartridges
        cartridge_dir=cartridge_dir.name,      # "investigation-game"
        bot_name="_metabot",
        metabot=None,
        starting_node="start",
        output_callback=None
    )
    # To initialize the metabot we call the prompt function.
    # This will trigger the first node of the metabot.
    metabot.prompt("")

    default_bot_listener = None
    
    # Instantiate agent's boss bot
    bot_agents_boss = Bot(
        cartridges_path=cartridge_dir.parent,  # /cartridges
        cartridge_dir=cartridge_dir.name,      # "investigation-game"
        bot_name="agents-boss",
        metabot=metabot,
        starting_node="boot",
        default_ai_api_namespace=default_ml_model_api
    )

    log_chats = os.getenv("COGNICONSOLE_LOG_CHATS")
    if not log_chats:
        default_bot_listener = bot_agents_boss
        default_bot_listener.prompt("")

    else:
        # Instantiate researcher bot.
        bot_research_logger = Bot(
            cartridges_path=cartridge_dir.parent,
            cartridge_dir=cartridge_dir.name,
            bot_name="research_logger",
            metabot=metabot,
            starting_node="boot",
            default_ai_api_namespace=default_ml_model_api
        )

        default_bot_listener = bot_research_logger
        default_bot_listener.link_bot("agents_boss", bot_agents_boss)

        # Initializing game.
        default_bot_listener.prompt("")

    # Initializing prompt interaction.
    def listen():
        try:
            text = input("> ").strip()
            if text == "_exit":
                return None
            return text
        except KeyboardInterrupt:
            print("\nExiting.")
            return None

    while True:
        user_input = listen()
        if user_input is None:
            break
        default_bot_listener.prompt(user_input)

if __name__ == "__main__":
    main()
