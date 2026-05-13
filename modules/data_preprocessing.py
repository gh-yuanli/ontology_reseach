import pandas as pd


class DataPreprocessor:
    def process(self, datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
        data_sample = datasets["sample"]
        data_history_plc = datasets["history_plc"]
        data_profile = datasets["profile"]
        data_qw = datasets["qw"]
        data_behave = datasets["behave"]

        target_appnt_ids = data_sample[data_sample["insurance_period_beg_dt"] == 20260430][
            "appnt_id_no"
        ].unique().tolist()
        target_tel_nos = data_sample[data_sample["insurance_period_beg_dt"] == 20260430][
            "tel_no"
        ].unique().tolist()

        data_profile_target = data_profile[data_profile["tel_no"].isin(target_tel_nos)]
        data_qw_target = data_qw[data_qw["tel_no"].isin(target_tel_nos)]
        data_behave_target = data_behave[data_behave["tel_no"].isin(target_tel_nos)]
        data_history_plc_target = data_history_plc[
            data_history_plc["appnt_id_no"].isin(target_appnt_ids)
        ]

        data_qw_agg = (
            data_qw_target.sort_values(["tel_no", "msg_time"])
            .groupby("tel_no")
            .apply(lambda g: "。".join(g["content_str"].dropna()))
            .reset_index(name="qw_text")
        )

        data_behave_agg = (
            data_behave_target.sort_values(["tel_no", "evt_start_tm"])
            .groupby("tel_no")
            .apply(lambda g: "; ".join(g["button_nm"].dropna()))
            .reset_index(name="behave_text")
        )

        data_history_plc_agg = data_history_plc_target.groupby("appnt_id_no").apply(
            lambda g: "; ".join(g["cvrg_name"].dropna())
        ).reset_index(name="cvrg_name_text")

        test_set = (
            data_sample[data_sample.appnt_id_no.isin(target_appnt_ids)][
                ["appnt_id_no", "tel_no"]
            ]
            .drop_duplicates()
            .merge(data_profile_target, on="tel_no", how="left")
            .merge(data_behave_agg, on="tel_no", how="left")
            .merge(data_qw_agg, on="tel_no", how="left")
            .merge(data_history_plc_agg, on="appnt_id_no", how="left")
            .drop_duplicates(subset=["appnt_id_no"])
        )

        return test_set