# Cogniconsole
> A Python framework for building structured, controllable AI bots

# Installation and Usage

Run `pip install cogniconsole`.  
This is the main library. It is the core that allows developers to create their own cartridges using its utilities.

After installing it, visit: `https://github.com/WillFranceschi/cogniconsole`

Download the `cartridges/investigation-game/` directory.

Inside the investigation game directory, you will find a `.env` file with the necessary environment variables.  
This file contains:
```
# Choose your default model api. It can be "ollama" or "openai"
export COGNICONSOLE_DEFAULT_MODEL_API="openai"

# If on COGNICONSOLE_DEFAULT_MODEL_API you chose "ollama"...
# export COGNICONSOLE_OLLAMA_DEFAULT_MODEL="deepseek-r1:latest"
# export COGNICONSOLE_OLLAMA_DEFAULT_API_URL="http://192.168.8.126:11435/api/generate"

# If on COGNICONSOLE_DEFAULT_MODEL_API you chose "openai"...
export OPENAI_API_KEY="<your-open-ai-key>"

# Uncomment the following envvar if you want to save the chats.
# export COGNICONSOLE_LOG_CHATS=1
```

Alternatively, you can export these variables one by one depending on your operating system.

After adding the environment variables to your terminal:  
- If you are using "ollama", you will need to install `requests` as a dependency: `pip install requests`  
- If you are using "openai", you will need to install `openai` as a dependency: `pip install openai`

After that setup, run:  
`cogniconsole <path-to-investigation-game-dir-you-downloaded-from-github>`

If everything is set up correctly, the game will start.

This is a simple text-based game in which the main goal is to demonstrate Cogniconsole's capabilities and serve as an example for developers to create their own cartridges.  
In it, you will find prompt examples, how to utilize each resource, and common examples of logic handling.

# What is Cogniconsole?

**Cogniconsole** is a Python library for building structured, controllable AI bots.

It provides developers with a framework to manage prompts, interact with multiple models, enforce execution constraints, and organize bot behavior in a predictable and reusable way.

Instead of treating AI interactions as loose prompt chains, Cogniconsole introduces a disciplined architecture inspired by video games:

- The **console** (the library) provides the runtime, tools, and rules.  
- Developers build **cartridges** — self-contained modules that define specific bot behaviors, tasks, and constraints.  
- Each cartridge can run multiple **bots**, which are execution instances following the cartridge’s logic.  

> In standard AI terminology, bots are often called **agents**. We use the term **bot** to emphasize that multiple bots can run per cartridge.

Each cartridge follows a predefined structure, making bots easier to develop, test, reuse, and share.

# Why Cogniconsole?
This approach allows developers to:

- Precisely control how and when models are used.
- Combine multiple models within a single workflow.
- Encapsulate logic into modular, portable units.
- Avoid the chaos of unstructured prompt engineering.

Cogniconsole is designed for developers who want **fine-grained control over AI systems**, without sacrificing flexibility.

# Project Structure
```text
/project-folder
│
├── cogniconsole/        # Core library
├── cartridges/          # Example cartridges
│   └── investigation-game/
├── docs/                # Documentation
├── README.md
└── LICENSE
```

# Documentation
[Start here](docs/start-here.md)

# Contributing
Contributions are welcome. Please open an issue or submit a pull request.

# License
This project is licensed under the MIT License.
