# CLAUDE.md

## 项目背景

基于 RAG 架构的保险产品智能推荐 Pipeline，将原始 notebook 逻辑拆解为独立模块。数据来自太平洋保险客户数据集，包含画像、行为、企微对话、历史保单等多源异构数据。

## 技术栈

- **Python** >= 3.9
- **uv** — 包管理与虚拟环境
- **openai** — MiniMax API（base_url: https://api.minimaxi.com/v1）
- **pandas / openpyxl** — 数据处理

## 模块说明

| 文件 | 职责 | 关键类/函数 |
|------|------|------------|
| `data_loader.py` | Excel 文件路径 + 加载 | `DataLoader.load_all()` |
| `data_preprocessing.py` | 目标用户筛选/聚合/合并 | `DataPreprocessor.process()` |
| `field_mapping.py` | 字段字典 + 列名中文化 | `FieldMapper.load_field_dict()`, `FieldMapper.translate()` |
| `prompt.py` | user_prompt 模板 | `USER_PROMPT`, `build_client_prompt()` |
| `llm_call.py` | LLM 调用封装 | `LLMCaller.call()`, `LLMCaller.batch_inference()` |
| `result_processor.py` | JSON 响应解析 | `ResultProcessor.parse_response()`, `ResultProcessor.collect()` |
| `evaluation.py` | 推荐效果评估 | `Evaluator.run()` |

## 关键设计决策

1. **目标用户筛选**：以 `insurance_period_beg_dt == 20260430` 划定预测集
2. **数据聚合**：QW（企微）和 Behave（APP）按时间顺序聚合为单行文本；历史保单聚合险种名称/类型/保额
3. **字段映射**：通过 `测试用表字典.xlsx` 读取英中映射，额外字段（behave_text 等）hardcode 在 `FieldMapper.EXTRA_FIELDS`
4. **Prompt 模板**：产品列表 hardcode 在 `prompt.py`，修改产品列表需同步修改该文件中的表格

## 环境变量

| 变量 | 说明 |
|------|------|
| `MINIMAX_API_KEY` | MiniMax API 密钥，必填 |

## 运行

```bash
cd Ontology_Marketing_Research
export MINIMAX_API_KEY="..."
uv run python pipeline.py
```

## 注意事项

- API key 禁止硬编码在代码中
- `pipeline.py` 中 `sample_size=3` 为 debug 模式，全量推理改为 `None`
- Windows 终端中文输出可能乱码，不影响实际结果