# The Console: Core Engine & CLI

The **Console** is the backbone of the Cogniconsole framework. It acts as the virtual "hardware" that loads cartridges, manages bot states, and provides the essential utilities for both deterministic logic and AI interactions.

---

## 1. CLI Entry Point (`main.py`)

The command-line interface is designed to be a dynamic bootloader. It allows you to run any cartridge without needing to modify the core library or reinstall the package.

### Usage
`$ cogniconsole <path-to-cartridge-folder>`

### Execution Logic

1.  **Path Validation:** The CLI verifies that the provided path exists and contains a valid `main.py`.
2.  **Dynamic Import:** Using `importlib`, the console loads the cartridge's `main.py` as a module at runtime.
3.  **Handover:** It searches for a `main()` function within the cartridge. If found, it executes it, passing control of the session to your custom implementation.

-----

## 2  The Node Loader (`node_loader.py`)

The `_NodeLoader` is a private, lazy-loading utility that handles the "logic modules" of a bot. It is optimized for performance and memory isolation.

### Key Features

* **Lazy Loading:** Nodes are not loaded into memory until they are explicitly called by the `Bot` class.
* **Module Caching:** To ensure performance, every loaded node is cached in an internal dictionary. This avoids redundant disk I/O.
* **Isolation via Unique Namespaces:** Each node is imported with a unique internal name (`cogniconsole_<cartridge>-<bot>-<node>`). This allows multiple bots to run simultaneously even if they have nodes with identical filenames.
* **Memory Management:** The `unload_nodes()` method can be called to clear the cache, ensuring the system stays lean during long sessions.

-----

## 3 The Bot Class (`bot.py`)

The `Bot` class is the primary toolkit for developers. It provides the methods necessary to navigate logic, manage memory, and communicate with AI models.

### Node Navigation & Flow

  * `prompt(msg)`: The primary entry point to trigger a bot's logic cycle.
  * `next_node(node_name, short_memory)`: Transitions the execution to a specific node, passing optional data through `short_memory`.
  * `set_starting_node(node_name)`: Dynamically changes where the bot begins its next interaction cycle.

### Extensible API System

The Bot uses a `SimpleNamespace` called `_api` to allow modular extensions:

  * **Registration:** `add_to_api(name, entry)` allows you to attach custom functions or objects (like database connectors or external service wrappers) directly to the bot.
  * **Execution:** `api(entry_name, *args, **kwargs)` invokes these registered tools from within any node.

### Memory & Assets

The Bot class enforces a strict schema for file management:

  * **Short-term:** Managed via variables passed between nodes.
  * **Persistent:** \* `memory_save(filename, content, append)`: Writes data to the bot's `_memory` folder.
      * `memory_load(filename)`: Reads stored data.
      * `memory_erase(filename)`: Deletes persistent records.
  * **Assets:** `asset_load(filename)` provides read-only access to static files in the `_assets` folder.

### AI Orchestration

  * `prompt_ai(...)`: Routes AI requests through the **Metabot**.
  * `render_prompt(path, **kwargs)`: A templating engine that loads text files and replaces `{{variable}}` placeholders with dynamic data before sending them to the AI.

-----

## 4 The Metabot Architecture

In Cogniconsole, every bot exists within a hierarchy:

  * **The Metabot:** A specialized Bot instance that acts as the "System Administrator." It typically holds the API registrations for providers like OpenAI or Ollama.
  * **Agent Bots:** Standard bots that perform specific tasks. They require a reference to the Metabot to access shared AI resources and global configurations.

-----

## 5 Directory Schema Requirements

For the Console and Node Loader to function, your cartridge must follow this structure:

```
_bots/
└── <bot_name>/
    ├── _logic/      # Directory for nodes (each with its own main.py)
    ├── _assets/     # Static, read-only data
    └── _memory/     # Persistent, read/write data
```

-----

> **Next Step:** To learn how to structure your Python logic within these nodes, proceed to the [Cartridges Documentation](cartridges.md).
