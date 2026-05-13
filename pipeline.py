import os
import warnings
from datetime import datetime

from modules.data_loader import DataLoader
from modules.data_preprocessing import DataPreprocessor
from modules.evaluation import Evaluator
from modules.field_mapping import FieldMapper
from modules.llm_call import LLMCaller

# from modules.prompt_v0 import build_client_prompt  # 模式1：纯大模型推理模式
from modules.prompt_v1 import build_client_prompt  # 模式2：加入本体逻辑
from modules.result_processor import ResultProcessor

warnings.filterwarnings('ignore')

API_KEY = os.environ.get("MINIMAX_API_KEY", "")


def main():
    loader = DataLoader()
    preprocessor = DataPreprocessor()
    mapper = FieldMapper()
    processor = ResultProcessor()

    datasets = loader.load_all()
    test_set = preprocessor.process(datasets)
    client_full_info = mapper.translate(test_set)

    caller = LLMCaller(api_key=API_KEY)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    responses = caller.batch_inference(
        client_full_info,
        prompt_builder=build_client_prompt,
        sample_size=60,
        ts = ts
    )

    results = processor.collect(responses, ts)

    evaluator = Evaluator(result_dir=os.path.join(os.path.dirname(__file__), "output", ts))
    sample_path = os.path.join(os.path.dirname(__file__), "datasets", "tmp_xx_ontology_sample0.xlsx")
    evaluator.run(sample_path)


if __name__ == "__main__":
    main()