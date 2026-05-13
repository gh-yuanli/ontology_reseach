import json
import os
import re


class ResultProcessor:
    @staticmethod
    def parse_response(content: str) -> dict:
        pattern = r"```(?:json)?\s*\n?(.*?)```"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except Exception:
                return {}
        return {}

    def collect(self, responses: list[str], ts: str) -> list[dict]:
        results = []
        for content in responses:
            parsed = self.parse_response(content)
            if parsed:
                results.append(parsed)

        out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", ts)
        os.makedirs(out_dir, exist_ok=True)
        results_path = os.path.join(out_dir, "results.json")
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"产品推荐结果已存入 {results_path}")

        return results