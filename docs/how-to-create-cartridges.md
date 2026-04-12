# How to Create Cartridges for Cogniconsole

In this tutorial, we will use the **"investigation-game"** as a practical example of how to build and structure your own cartridges.

## Case Study: The Investigation Game
Inspired by the classic *Carmen Sandiego* series and the recent real-world heist at the Louvre museum, this cartridge is a text-based simulation. You play as a field agent exchanging messages with your superior to solve a crime.

The cartridge utilizes two distinct bots:

* **Agent Boss**: A "Specialist" that simulates your superior. He assigns the case, evaluates clues, and directs your investigation.
* **Research Logger**: A utility bot that acts as a proxy between the Agent Boss and the player. While toggled off by default, when active, it logs every interaction for research purposes. It saves game runs to its own `_memory/` folder as a Markdown file, using timestamps as an index.

## Directory Structure
To run a cartridge in Cogniconsole, use the following command:
`$ cogniconsole <path-to-cartridge-dir>`

All cartridge assets and logic must reside within a single directory. While Cogniconsole is designed to be as flexible as possible, it follows a specific directory schema to ensure the core library can initialize your project correctly.

### Basic Structure and Required Files
At a minimum, every cartridge directory must contain a `main.py` file at its root. 

* **`main.py`**: This file is responsible for **"bootloading"** the cartridge. When Cogniconsole loads a directory, it looks for this file first to initialize the cartridge logic and state.
* **`_bots/`**: This directory is the home of your "bots." In Cogniconsole development, **Bots** are the primary entities that define interaction, personality, and behavior within your application.

```text
<your-custom-path>/investigation-game/
├── main.py
└── _bots/
    ├── ...
```
### Rules for Directory Naming
The primary rule in Cogniconsole is that **directories prefixed with an underscore (`_`) are reserved.** This ensures a protected namespace for future core features and helps separate framework metadata from your custom logic.

### Recommended Naming Conventions
To keep cartridges organized and readable, we suggest following the **URL convention** (kebab-case):
`this-is-the-convention-for-directory-names/`
`this-is-my-file-name.md`

#### Semantic Metadata Encoding
We use the underscore (`_`) as a semantic separator to encode specific information within a filename or directory name without breaking the primary identifier. For example, if you need to prefix a file with a date:

**Example:** `260410_my-file-description.jpg`

* **`260410`**: Date information.
* **`_`**: Semantic separator.
* **`my-file-description`**: Primary description/slug.

> **Note:** While powerful, you should be parsimonious with this technique. Avoid creating excessively long names that hinder readability.

### Structure of the `_bots/` Directory
The `_bots/` folder contains the individual AI entities for your cartridge. Each bot typically lives in its own subdirectory:

```text
<your-custom-path>/investigation-game/
├── main.py
└── _bots/
    ├── _metabot/         (Reserved framework bot)
    ├── agents-boss/      (Specific character/entity)
    └── research-logger/  (Utility/logging bot)
```

# The Bot Entity

In the Cogniconsole ecosystem, a **Bot** is a discrete, autonomous agent designed to inhabit a specific role within your application. 

Think of a Bot as a **"Dedicated Specialist."** Whether that role is narrative (like a "Witness" in an investigation) or functional (like a "SQLite Interface"), the Bot is defined by its specific scope of work. Just as a human specialist follows a protocol to provide an answer, a Cogniconsole Bot uses its instructions and state to process information and interact with the user or other bots.

## The Bot Lifecycle
Every time a Bot receives an input, whether from a human user or another system entity, it follows a simple, linear lifecycle:

`Input Message` -> `Bot Processing` -> `Output Message`

## How do Bots process inputs?
To keep interactions grounded and manageable, we have emulated the human limitation of focusing on a single decision-making process at a time. This mirrors the **Concept of Attention** that is central to modern LLM advancements.

