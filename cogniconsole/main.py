"""
Main entry point for the Cogniconsole CLI.
This script handles the dynamic loading and execution of cartridges.
"""

import importlib.util
import sys
from pathlib import Path

def main():
    """
    Parses CLI arguments and executes the main function of a specified cartridge.
    """
    if len(sys.argv) < 2:
        print("Usage: cogniconsole <cartridge-path>")
        sys.exit(1)

    cartridge_path = Path(sys.argv[1])
    if not cartridge_path.exists():
        print(f"Cartridge path does not exist: {cartridge_path}")
        sys.exit(1)

    # Dynamic import
    spec = importlib.util.spec_from_file_location("cartridge_main", cartridge_path / "main.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Call the cartridge main() function
    if hasattr(module, "main"):
        module.main()
    else:
        print("Cartridge main.py has no 'main' function.")

if __name__ == "__main__":
    main()