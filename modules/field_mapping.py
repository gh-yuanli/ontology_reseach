from pathlib import Path

import pandas as pd


def get_project_root() -> Path:
    return Path(__file__).parent.parent


class FieldMapper:
    EXTRA_FIELDS = {
        "behave_text": "APP按钮点击记录",
        "qw_text": "企业微信记录",
        "cvrg_name_text": "历史购买险种记录",
        "productbigtype_text": "历史购买险种类型",
        "insured_amt_text": "历史购买险种保额",
    }

    def load_field_dict(self) -> dict[str, str]:
        root = get_project_root()
        df = pd.read_excel(root / "datasets" / "测试用表字典.xlsx", sheet_name="数据字典")
        field_dict = df[["字段名", "中文含义"]].set_index("字段名")["中文含义"].to_dict()
        field_dict.update(self.EXTRA_FIELDS)
        return field_dict

    def translate(self, df: pd.DataFrame) -> list[dict]:
        field_dict = self.load_field_dict()
        df.columns = [field_dict.get(col, col) for col in df.columns]
        return df.to_dict("records")