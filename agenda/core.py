import openai
import requests

class SiliconFlowTool:
    def __init__(self):
        self.api_key = "sk-pqlgknchwqqmkafxqsvdfiiryujimuemsasskrcsmcnyowtu"
        self.base_url = "https://api.siliconflow.com/v1"

    def run(self, messages, model="Qwen/QwQ-32B", temperature=0.7, max_tokens=1024, user_id=None, system_prompt=None):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            "messages": [],
        }
        if user_id:
            payload["user_id"] = user_id
        if system_prompt:
            payload["messages"].append({"role": "system", "content": system_prompt})
        payload["messages"].extend(messages)
        response = requests.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

# Example usage with OpenAI-like interface
class SiliconFlowOpenAIAdapter:
    def __init__(self):
        self.tool = SiliconFlowTool("sk-pqlgknchwqqmkafxqsvdfiiryujimuemsasskrcsmcnyowtu")

    def Completion_create(self, **kwargs):
        messages = kwargs.get("messages")
        model = kwargs.get("model", "Qwen/QwQ-32B")
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1024)
        user_id = kwargs.get("user_id")
        system_prompt = kwargs.get("system_prompt")
        content = self.tool.run(messages, model, temperature, max_tokens, user_id, system_prompt)
        return {"choices": [{"message": {"content": content}}]}