## The "One-at-a-Time" Rule
Each Bot processes exactly **one input message** at a time. While a Bot is busy "thinking" or processing its current task, it is blocked from receiving other inputs. This architectural choice offers two major benefits:

1.  **Simplicity:** It removes the complexity of managing concurrent states or "race conditions" within a single agent's logic.
2.  **Scalability:** Because Bots are virtual entities, they are easily replicable. If a specific role becomes a bottleneck, the cartridge can simply spawn additional instances of that bot to handle the load.

**Example: Scalable Specialists**
Because bots are lightweight virtual entities, you can design your cartridge to scale horizontally. For instance, if a single "Support Bot" instance reaches its processing capacity, the cartridge logic can be programmed to spawn a "swarm" of identical "Support Bot" instances to distribute the workload. This ensures that the single-threaded nature of an individual bot never becomes a bottleneck for the entire system.

## Structure of the Bot Directory

To understand how a specialist functions, let's examine the internal structure of a bot called `agents-boss`.

```text
<your-custom-path>/investigation-game/
|-- main.py
|-- _bots/
    |-- _metabot/...
    |-- agents-boss/
        |-- _assets/
        |-- _logic/
        |-- _memory/
```

### _assets/
This directory contains global, static information relevant to the bot's domain. In our investigation game example, this folder stores `louvre-heist.json`, which contains the fixed facts and details about the crime that the bot can reference.

### _logic/
This directory contains the **"reasoning tree"** of the bot. This is where the decision-making flows and behavioral instructions are defined. We will explore the internal folder structure of `_logic/` in the next section.

### _memory/
This directory manages the bot's long-term persistence. For the investigation game, it contains two key files:

* **`player-progress.json`**: This file tracks the live state of the current game session (e.g., clues found, locations visited).
* **`template_player-progress.json`**: This is a "clean" version of the progress file. When a game session ends or needs to be reset, the cartridge uses this template to restore the default state.

## The Bot Logic

For the **Investigation Game**, the `agents-boss` bot is designed for high predictability. It is programmed to process only three primary instructions:

1.  **Visit Location:** Investigate a specific spot in the current city.
2.  **Add Clues:** Submit new evidence to the case file.
3.  **Travel:** Move the investigation to a different city.

Any message falling outside these three categories is considered **"outboundary."** In these cases, the bot responds "in character," informing the player that the message is nonsensical or irrelevant to the investigation. This strict behavioral limit ensures the bot remains a reliable tool rather than an unpredictable conversationalist.

### Internal Logic Structure
The `_logic/` directory follows a node-based architecture. Each subdirectory represents a specific state or "node" in the bot's decision-making tree:

```text
<your-custom-path>/investigation-game/
|-- main.py
|-- _bots/
    |-- agents-boss/
        |-- _logic/
            |-- boot/            (Runs once when the game starts)
            |-- start/           (The router: filters player intent)
            |-- visit-location/  (Handles "visit a location" messages)
            |-- add-clues/       (Handles evidence submission)
            |-- travel/          (Handles "travel to another city" messages)
            |-- errors/          (Handles invalid LLM outputs)
            |-- outboundaries/   (Handles unpredicted player messages)
            |-- game-over/       (Handles win/loss conditions)
```

## Start Node: The Main Router

The `start` node acts as the "router" of the bot's logic tree. It is responsible for interpreting the player's natural language and routing the execution to the appropriate specialized node.

Below is the implementation of the `start` node and its associated prompt.

### Node Implementation (`run.py`)

