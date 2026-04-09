from pathlib import Path
from .node_loader import _NodeLoader
from types import SimpleNamespace
import re


class Bot:
    """
    Standard utilities for Cogniconsole bots.

    Provides shared infrastructure such as node traversal, memory handling,
    and controlled LLM access. Bot-specific behavior is defined externally
    through a deterministic graph of logic nodes declared in the cartridge’s
    `_logic` directory structure of each bot.
    """
    def __init__(
        self,
        *,
        cartridges_path: Path,
        cartridge_dir: str,
        bot_name: str,
        metabot: "Bot | None",
        starting_node: str,
        output_callback = None,
        prompt_user_input = None,
        default_ai_api_namespace="ollama"
    ):
        """
        Initializes a Bot instance with the necessary info for node execution.

        Parameters:
            cartridges_path (Path): Absolute path to the directory containing cartridges.
            cartridge_dir (str): Directory name of the specific cartridge.
            bot_name (str): Name of the bot being instantiated.
            metabot (Bot | None): Reference to the system's _metabot instance.
            starting_node (str): Name of the node where execution begins.
            output_callback (callable, optional): Function to handle text output.
            prompt_user_input (callable, optional): Function to handle user input requested by the bot.
            default_ai_api_namespace (str): Default API provider (e.g., "ollama", "openai").
        """
        # Identity.
        self._cartridge_dir = cartridge_dir
        self._bot_name = bot_name
        self._starting_node = starting_node

        # Normalize and validate cartridges path.
        self._cartridges_path = cartridges_path.resolve()
        if not self._cartridges_path.exists():
            raise FileNotFoundError(
                f"Cartridge path does not exist: {self._cartridges_path}"
            )

        # Node loader.
        self._node_loader = _NodeLoader(
            cartridges_path=self._cartridges_path,
            cartridge_dir=self._cartridge_dir,
            bot_name=self._bot_name,
        )

        # Execution state.
        self._node_history: list[str] = [self._starting_node]

        # Stream-capable default output callback.
        self._output_callback = output_callback or None
        
        # Default input callback. Used when bots need some input from users.
        self._prompt_user_input = prompt_user_input or self.default_prompt_user_input

        # _metabot configuration and validation.
        if bot_name != "_metabot":
            if not (metabot and metabot.get_bot_name() == "_metabot"):
                raise ValueError(f"Bot '{bot_name}' requires a _metabot instance")
            self._metabot = metabot
        # If we are instantiating metabot, the metabot is the metabot of itself.
        else:
            self._metabot = self
        
        # Initialize API dictionary.
        self._api = SimpleNamespace()

        # Initialize the default AI api namespace.
        self._default_ai_api_namespace = default_ai_api_namespace

        # Dictionary of linked bots indexed by namespace.
        self._linked_bots = {}

    # Add a method to the API
    def add_to_api(self, name: str, entry):
        """
        Registers a method or object into the bot's internal API namespace.

        Parameters:
            name (str): The name to register.
            entry (any): The callable function or object to store.
        """
        setattr(self._api, name, entry)

    def api(self, entry_name: str, *args, **kwargs):
        """
        Accesses and executes a registered method or retrieves a registered object.

        Parameters:
            entry_name (str): The name of the API entry to access.
            *args: Positional arguments for callable entries.
            **kwargs: Keyword arguments for callable entries.

        Returns:
            any: The result of the callable or the retrieved object.
        """
        # Check if the attribute exists
        if not hasattr(self._api, entry_name):
            raise ValueError(f"API method or object '{entry_name}' not found.")
        
        attr = getattr(self._api, entry_name)
        
        # If it’s callable, call it with args/kwargs, else return the object
        if callable(attr):
            return attr(*args, **kwargs)
        else:
            return attr

    def get_bot_name(self):
        """
        Returns the name of the bot.

        Returns:
            str: The bot's name.
        """
        return self._bot_name
    
    def get_trigger_message(self):
        """
        Returns the message that triggered the current node cycle.

        Returns:
            str: The trigger message.
        """
        return self._trigger_message

    def prompt(self, msg = None):
        """
        Initial prompt that will trigger the bot to navigate the nodes and send a reply.

        Parameters:
            msg (str, optional): The user message to process.
        """

        # Registering original message.
        self._trigger_message = msg

        # Load the first node
        starting_node = self._node_loader.load(self._starting_node)
        starting_node.run(self, msg)

        self._node_history.clear()
        self._node_history.append(self._starting_node)

    def get_node_history(self):
        """
        Retrieves the sequence of nodes visited during the current execution.

        Returns:
            list[str]: A list of node names.
        """
        return self._node_history

    def set_starting_node(self, node_name: str):
        """
        Updates the starting node for future node cycles.

        Parameters:
            node_name (str): The name of the node to set as starting point.
        """
        self._starting_node = node_name

    def next_node(self, next_node: str, short_memory = None):
        """
        Transitions execution to the next specified node logic.

        Parameters:
            next_node (str): The name of the node to navigate to.
            short_memory (any, optional): Data to pass between nodes.
        """
        # Append to node history
        self._node_history.append(next_node)

        # Load the node (cached if already loaded)
        node = self._node_loader.load(next_node)

        # Execute the node's default run method
        node.run(self, short_memory)

    def default_output_callback(self, text: str):
        """
        Default output callback. Prints to terminal and supports streaming.

        Parameters:
            text (str): The text to be output.
        """
        if self._output_callback == None:
            print(text, end="", flush=True)
        else:
            self._output_callback(text)
    
    def default_prompt_user_input(self, prompt_text: str) -> str:
        """
        Default input callback. Used by default when the bot needs to ask a question to the user.

        Parameters:
            prompt_text (str): The question or prompt to display to the user.

        Returns:
            str: The user's input.
        """
        self._output_callback(prompt_text)

        # Read input from terminal
        answer = input()  # this blocks until user types something

        return answer

    def prompt_ai(
        self,
        message: str,
        *,
        stream: bool = False,
        output_callback = None,
        ai_api_namespace = None,
        **kwargs
    ):
        """
        Sends a request to the configured AI API through the metabot.

        Parameters:
            message (str): The prompt content for the AI.
            stream (bool): Whether to stream the response.
            output_callback (callable, optional): Override for handling output.
            ai_api_namespace (str, optional): The specific AI provider to use.
            **kwargs: Additional parameters for the AI model.

        Returns:
            any: The response from the AI API.
        """
        if output_callback is None:
            output_callback = self.default_output_callback

        if ai_api_namespace is None:
            if self._default_ai_api_namespace is None:
                raise ValueError(f"No AI api namespace argument was passed and there is no default api model set.")
            ai_api_namespace = self._default_ai_api_namespace
        
        if not hasattr(self._metabot._api, ai_api_namespace):
            raise ValueError(f"API for given AI namespace '{ai_api_namespace}' not found in the metabot's api registry.")

        return self._metabot.api(ai_api_namespace).prompt_ai(
            message,
            stream,
            output_callback,
            **kwargs
        )

    def render_prompt(self, prompt_path: str, **kwargs) -> str:
        """
        Reads a prompt file and replaces template placeholders with provided values.

        Parameters:
            prompt_path (str): Relative path to the prompt template file within the node.
            **kwargs: Values to fill into placeholders (e.g., {{variable_name}}).

        Returns:
            str: The rendered prompt string.
        """
        # Construct full path relative to current node's _logic directory
        base_path = (
            self._cartridges_path
            / self._cartridge_dir
            / "_bots"
            / self._bot_name
            / "_logic"
            / self._node_history[-1]
        )
        full_path = base_path / prompt_path

        if not full_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {full_path}")

        # Read the prompt file
        with open(full_path, "r", encoding="utf-8") as f:
            prompt_text = f.read()

        # Regex to match {{variable_name}}
        pattern = re.compile(r"\{\{\s*(\w+)\s*\}\}")

        # Replace each match with corresponding value from kwargs
        def replacer(match):
            key = match.group(1)
            return str(kwargs.get(key, match.group(0)))  # fallback: keep placeholder

        return pattern.sub(replacer, prompt_text)

    def prompt_user(self, prompt_text: str) -> str:
        """
        Requests input from the user via the configured input callback.

        Parameters:
            prompt_text (str): The text to display to the user.

        Returns:
            str: The user's input string.
        """
        return self._prompt_user_input(prompt_text)

    def asset_load(self, filename: str):
        """
        Loads the contents of a file from the bot's _assets directory.

        Parameters:
            filename (str): The name of the file to load.

        Returns:
            str | None: File content as a string, or None if the file doesn't exist.
        """
        file_path = self._cartridges_path / self._cartridge_dir / "_bots" / self._bot_name / "_assets" / filename
        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def memory_load(self, filename: str):
        """
        Loads the contents of a file from the bot's _memory directory.

        Parameters:
            filename (str): The name of the file to load.

        Returns:
            str | None: File content as a string, or None if the file doesn't exist.
        """
        file_path = self._cartridges_path / self._cartridge_dir / "_bots" / self._bot_name / "_memory" / filename
        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def memory_save(self, filename: str, content: str, append = False):
        """
        Saves content to a file within the bot's _memory directory.

        Parameters:
            filename (str): The name of the file to save.
            content (str): The string content to write.
            append (bool): If True, appends to the file; otherwise overwrites.
        """
        base_path = (
            self._cartridges_path
            / self._cartridge_dir
            / "_bots"
            / self._bot_name
            / "_memory"
        )

        file_path = base_path / filename

        # Ensure all parent directories exist.
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Selecting file open mode.
        open_mode = "w"
        if append:
            open_mode = "a"

        # Write file.
        with open(file_path, open_mode, encoding="utf-8") as f:
            f.write(content)

    def memory_erase(self, filename: str) -> bool:
        """
        Deletes a specific file from the bot's _memory directory.

        Parameters:
            filename (str): The name of the file to erase.

        Returns:
            bool: True if the file was successfully deleted, False if it didn't exist.

        Raises:
            ValueError: If the path exists but is not a file.
        """
        base_path = (
            self._cartridges_path
            / self._cartridge_dir
            / "_bots"
            / self._bot_name
            / "_memory"
        )

        file_path = base_path / filename

        if not file_path.exists():
            return False

        if not file_path.is_file():
            raise ValueError(f"Memory path is not a file: {file_path}")

        file_path.unlink()
        return True

    def set_default_output_callback(self, output_callback):
        """
        Overrides the default output callback for this bot instance.

        Parameters:
            output_callback (callable): The function to handle text output.
        """
        self._output_callback = output_callback

    def set_default_prompt_user_input(self, prompt_user_input):
        """
        Overrides the default user input callback for this bot instance.

        Parameters:
            prompt_user_input (callable): The function to handle user input requests.
        """
        self._prompt_user_input = prompt_user_input

    def link_bot(self, name: str, bot: "Bot"):
        """
        Links another Bot instance to this bot under a specific namespace.

        Parameters:
            name (str): The namespace key to identify the linked bot.
            bot (Bot): The Bot instance to link.

        Raises:
            ValueError: If the namespace is empty.
            TypeError: If the provided object is not a Bot instance.
            KeyError: If the namespace is already in use.
        """
        # Validate namespace.
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Namespace must be a non-empty string")

        # Validate bot instance.
        if not isinstance(bot, Bot):
            raise TypeError(f"Expected Bot instance, got {type(bot).__name__}")

        # Prevent overwriting existing namespace.
        if name in self._linked_bots:
            raise KeyError(f"Bot namespace '{name}' already exists")

        # Link the bot.
        self._linked_bots[name] = bot

    def get_linked_bot(self, name: str) -> "Bot":
        """
        Retrieves a previously linked Bot instance by its namespace.

        Parameters:
            name (str): The namespace key of the linked bot.

        Returns:
            Bot: The linked Bot instance.

        Raises:
            ValueError: If the namespace string is invalid.
            KeyError: If the namespace is not found in the linked registry.
        """
        # Validate namespace.
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Namespace must be a non-empty string")

        # Check existence.
        if name not in self._linked_bots:
            raise KeyError(f"Bot namespace '{name}' is not linked")

        return self._linked_bots[name]