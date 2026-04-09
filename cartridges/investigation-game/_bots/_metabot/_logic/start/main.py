import os
import importlib.util
from pathlib import Path
from types import SimpleNamespace

initiated = False

def run(metabot, short_memory):
    """
    _metabot start node.
    Loads shared resources like the Ollama API.
    This node is executed once per cartridge.
    """
    global initiated
    if initiated:
        return
    initiated = True

    default_model_api = os.getenv("COGNICONSOLE_DEFAULT_MODEL_API")

    start_node_path = Path(__file__).parent

    if default_model_api == "ollama":

        # --- Path to the ollama.py file relative to this start/main.py. ---
        ollama_path = start_node_path.parent.parent / "_assets" / "_aimodel-apis" / "ollama.py"

        if not ollama_path.exists():
            raise FileNotFoundError(f"Ollama API not found at {ollama_path}")

        # --- Dynamically load the module. ---
        spec = importlib.util.spec_from_file_location("_metabot_ollama_api", ollama_path)
        ollama_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ollama_module)

        # Creating the metabot prompt_ai api method.
        def ollama_prompt_ai(
            message: str,
            stream: bool = False,
            output_callback = None,
            **kwargs
        ):
            return ollama_module.prompt(
                message,
                stream,
                output_callback,
                **kwargs
            )
        ollama_ns = SimpleNamespace()
        ollama_ns.prompt_ai = ollama_prompt_ai
        metabot.add_to_api("ollama", ollama_ns)

    elif default_model_api == "openai":

        # --- Path to the openai.py file relative to this start/main.py. ---
        openai_path = start_node_path.parent.parent / "_assets" / "_aimodel-apis" / "openai.py"

        if not openai_path.exists():
            raise FileNotFoundError(f"Openai API not found at {openai_path}")

        # --- Dynamically load the module ---
        spec = importlib.util.spec_from_file_location("_metabot_openai_api", openai_path)
        openai_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(openai_module)

        # Creating the metabot prompt_ai api method.
        # We know we could merge togeter ollama_promptLLm and openaiPromptLLm.
        # but that would require thinking about "more data structures".
        # for now the linear module and load creation will suffice.
        # we have other priorities to focus at the moment and the current solution will work transparently for cartridge creators.
        # However it is something to improve in future versions.
        def openai_prompt_ai(
            message: str,
            stream: bool = False,
            output_callback = None,
            **kwargs
        ):
            return openai_module.prompt(
                message,
                stream,
                output_callback,
                **kwargs
            )

        openai_ns = SimpleNamespace()
        openai_ns.prompt_ai = openai_prompt_ai
        metabot.add_to_api("openai", openai_ns)
