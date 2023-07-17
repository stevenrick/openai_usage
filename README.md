# OpenAI Usage

A set of scripts for querying users in an OpenAI organization, downloading user usage to csv, and plotting cost over time.

External resources: Pandas, Matplotlib

Tested on Mac OS 12.6.7 with Python 3.10.9

To use, create .env file at root with the following information:
- `openai_org_id` - can find [here](https://platform.openai.com/account/org-settings) **required**
- `openai_api_key` - API key of a user with owner privileges in the org **required**
- `data_dir` - path to your data directory *optional*
- `finetune_models` - list of text strings that are names of any finetune models your organization uses *optional*
- `date_range` - list of text strings for dates to get usage from in the format of `YYYY-MM-DD` *optional*

After your .env file is setup:
- Run `python openai_usage.py` to get the users in your org and then download their data for specified date_range OR yesterday
- Run `python openai_analysis.py` to clean up the usage data, attach cost values, and plot per user costs
