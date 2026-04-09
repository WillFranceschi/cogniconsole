import importlib.util
import sys
from pathlib import Path

class _NodeLoader:
    """
    Private helper to lazily load node scripts following the Cogniconsole cartridge schema.
    """

    def __init__(self, cartridges_path: Path, cartridge_dir: str, bot_name: str):
        """
        Initializes the node loader with specific cartridge and bot context.

        Parameters:
            cartridges_path (Path): Base filesystem path for cartridges.
            cartridge_dir (str): Name of the cartridge directory.
            bot_name (str): Name of the bot.
        """
        self._cartridge_dir = cartridge_dir
        self._bot_name = bot_name
        self._base_path = cartridges_path / cartridge_dir / "_bots" / bot_name / "_logic"
        self._cache = {}

        # Enforce directory existence.
        if not self._base_path.exists():
            raise FileNotFoundError(f"Bot logic directory does not exist: {self._base_path}")

    def _cache_key(self, node_name: str) -> str:
        """
        Generates a unique cache key for a specific node.

        Parameters:
            node_name (str): Name of the node.

        Returns:
            str: The generated cache key.
        """
        return f"{self._cartridge_dir}-{self._bot_name}-{node_name}"

    def load(self, node_name: str):
        """
        Load a node script (main.py) dynamically.

        Parameters:
            node_name (str): The node directory name.

        Returns:
            module: The loaded Python module.
        """
        key = self._cache_key(node_name)
        if key in self._cache:
            return self._cache[key]

        # Construct path to main.py.
        script_path = self._base_path / node_name / "main.py"

        if not script_path.exists():
            raise FileNotFoundError(f"Node '{node_name}' not found at {script_path}")

        # Unique module name for importlib.
        module_name_unique = f"cogniconsole_{key}"
        spec = importlib.util.spec_from_file_location(module_name_unique, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Cache the module
        self._cache[key] = module
        return module

    def unload_nodes(self):
        """
        Unload all node modules belonging to this bot.
        """
        prefix = f"{self._cartridge_dir}-{self._bot_name}"

        keys_to_remove = [
            key for key in self._cache
            if key.startswith(prefix)
        ]

        for key in keys_to_remove:
            module_name = f"cogniconsole_{key}"
            sys.modules.pop(module_name, None)
            del self._cache[key]
    
    # Dev / maintenance helpers
    def list_loaded_nodes(self):
        """
        Dev helper: list cached node keys.

        Returns:
            list: List of cached keys.
        """
        return list(self._cache.keys())