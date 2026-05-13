import json
import os
from datetime import datetime

import pandas as pd


class Evaluator:
    def __init__(self, result_dir: str):
        self.result_dir = result_dir

    def load_ground_truth(self, sample_path: str) -> pd.DataFrame:
        df = pd.read_excel(sample_path)
        return df[["appnt_id_no", "cvrg_cd", "cvrg_name"]].drop_duplicates()

    def load_results(self, path: str) -> list[dict]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def build_recommendations(self, results: list[dict], top_n: int = None):
        client_products = []
        for item in results:
            app_id = item.get("appnt_id_no")
            tel_no = item.get("tel_no")
            result = item.get("predict_results")

            product_combo = [(ref["险种代码"], ref["险种名称"]) for ref in result]

            if top_n:
                product_infos = product_combo[:top_n]
                for product_info in product_infos:
                    client_product = (app_id, tel_no, int(product_info[0]), product_info[1])

                    client_products.append(client_product)

        return client_products

    def compute_hit(self, recommendations: list, ground_truth: pd.DataFrame) -> pd.DataFrame:
        check_df = pd.DataFrame(recommendations, columns=["appnt_id_no", "tel_no", "cvrg_cd", "cvrg_name"])

        merged = check_df.merge(
            ground_truth[["appnt_id_no", "cvrg_cd"]],
            on=["appnt_id_no", "cvrg_cd"],
            how="left",
            indicator=True,
        )
        merged["is_hit"] = merged["_merge"] == "both"
        merged.rename(columns = {"cvrg_cd":"predicted_cvrg_cd", "cvrg_name":"predicted_cvrg_name"}, inplace=True)

        merged = merged.merge(
            ground_truth[["appnt_id_no", "cvrg_cd", "cvrg_name"]],
            on="appnt_id_no",
            how="left"
        )
        merged.rename(columns = {"cvrg_cd":"actual_cvrg_cd", "cvrg_name":"actual_cvrg_name"}, inplace=True)
        return merged[["appnt_id_no", "tel_no", "predicted_cvrg_cd", "predicted_cvrg_name", "is_hit", "actual_cvrg_cd", "actual_cvrg_name"]]

    def precision(self, hit_df: pd.DataFrame) -> float:
        return hit_df[hit_df["is_hit"] == 1].appnt_id_no.nunique() / hit_df.appnt_id_no.nunique()

    def _hit_user_count(self, hit_df: pd.DataFrame) -> int:
        return int(hit_df[hit_df["is_hit"] == 1].appnt_id_no.nunique())

    def _total_user_count(self, hit_df: pd.DataFrame) -> int:
        return int(hit_df.appnt_id_no.nunique())

    @staticmethod
    def _format_console_evaluation_table(
        top1_hits: int,
        top1_total: int,
        top3_hits: int,
        top3_total: int,
        p1: float,
        p3: float,
    ) -> str:
        h0, h1, h2 = "维度", "Top1", "Top3"
        rows = [
            ("命中客户数（至少一条推荐与真实险种一致）", str(top1_hits), str(top3_hits)),
            ("参与评估的客户总数", str(top1_total), str(top3_total)),
            ("客户级准确率", f"{p1:.1%}", f"{p3:.1%}"),
        ]
        w0 = max(len(h0), max(len(r[0]) for r in rows))
        w1 = max(len(h1), max(len(r[1]) for r in rows))
        w2 = max(len(h2), max(len(r[2]) for r in rows))

        def horizontal() -> str:
            return f"+{'-' * (w0 + 2)}+{'-' * (w1 + 2)}+{'-' * (w2 + 2)}+"

        width = len(horizontal())
        out = [
            "=" * width,
            "评估结果".center(width),
            "=" * width,
            horizontal(),
            f"| {h0:<{w0}} | {h1:^{w1}} | {h2:^{w2}} |",
            horizontal(),
        ]
        for a, b, c in rows:
            out.append(f"| {a:<{w0}} | {b:>{w1}} | {c:>{w2}} |")
        out.append(horizontal())
        return "\n".join(out)

    def _write_evaluation_markdown(
        self,
        report_path: str,
        hit_top1_path: str,
        hit_top3_path: str,
        top1_hits: int,
        top1_total: int,
        top3_hits: int,
        top3_total: int,
        p1: float,
        p3: float,
    ) -> None:
        lines = [
            "# 推荐结果评估报告",
            "",
            f"> 生成时间：`{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
            "",
            "本报告汇总 **Top1** 与 **Top3** 推荐相对真实保单的命中情况；明细数据已导出为同目录下的 Excel 文件。",
            "",
            "---",
            "",
            "## 核心指标一览",
            "",
            "| 维度 | Top1 | Top3 |",
            "|------|------|------|",
            f"| 命中客户数（至少一条推荐与真实险种一致） | **{top1_hits}** | **{top3_hits}** |",
            f"| 参与评估的客户总数 | {top1_total} | {top3_total} |",
            f"| 客户级准确率 | **{p1:.1%}** | **{p3:.1%}** |",
            "",
            "### 指标说明",
            "",
            "- **命中客户数**：在对应 TopN 推荐中，至少有一条预测的险种代码与 ground truth 中该客户实际购买的险种代码一致的客户人数（按 `appnt_id_no` 去重）。",
            "- **准确率**：命中客户数 ÷ 参与评估的客户总数。",
            "",
            "---",
            "",
            "## 明细文件路径",
            "",
            "以下文件与本报告位于同一目录，可直接用 Excel 打开核对逐单明细。",
            "",
            "| 内容 | 文件名 |",
            "|------|--------|",
            f"| Top1 推荐与命中明细 | `{os.path.basename(hit_top1_path)}` |",
            f"| Top3 推荐与命中明细 | `{os.path.basename(hit_top3_path)}` |",
            "",
            "### 绝对路径",
            "",
            f"- Top1：`{hit_top1_path}`",
            f"- Top3：`{hit_top3_path}`",
            "",
        ]
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def run(self, sample_path: str) -> tuple[float, float]:
        results = self.load_results(os.path.join(self.result_dir, "results.json"))

        client_top1 = self.build_recommendations(results, top_n=1)
        client_top3 = self.build_recommendations(results, top_n=3)

        ground_truth = self.load_ground_truth(sample_path)

        hit_top1 = self.compute_hit(client_top1, ground_truth)
        hit_top3 = self.compute_hit(client_top3, ground_truth)

        hit_top1_path = os.path.join(self.result_dir, "top1_reference_detail.xlsx")
        hit_top3_path = os.path.join(self.result_dir, "top3_reference_detail.xlsx")
        hit_top1.to_excel(hit_top1_path, index=False)
        hit_top3.to_excel(hit_top3_path, index=False)

        p1 = self.precision(hit_top1)
        p3 = self.precision(hit_top3)

        top1_hits = self._hit_user_count(hit_top1)
        top1_total = self._total_user_count(hit_top1)
        top3_hits = self._hit_user_count(hit_top3)
        top3_total = self._total_user_count(hit_top3)

        report_path = os.path.join(self.result_dir, "evaluation_summary.md")
        self._write_evaluation_markdown(
            report_path,
            hit_top1_path,
            hit_top3_path,
            top1_hits,
            top1_total,
            top3_hits,
            top3_total,
            p1,
            p3,
        )
        print(f"评估摘要已写入 Markdown：{report_path}")
        print(
            self._format_console_evaluation_table(
                top1_hits,
                top1_total,
                top3_hits,
                top3_total,
                p1,
                p3,
            )
        )

        return p1, p3