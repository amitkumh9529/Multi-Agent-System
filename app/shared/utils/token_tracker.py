
from typing import Any, Dict, List, Optional
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

class TokenUsageTracker(BaseCallbackHandler):
    """
    Callback Handler che aggrega l'utilizzo dei token da tutte le chiamate LLM.
    """
    def __init__(self):
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.successful_requests = 0

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Eseguito quando una chiamata LLM termina."""
        if response.llm_output:
            # Alcuni provider mettono i token qui (es. OpenAI)
            token_usage = response.llm_output.get("token_usage")
            if token_usage:
                self.total_tokens += token_usage.get("total_tokens", 0)
                self.prompt_tokens += token_usage.get("prompt_tokens", 0)
                self.completion_tokens += token_usage.get("completion_tokens", 0)
                self.successful_requests += 1
                return

        # Fallback: controlliamo le generazioni (es. ChatBedrock)
        if response.generations:
            for generation_list in response.generations:
                for generation in generation_list:
                    if generation.message and hasattr(generation.message, "usage_metadata"):
                        usage = generation.message.usage_metadata
                        if usage:
                            self.total_tokens += usage.get("total_tokens", 0)
                            self.prompt_tokens += usage.get("input_tokens", 0)
                            self.completion_tokens += usage.get("output_tokens", 0)
                            self.successful_requests += 1
