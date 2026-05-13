# Ontology Marketing Research — RAG Insurance Recommendation Pipeline

## 项目概述

基于 RAG（检索增强生成）架构的保险产品智能推荐系统。系统从多源异构数据（客户画像、APP 行为、企微对话、历史保单）中提取客户特征，结合保险产品目录，生成个性化推荐。

## 目录结构

```
Ontology_Marketing_Research/
├── pyproject.toml           # uv 项目配置
├── pipeline.py              # 主流程入口
├── modules/
│   ├── __init__.py
│   ├── data_loader.py      # Excel 文件路径 + 加载
│   ├── data_preprocessing.py  # 目标用户筛选、多表聚合、合并
│   ├── field_mapping.py    # 字段字典读取 + 列名中文化
│   ├── prompt.py           # user_prompt 模板 + client prompt 构建
│   ├── llm_call.py         # LLM 客户端封装 + 批量推理
│   ├── result_processor.py # LLM 响应 JSON 解析 + 结果持久化
│   └── evaluation.py      # 推荐效果评估（Top1/Top3 准确率）
├── datasets/               # 数据文件目录
└── output/                 # 推理结果目录（按时间戳组织）
```

## 环境配置

```bash
# 安装依赖
cd Ontology_Marketing_Research
uv venv
uv pip install -e .

# 运行（需要设置 API key）
export MINIMAX_API_KEY="your-api-key"
uv run python pipeline.py
```

Windows PowerShell:
```powershell
$env:MINIMAX_API_KEY = "your-api-key"
uv run python pipeline.py
```

## 依赖

- Python >= 3.9
- pandas
- openai
- tqdm
- openpyxl >= 3.1.5

## 数据文件

| 文件 | 说明 |
|------|------|
| `tmp_xx_ontology_sample0.xlsx` | 样本主表（含目标用户标识） |
| `tmp_xx_ontology_sample_history_behave.xlsx` | APP 行为数据 |
| `tmp_xx_ontology_sample_history_plc.xlsx` | 历史保单数据 |
| `tmp_xx_ontology_sample_profi.xlsx` | 客户画像数据 |
| `tmp_xx_ontology_sample_qw.xlsx` | 企业微信聊天记录 |
| `测试用表字典.xlsx` | 字段中英文映射字典 |

## Pipeline 流程

1. **DataLoader** — 加载所有 Excel 数据文件
2. **DataPreprocessor** — 按 `insurance_period_beg_dt == 20260430` 筛选目标用户，聚合多表
3. **FieldMapper** — 字段列名中文化，输出 `list[dict]`
4. **LLMCaller** — 批量调用 LLM（默认 sample_size=50）
5. **ResultProcessor** — 解析 JSON 输出，写入 `results.json`
6. **Evaluator** — 计算 Top1/Top3 准确率，输出明细 Excel

## 输出文件

每次运行生成 `output/{timestamp}/` 目录：
- `results.json` — LLM 推荐结果
- `prompts.json` — 本次输入的所有 prompt
- `top1_reference_detail.xlsx` — Top1 命中明细
- `top3_reference_detail.xlsx` — Top3 命中明细

## 修改推荐产品列表

编辑 `modules/prompt.py` 中 `USER_PROMPT` 里的保险产品表格。

## 注意事项

- 默认推理 sample_size=3，如需全量推理在 `pipeline.py` 中调整或设为 `None`
- API key 通过环境变量 `MINIMAX_API_KEY` 传入，请勿硬编码