```python
import sys   # Any additional required library for the node execution.
import json  # Because each bot has "api tools" we recommend keeping minimal dependencies per node.


def run(bot, short_memory): # This is the entrypoint that cogniconsole core library will look for.
                            # bot parameter: receives the reference of the current bot (agent's boss)
                            # short memory: for the first node it receives the original message; when nodes call other nodes
                            # they can pass whatever data is important.
    
    # Retrieval of long term memory for the current game run.
    # Here, notice some of the Bot's tools. Because we have a structured directory, cartridge creators can use the methods
    # bot.asset_load and bot.memory_load and those methods will look for files in the `_asset` and `_memory` directories.
    player_mission = json.loads(bot.asset_load("louvre-heist.json")) # player mission coming from the bot's `_asset` directory.
    player_progress = json.loads(bot.memory_load("player-progress.json")) # player progress from the bot's `_memory` directory.
    trigger_message = bot.get_trigger_message() # the original trigger message sent by the user/player

    # Short memory initialization.
    # Here we create a dictionary that will be passed as short memory to other nodes.
    short_memory = {
        "player": {
            "mission": player_mission,
            "progress": player_progress
        }
    }

    # Everytime the player sends a message we need to check if it exceeded mission_max_days and max_off_context_messages. If that's the case, its game over.
    # Here we have our first node navigation which is done by the method bot.next_node.
    # Notice that this method receives two arguments: the node path and short memory.
    def check_game_over(player_progress, player_mission):
        if player_progress["case_days"] > player_mission["mission_max_days"]:
            bot.next_node("game-over/mission-expired", short_memory)
            return True

        if player_progress["off_context_inquiries"] > player_mission["max_off_context_messages"]:
            bot.next_node("game-over/too-many-off-context-messages", short_memory)
            return True

        return False
    
    # Here, if we reach game-over condition, we exit this current node execution
    if check_game_over(player_progress, player_mission):
        return

    # Inject prompt with player's inquiry.
    # Here we can modify a prompt template with the player's message.
    # The bot.render_prompt receives two arguments: the prompt file (which should be in the same logic directory, 
    # though creators can use subfolders) and a list of arguments representing variables to be injected/replaced. 
    # In this case, there is only one variable: trigger_message, which is labeled player_inquiry.
    rendered_prompt = bot.render_prompt("prompt.md", player_inquiry=trigger_message)

    # Here is where we prompt the LLM to filter what the player wants. 
    # Notice that the bot is already set with the default LLM model via the cartridge's `main.py` file.
    ai_output = bot.prompt_ai(rendered_prompt)

    # Note this is the first instance where we are implementing decision making logic. 
    # Meaning here we choose the next node based on the LLM's answer.
    if ai_output == "t":
        bot.next_node("travel", short_memory)
    elif ai_output == "v":
        bot.next_node("visit-location", short_memory)
    elif ai_output == "c":
        bot.next_node("add-clues", short_memory)
    elif ai_output == "o":
        bot.next_node("outboundaries/start", short_memory)
    else:
        # If the LLM returns anything other than the expected characters, we treat it as a system error.
        short_memory["ai_output"] = ai_output
        bot.next_node("errors/ai/log", short_memory)
```

### Fuzzy Logic Strategy

**What is Fuzzy Logic?**
In traditional programming, logic is "binary" (true or false, 1 or 0). However, human language is messy and ambiguous. **Fuzzy Logic** allows a system to handle degrees of truth. By using an LLM as a "fuzzy" filter, we can translate an unpredictable human message into a predictable system command.

The strategy used in the `start` node accomplishes several critical goals:

* **Token Economy:** By forcing the LLM to output exactly one character (`t`, `v`, `c`, or `o`), we drastically reduce API costs and latency.
* **Predictability:** We take the "fuzzy" output of the LLM and immediately validate it against a hard-coded `if/else` block. This ensures that the application logic remains in the developer's control.
* **Error Segregation:** Notice the distinction between **Outboundary** (the player said something irrelevant) and **LLM Error** (the model failed to follow instructions). This allows for much more precise debugging.
* **State Decoupling:** The `short_memory` object allows you to pass specific context between nodes without cluttering the global state, keeping each node execution clean and focused.

### Start Node Prompt (`prompt.md`)

