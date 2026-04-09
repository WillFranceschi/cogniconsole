import os
from openai import OpenAI

# Initialize OpenAI client using environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Default model parameters
DEFAULT_MODEL = "gpt-4o"
DEFAULT_MAX_TOKENS = 512
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9

def prompt(
    message: str,
    stream: bool = False,
    output_callback=None,
    **kwargs
) -> str | None:
    """
    Minimal OpenAI GPT API wrapper for stateless prompt generation.

    Args:
        message (str): The prompt to send.
        stream (bool): If True, output_callback is called for each chunk.
        output_callback (callable, optional): Function to receive streamed text.
            Should accept (text: str, stream: bool).
        **kwargs: Optional model parameters like model, max_tokens, temperature, top_p, etc.

    Returns:
        str | None: Full response if stream=False, else None.
    """
    model = kwargs.get("model", DEFAULT_MODEL)
    max_tokens = kwargs.get("max_tokens", DEFAULT_MAX_TOKENS)
    temperature = kwargs.get("temperature", DEFAULT_TEMPERATURE)
    top_p = kwargs.get("top_p", DEFAULT_TOP_P)

    response_text = ""

    try:
        if stream:
            # Streaming response.
            stream_response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": message}],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stream=True
            )

            for chunk in stream_response:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        text = delta.content
                        response_text += text
                        if output_callback:
                            output_callback(text)

            # Signal end of stream.
            if output_callback:
                output_callback("")

            return None
        else:
            # Non-streaming response.
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": message}],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
            # Extract the content from first choice.
            response_text = completion.choices[0].message.content
            return response_text

    except Exception as e:
        if output_callback:
            output_callback(f"\n[OpenAI Error: {e}]\n")
        return None
