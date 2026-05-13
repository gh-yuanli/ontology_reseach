import json
import os
import random
from typing import Optional

from openai import OpenAI
from tqdm import tqdm


class LLMCaller:
    def __init__(self, api_key: str, base_url: str = "https://api.minimaxi.com/v1"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def call(self, prompt: str, model: str = "MiniMax-M2.7") -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def batch_inference(
        self,
        client_infos: list[dict],
        prompt_builder,
        model: str = "MiniMax-M2.7",
        sample_size: Optional[int] = None,
        ts: str = "",
        seed: int = 42,
    ) -> list[dict]:
        targets = random.sample(client_infos, sample_size) if sample_size else client_infos
        results = []
        prompts  = []
        for info in tqdm(targets, desc="产品推荐中..."):
            prompt = prompt_builder(info)
            content = self.call(prompt, model=model)
            results.append(content)
            prompts.append(prompt)

        out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", ts)
        os.makedirs(out_dir, exist_ok=True)
        prompts_path = os.path.join(out_dir, "prompts.json")
        with open(prompts_path, "w", encoding="utf-8") as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)

        print(f"客户提示词已存入 {prompts_path}")

        return results