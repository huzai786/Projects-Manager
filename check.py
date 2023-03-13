import pickle

from config import config

with open(config.DB_NAME, 'rb') as f:
    data = pickle.load(f)

print(data)
print(data["75308241"].github_info)