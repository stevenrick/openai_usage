import pandas as pd
import os
from dotenv import load_dotenv
from matplotlib import pyplot as plt

from openai_model_costs import model_map_cost_per_1k

load_dotenv()


def add_cost_cols(_df):
    model_list = _df["model"].tolist()
    context_cost_per_1k = []
    generated_cost_per_1k = []
    for m in model_list:
        try:
            if m in finetune_models:
                m = "finetune"
            context_cost_per_1k.append(model_map_cost_per_1k[m][0])
            generated_cost_per_1k.append(model_map_cost_per_1k[m][1])
        except KeyError:
            print(m, 'not in model map')
    _df["context_cost_per_1k"] = context_cost_per_1k
    _df["generated_cost_per_1k"] = generated_cost_per_1k
    return _df


data_dir = os.getenv('data_dir')
finetune_models = os.getenv('finetune_models')
usage_path = os.path.join(data_dir, "open_ai_usage.csv")

df = pd.read_csv(usage_path)
df = add_cost_cols(df)
df["dollars"] = (df["context_tokens"] / 1000) * df["context_cost_per_1k"] +\
                (df["generated_tokens"] / 1000) * df["generated_cost_per_1k"]

users = df["username"].unique()

cta = df["context_tokens"].sum()
gta = df["generated_tokens"].sum()
total = cta + gta

sum_dict = {"date": [], "user": [], "context_tokens": [], "generated_tokens": [], "dollars": []}

for u in users:
    subset = df[df["username"] == u]
    groups = subset.groupby("date")
    for group in groups:
        # print(group[0])
        ct = group[1]["context_tokens"].sum()
        gt = group[1]["generated_tokens"].sum()
        d = group[1]["dollars"].sum()
        u_tot = ct + gt
        # print(u, u_tot, d)
        sum_dict["date"].append(group[0])
        sum_dict["user"].append(u)
        sum_dict["context_tokens"].append(ct)
        sum_dict["generated_tokens"].append(gt)
        sum_dict["dollars"].append(d)

sum_df = pd.DataFrame(sum_dict)

date_list = sorted(sum_df.date.unique())
dollar_dict = dict()
for d in date_list:
    for user in sum_df["user"].unique():
        if user not in dollar_dict:
            dollar_dict[user] = []
        subset = sum_df[(sum_df["date"] == d) & (sum_df["user"] == user)]
        if subset.size != 0:
            dollar_dict[user].append(subset["dollars"].values[0])
        else:
            dollar_dict[user].append(0)

dollar_plotdf = pd.DataFrame(data=dollar_dict, index=date_list)
dollar_plotdf.plot.line(subplots=True)
plt.show()
