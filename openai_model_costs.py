# maps model name to [input, output] cost per 1k tokens
model_map_cost_per_1k = {
    'gpt-3.5-turbo-0301': [0.0015, 0.002],
    'gpt-3.5-turbo-0613': [0.0015, 0.002],
    'gpt-3.5-turbo-16k-0613': [0.003, 0.004],
    'gpt-4-0314': [0.03, 0.06],
    'gpt-4-0613': [0.03, 0.06],
    'text-embedding-ada-002-v2': [0.0001, 0.0001],
    'text-davinci:003': [0.02, 0.02],
    'text-ada:001': [0.0004, 0.0004],
    'finetune': [0.12, 0.12],
    'text-davinci-edit:001': [0.03, 0.06],
}
