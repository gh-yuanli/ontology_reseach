# 推荐结果评估报告

> 生成时间：`2026-05-13 19:31:15`

本报告汇总 **Top1** 与 **Top3** 推荐相对真实保单的命中情况；明细数据已导出为同目录下的 Excel 文件。

---

## 核心指标一览

| 维度 | Top1 | Top3 |
|------|------|------|
| 命中客户数（至少一条推荐与真实险种一致） | **0** | **0** |
| 参与评估的客户总数 | 1 | 1 |
| 客户级准确率 | **0.0%** | **0.0%** |

### 指标说明

- **命中客户数**：在对应 TopN 推荐中，至少有一条预测的险种代码与 ground truth 中该客户实际购买的险种代码一致的客户人数（按 `appnt_id_no` 去重）。
- **准确率**：命中客户数 ÷ 参与评估的客户总数。

---

## 明细文件路径

以下文件与本报告位于同一目录，可直接用 Excel 打开核对逐单明细。

| 内容 | 文件名 |
|------|--------|
| Top1 推荐与命中明细 | `top1_reference_detail.xlsx` |
| Top3 推荐与命中明细 | `top3_reference_detail.xlsx` |

### 绝对路径

- Top1：`E:\claude-code\Ontology_AgenticML\Ontology_Marketing_Research\output\20260513_192903\top1_reference_detail.xlsx`
- Top3：`E:\claude-code\Ontology_AgenticML\Ontology_Marketing_Research\output\20260513_192903\top3_reference_detail.xlsx`
