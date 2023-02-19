import pickle

from config import DB_NAME

with open(DB_NAME, 'rb') as f:
    data = pickle.load(f)

print(data["38073306"].project_path)

