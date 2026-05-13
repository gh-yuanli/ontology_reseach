import json
import os

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

        print(f"Top1 命中数: {hit_top1[hit_top1['is_hit']==1].appnt_id_no.nunique()} / 总数: {hit_top1.appnt_id_no.nunique()} / 准确率: {p1:.1%}")
        print(f"Top3 命中数: {hit_top3[hit_top3['is_hit']==1].appnt_id_no.nunique()} / 总数: {hit_top3.appnt_id_no.nunique()} / 准确率: {p3:.1%}")
        print(f"Top1 明细存入 {hit_top1_path}")
        print(f"Top3 明细存入 {hit_top3_path}")

        return p1, p3