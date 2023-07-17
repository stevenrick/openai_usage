import os
import csv
import json
import requests
import datetime
from requests.adapters import HTTPAdapter, Retry
from dotenv import load_dotenv

load_dotenv()

s = requests.Session()

retries = Retry(total=20,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504])

s.mount("https://", HTTPAdapter(max_retries=retries))

data_dir = os.getenv("data_dir")
member_csv = os.path.join(data_dir, "open_ai_members.csv")

openai_org_id = os.getenv("openai_org_id")
openai_api_key = os.getenv("openai_api_key")

# # # this is for populating member list # # #

header1 = {"Authorization": "Bearer {}".format(openai_api_key)}
users = s.get("https://api.openai.com/v1/organizations/{}/users".format(openai_org_id),
              headers=header1)
user_data = json.loads(users.text)

member_list = [["userName", "userId", "userRole"]]

for member in user_data["members"]["data"]:
    user_name = member["user"]["name"]
    user_id = member["user"]["id"]
    user_role = member["role"]
    member_list.append([user_name, user_id, user_role])

with open(member_csv, "w") as csv_file:
    csvWriter = csv.writer(csv_file)
    csvWriter.writerows(member_list)


# # # this runs and logs the usage queries # # #
date_list = os.getenv("date_range")
if date_list is None:
    now = datetime.datetime.now() - datetime.timedelta(days=1)
    date_list = [now.strftime("%Y-%m-%d")]

user_list = []
with open(member_csv, "r") as csv_file:
    csvReader = csv.reader(csv_file)
    next(csvReader)  # skip header row
    for row in csvReader:
        user_list.append({"username": row[0], "id": row[1]})

header2 = {"Authorization": "Bearer {}".format(openai_api_key),
           "openai-organization": "{}".format(openai_org_id)}

usage_csv = os.path.join(data_dir, "open_ai_usage.csv")

for user in user_list:
    for day in date_list:
        print(day, user["id"])
        usage = s.get("https://api.openai.com/v1/usage?date={}&user_public_id={}".format(day, user["id"]),
                      headers=header2)
        usage_data = json.loads(usage.text)["data"]
        if not usage_data:
            print("no usage")
        write_header = not os.path.exists(usage_csv)
        with open(usage_csv, "a") as usage_file:
            csvWriter2 = csv.writer(usage_file)
            if write_header:
                csvWriter2.writerow(["date",
                                     "username",
                                     "requests",
                                     "model",
                                     "context_tokens",
                                     "generated_tokens"])
            for batch in usage_data:
                outData = [day,
                           user["username"],
                           batch["n_requests"],
                           batch["snapshot_id"],
                           batch["n_context_tokens_total"],
                           batch["n_generated_tokens_total"]]
                csvWriter2.writerow(outData)
