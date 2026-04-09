import os
import requests
import json

# Default API parameters
DEFAULT_MODEL = os.getenv("COGNICONSOLE_OLLAMA_DEFAULT_MODEL")# "e.g.: deepseek-r1:latest"
DEFAULT_API_URL = os.getenv("COGNICONSOLE_OLLAMA_DEFAULT_API_URL")# "e.g.: http://192.168.8.126:11434/api/generate"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_K = 40
DEFAULT_TOP_P = 0.9
DEFAULT_MAX_TOKENS = 512

def prompt(
    message: str,
    stream: bool = False,
    output_callback = None,
    **kwargs
) -> str | None:
    """
    Minimal Ollama API wrapper for stateless prompt generation.

    Args:
        message (str): The prompt to send.
        stream (bool): If True, output_callback is called for each chunk.
        output_callback (callable, optional): Function to receive streamed text.
            Should accept (text: str, stream: bool).
        **kwargs: Optional model parameters like temperature, top_k, top_p, max_tokens, model, api_url, etc.

    Returns:
        str | None: Full response if stream=False, else None.
    """
    # Determine final values for parameters, using kwargs if present
    model = kwargs.get("model", DEFAULT_MODEL)
    api_url = kwargs.get("api_url", DEFAULT_API_URL)
    temperature = kwargs.get("temperature", DEFAULT_TEMPERATURE)
    top_k = kwargs.get("top_k", DEFAULT_TOP_K)
    top_p = kwargs.get("top_p", DEFAULT_TOP_P)
    max_tokens = kwargs.get("max_tokens", DEFAULT_MAX_TOKENS)

    response_text = ""

    try:
        r = requests.post(
            api_url,
            json={
                "model": model,
                "prompt": message,
                "stream": stream,
                "temperature": temperature,
                "top_k": top_k,
                "top_p": top_p,
                "max_tokens": max_tokens,
                **kwargs  # forward any extra options to the API
            },
            stream=stream,
            timeout=300
        )

        if stream:
            # Stream each chunk through the callback
            for line in r.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    response_text += chunk
                    if output_callback:
                        output_callback(chunk)

            # Signal end of stream
            if output_callback:
                output_callback("")

            return None

        else:
            # Non-streaming: get full response
            data = r.json()
            response_text = data.get("response", "")
            return response_text

    except Exception as e:
        if output_callback:
            output_callback(f"\n[Error: {e}]\n")
        return None