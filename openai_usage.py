import os
import csv
import json
import pandas as pd
import requests
import datetime
from requests.adapters import HTTPAdapter, Retry
from dotenv import load_dotenv

# # # setup # # #
s = requests.Session()
retries = Retry(total=20,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504])
s.mount("https://", HTTPAdapter(max_retries=retries))

load_dotenv()
data_dir = os.getenv("data_dir")
if data_dir is None:
    data_dir = os.path.curdir

date_list = os.getenv("date_range")
if date_list is None:
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    date_list = [yesterday.strftime("%Y-%m-%d")]
else:
    date_list = eval(date_list)


member_csv = os.path.join(data_dir, "openai_members.csv")
usage_csv = os.path.join(data_dir, "openai_usage.csv")

openai_org_id = os.getenv("openai_org_id")
openai_api_key = os.getenv("openai_api_key")


def get_members():
    _header1 = {"Authorization": "Bearer {}".format(openai_api_key)}
    _users = s.get("https://api.openai.com/v1/organizations/{}/users".format(openai_org_id),
                   headers=_header1)
    _user_data = json.loads(_users.text)

    _member_list = [["userName", "userId", "userRole"]]

    for _member in _user_data["members"]["data"]:
        _user_name = _member["user"]["name"]
        _user_id = _member["user"]["id"]
        _user_role = _member["role"]
        _member_list.append([_user_name, _user_id, _user_role])

    print("Got {} members from OpenAI org".format(len(_member_list)-1))
    return _member_list


def write_members(_member_list):
    print("Writing openai_members.csv")
    with open(member_csv, "w") as _csv_file:
        _csv_writer = csv.writer(_csv_file)
        _csv_writer.writerows(_member_list)
    return


def get_and_write_usage(_members=None, from_file=False):
    if _members is None:
        _members = []
    _user_list = []
    if from_file:
        with open(member_csv, "r") as csv_file:
            _csv_reader = csv.reader(csv_file)
            next(_csv_reader)  # skip header row
            for row in _csv_reader:
                _user_list.append({"username": row[0], "id": row[1]})
    else:
        for entry in _members[1:]:
            _user_list.append({"username": entry[0], "id": entry[1]})

    _header2 = {"Authorization": "Bearer {}".format(openai_api_key),
                "openai-organization": "{}".format(openai_org_id)}

    for _user in _user_list:
        for day in date_list:
            print("Getting usage for {} on {}".format(_user["id"], day))
            _usage = s.get("https://api.openai.com/v1/usage?date={}&user_public_id={}".format(day, _user["id"]),
                           headers=_header2)
            _usage_data = json.loads(_usage.text)["data"]
            if _usage_data:
                write_header = not os.path.exists(usage_csv)
                with open(usage_csv, "a") as _usage_file:
                    _csv_writer2 = csv.writer(_usage_file)
                    if write_header:
                        _csv_writer2.writerow(["date",
                                               "username",
                                               "requests",
                                               "model",
                                               "context_tokens",
                                               "generated_tokens"])
                    for _batch in _usage_data:
                        _out_data = [day,
                                     _user["username"],
                                     _batch["n_requests"],
                                     _batch["snapshot_id"],
                                     _batch["n_context_tokens_total"],
                                     _batch["n_generated_tokens_total"]]
                        _csv_writer2.writerow(_out_data)
    return


def sort_usage():
    df = pd.read_csv(usage_csv)
    df.sort_values(by=['date', 'username'], ascending=[False, True])
    df.to_csv(path_or_buf=os.path.join(data_dir, "openai_usage_sorted.csv"), index=False)
    return


def main():
    # members = get_members()
    # write_members(members)
    # get_and_write_usage(members)
    # # alternatively if you already queried members (and don't expect changes) # #
    get_and_write_usage(from_file=True)
    # # optional functions
    sort_usage()


if __name__ == "__main__":
    main()
