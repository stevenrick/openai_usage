import pandas as pd
import os
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from openai_model_costs import model_map_cost_per_1k

# # # setup # # #
load_dotenv()
data_dir = os.getenv('data_dir')
finetune_models = os.getenv('finetune_models')
if finetune_models:
    finetune_models = eval(finetune_models)
else:
    finetune_models = []
usage_path = os.path.join(data_dir, "openai_usage.csv")


def add_cost_cols(_df):
    _model_list = _df["model"].tolist()
    _context_cost_per_1k = []
    _generated_cost_per_1k = []
    for _m in _model_list:
        try:
            if _m in finetune_models:
                _m = "finetune"
            _context_cost_per_1k.append(model_map_cost_per_1k[_m][0])
            _generated_cost_per_1k.append(model_map_cost_per_1k[_m][1])
        except KeyError:
            print(_m, 'not in model map')
    _df["context_cost_per_1k"] = _context_cost_per_1k
    _df["generated_cost_per_1k"] = _generated_cost_per_1k
    return _df


def add_costs_and_sum_by_day():
    _df = pd.read_csv(usage_path)
    _df = add_cost_cols(_df)
    _df["dollars"] = (_df["context_tokens"] / 1000) * _df["context_cost_per_1k"] +\
                     (_df["generated_tokens"] / 1000) * _df["generated_cost_per_1k"]

    _users = _df["username"].unique()

    _sum_dict = {"date": [], "user": [], "context_tokens": [], "generated_tokens": [], "dollars": []}

    for _user in _users:
        _subset = _df[_df["username"] == _user]
        _groups = _subset.groupby("date")
        for _group in _groups:
            # print(_group[0])
            _ct = _group[1]["context_tokens"].sum()
            _gt = _group[1]["generated_tokens"].sum()
            _d = _group[1]["dollars"].sum()
            # print(_user, _ct, _gt, _d)
            _sum_dict["date"].append(_group[0])
            _sum_dict["user"].append(_user)
            _sum_dict["context_tokens"].append(_ct)
            _sum_dict["generated_tokens"].append(_gt)
            _sum_dict["dollars"].append(_d)

    _sum_df = pd.DataFrame(_sum_dict)
    return _sum_df


def clean_and_plot_user_usage(_sum_df):
    _date_list = sorted(_sum_df.date.unique())
    _dollar_dict = dict()
    for _d in _date_list:
        for _user in _sum_df["user"].unique():
            if _user not in _dollar_dict:
                _dollar_dict[_user] = []
            subset = _sum_df[(_sum_df["date"] == _d) & (_sum_df["user"] == _user)]
            if subset.size != 0:
                _dollar_dict[_user].append(subset["dollars"].values[0])
            else:
                _dollar_dict[_user].append(0)

    dollar_plotdf = pd.DataFrame(data=_dollar_dict, index=_date_list)
    dollar_plotdf.plot.line(subplots=True)
    plt.show()


def main():
    df = add_costs_and_sum_by_day()
    clean_and_plot_user_usage(df)


if __name__ == "__main__":
    main()