```markdown
# Player Intent Filter Prompt

You are a **strict intent classifier**.

Your task is to read the player’s inquiry and determine **their primary intention**, then reply with **exactly one character** that represents that intent.

## Player Inquiry
{{player_inquiry}}

## Intent Mapping (MANDATORY)
Reply with:
- **`t`** → if the player wants to **travel to another city**
- **`v`** → if the player wants to **visit or inspect a location within the current city**
- **`c`** → if the player wants to **add, report, submit, or register clues** for the case
- **`o`** → if none of the above clearly apply (ambiguous, conversational, or irrelevant).

## Output Rules (STRICT)
- Output **ONLY ONE CHARACTER**: `t`, `v`, `c`, or `o`
- No text, punctuation, or whitespace.
```

## General logic loop.

We exemplify here one way to use logic that mixes fuzzy logic with hard logic. You may find more complex examples on other nodes like "add-clues" in which tasks like, checking relevant clues, checking if the player is visiting a correct location and if everything was right, updating the memory and generating an output message to the player.

However, we detected a general recipe on can follow on each node.

- Node is invoqued -> run function of the `main.py` file relative to that node is called.
- Important data is loaded to infer ther current context.
- Prompt template is injected with necessary information.
- LLM model is inquired.
- LLM output is verified with hard logic if needed.
- Based on the LLM output, 3 things can happen
  - The reasoning execution call another node for further processing, ending the current node execution.
  - The current node sends the output generated by the LLM + any post treatment of such output to the user.
  - This same cycle is repeated for further evaluation on the same node (on the investigation game example, this happens on "add-clues" node for example).

### Summary: The Power of Hybrid Logic

This loop represents the core philosophy of Cogniconsole. By blending the strengths of Large Language Models with the reliability of standard programming, you gain the best of both worlds.

**The "Fuzzy" LLM Layer**
The LLM handles the high-variability tasks that traditional code struggles with. This includes interpreting the nuances of human intent (figuring out what a player actually wants) and generating creative, in-character outputs. Whether the bot is acting as a grizzled detective or a technical database assistant, the LLM provides the "persona" and the linguistic flexibility to keep the interaction natural and engaging.

**The "Hard" Programming Layer**
Standard programming logic provides the guardrails and the source of truth. It manages the mission limits, updates the persistent memory, and handles the routing between nodes. While the LLM can be creative with its words, the Python code ensures that the underlying data remains accurate and that the game mechanics (like tracking days spent on a case) are never hallucinated.

By mixing these two layers, you create AI agents that are deeply conversational and creatively expressive, yet remain strictly controllable and technically sound.

### Key Points for the Developer:

* **Creative but Constrained:** You can let the LLM write a beautiful description of a crime scene, but the Python logic ensures that the clue actually exists in the `_assets/` folder before the player can "find" it.
* **Interpretation and Action:** Use the LLM to parse the "messy" human message into a simple flag, then let the code take over the heavy lifting of state management and navigation.

# The Metabot

The **Metabot** is a specialized framework entity present in every cartridge. It resides in the reserved `_metabot/` directory and acts as the technical bridge between the Cogniconsole core library and your specific cartridge logic.

### Purpose and Philosophy
The Metabot was born from the need to manage shared resources and technical implementations that span the entire cartridge. Instead of introducing a new, complex "system layer" or high-level abstraction, we applied the same **Bot** architecture to these technical tasks. 

By using the Bot entity to handle the framework's internal plumbing, we reduce the number of concepts a developer needs to learn. In Cogniconsole, almost everything, from a character in a game to the API connector, is simply a Bot.

### Key Responsibilities
The Metabot is primarily responsible for setting up and maintaining the environment required for the cartridge to function properly. This includes:

* **API Orchestration**: Implementing and managing communication with external LLM providers like OpenAI, Ollama, Gemini, etc...
* **Global Resource Management**: Handling shared assets or configurations that need to be accessible across all specialists in the cartridge.
* **Core Communication**: Acting as the direct line of communication between the console's core library and the cartridge’s internal logic.

