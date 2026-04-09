# Getting Started with Cogniconsole

Welcome to **Cogniconsole**. This guide will help you understand the framework's architecture and how to get your first AI bot running.

---

## 1. Core Concept & Philosophy
Cogniconsole is heavily inspired by **classic video-game architecture**. 

* **The Console (The Library):** This is the core engine you installed via pip. It provides the "hardware" and system utilities—module loading (`node_loader`), the base `Bot` class, memory management, and API integration tools.
* **The Cartridge (The Implementation):** This is the "software" created by the developer. A cartridge contains the specific logic, story, or task-oriented nodes. 

This separation allows flexibility; the same engine can run a complex murder-mystery game, a personal research assistant, or a technical support bot. For a deep dive into building these, see the [Cartridge Documentation](cartridges.md).

## 2. Advantages of using Cogniconsole

* **Lightweight Core:** The library is designed to be lean with minimal external dependencies. As the library evolves, we strive to keep this footprint as small as possible.
* **Clear Guideline Structure:** A standardized framework for creating cartridges ensures your AI projects stay organized and maintainable.
* **Model Agnostic & Multimodal:** Multiple AI models (e.g., OpenAI and Ollama) can be used simultaneously within the same cartridge.
* **Decoupled Prompts:** Prompts are separated from the core logic, allowing them to be modified dynamically based on specific user inputs.
* **Memory Management:** Built-in capabilities for managing both short-term (session-based) and long-term (persistent) memory, allowing bots to retain context over time.
* **Extensible "Bot-API" System:** Each Bot features an internal API layer, allowing it to be extended with specialized capabilities without bloating the base class. 
    * **External Integration:** Connect bots to services like Stripe for payments, Google Calendar for scheduling, or Slack for notifications.
    * **Inter-Bot Communication:** Bots can interact with one another via API commands, enabling complex multi-agent workflows tailored to the developer's needs.
* **Chat Logging:** Built-in support for saving detailed logs of chat sessions for debugging or analysis.
* **Programmatic Validation:** AI model answers can be checked and validated through "hard logic" to ensure reliability.
* **Collaborative Development:** The architecture’s modularity allows multiple developers to work on the same cartridge at the same time without merge conflicts.
* **Separation of Logic:** Distinct separation between "fuzzy logic" (AI reasoning) and "hard logic" (fixed code), providing better control over bot behavior.

## 3. Future Improvements & Roadmap

While the library is already stable and production-ready, we have a clear path for future enhancements:

* **Web API & Interface:** Our top priority is currently under development—transitioning from a CLI-only tool to a full Web API. This will allow developers to host cartridges as web services and interact with them via a dedicated UI.
* **Expanded Model Support:** We plan to integrate additional AI provider APIs to offer more choice, including:
    * **Google Gemini** (Pro and Flash)
    * **Anthropic Claude**
    * **Mistral AI**
    * **Groq**
* **Core Hardening:** Continuous improvements to the core library focusing on high-performance module loading, more robust error handling for API failures, and enhanced security for cartridge execution.
* **Cartridge Ecosystem & Feature Discovery:** By developing a wider variety of example cartridges (from RPGs to productivity tools), we will identify and extract common patterns to be added as standard features in the core library.

## 4. Next Steps

Ready to build? Dive into the rest of our documentation to master the system:

* **[The Console](console.md):** Deep dive into the CLI, installation, and environment configuration.
* **[Cartridges](cartridges.md):** Detailed technical guide on folder structures, nodes, and building logic.
* **[Author's Notes](authors-notes.md):** The story behind the project and specific design choices.