To put it simply: the Metabot handles the **infrastructure** so your specialists can focus on the **interaction**.

# Cartrigde initialization.

As mentioned, every cartridge has a `main.py` file in its root. Let's take a look at the investigation-game cartridge:

```python
import os
import sys
from pathlib import Path

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
```






















# Cartridge Initialization: The Bootloader

The `main.py` file at the root of your directory is the entry point for your application. It is responsible for checking environment variables, instantiating the bots, and managing the user input loop.

### Bootloader Implementation (`main.py`)

```python
import os
import sys
from pathlib import Path

# The core Bot class is the fundamental building block of every entity in Cogniconsole.
from cogniconsole.bot import Bot

def main():
    # Detect the physical location of the cartridge on the disk.
    cartridge_dir = Path(__file__).parent

    # Configuration: Determining which LLM provider the cartridge will use.
    # We pull these from environment variables to keep the cartridge code provider-agnostic.
    default_ml_model_api = os.getenv("COGNICONSOLE_DEFAULT_MODEL_API")

    # API Validation: Ensuring the necessary credentials/endpoints are available.
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

    # 1. Instantiate the Metabot.
    # The Metabot is unique; it doesn't have a parent 'metabot' and serves as the 
    # technical foundation for the rest of the cartridge.
    metabot = Bot(
        cartridges_path=cartridge_dir.parent,  # /cartridges
        cartridge_dir=cartridge_dir.name,      # "investigation-game"
        bot_name="_metabot",
        metabot=None,
        starting_node="start",
        output_callback=None
    )

    # Initialize the Metabot's logic.
    # We send an empty prompt to trigger the 'boot/start' logic of the infrastructure.
    metabot.prompt("")

    default_bot_listener = None
    
    # 2. Instantiate the Specialist (Agent's Boss).
    # Note that we pass the 'metabot' reference so this specialist can communicate with the API.
    bot_agents_boss = Bot(
        cartridges_path=cartridge_dir.parent,  # /cartridges
        cartridge_dir=cartridge_dir.name,      # "investigation-game"
        bot_name="agents-boss",
        metabot=metabot,
        starting_node="boot",
        default_ai_api_namespace=default_ml_model_api
    )

    # 3. Handle Conditional Logic (The Research Proxy).
    # Here we decide if the user interacts directly with the Boss or through a Logger.
    log_chats = os.getenv("COGNICONSOLE_LOG_CHATS")
    if not log_chats:
        # Standard Mode: The user speaks directly to the Boss.
        default_bot_listener = bot_agents_boss
        default_bot_listener.prompt("")

    else:
        # Research Mode: We instantiate a proxy bot to sit between the user and the Boss.
        bot_research_logger = Bot(
            cartridges_path=cartridge_dir.parent,
            cartridge_dir=cartridge_dir.name,
            bot_name="research_logger",
            metabot=metabot,
            starting_node="boot",
            default_ai_api_namespace=default_ml_model_api
        )

        # The 'link_bot' method allows one bot to hold a reference to another.
        # This allows the logger to pass messages forward to the Agent Boss.
        default_bot_listener = bot_research_logger
        default_bot_listener.link_bot("agents_boss", bot_agents_boss)

        # Initializing game.
        default_bot_listener.prompt("")

    # 4. The Interaction Loop.
    # This keeps the console open and listening for player input.
    def listen():
        try:
            text = input("> ").strip()
            if text == "_exit": # Internal command to close the console.
                return None
            return text
        except KeyboardInterrupt:
            print("\nExiting.")
            return None

    while True:
        user_input = listen()
        if user_input is None:
            break
        # Every input is sent to the 'default_bot_listener', which triggers the 
        # logic loop (Context -> Prompt -> LLM -> Hard Logic -> Resolution).
        default_bot_listener.prompt(user_input)

if __name__ == "__main__":
    main()
```

# Conclusion

You are now ready to build complex, scalable, and intelligent applications using the Cogniconsole framework. Happy coding!