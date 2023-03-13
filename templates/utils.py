import os
import pickle
import random

from config import config


def delete_records(db_name, project_id):
    with open(db_name, 'rb') as f:
        record = pickle.load(f)
        del record[project_id]
    with open(db_name, 'wb') as f:
        pickle.dump(record, f)

def save_records(db_name, instance, _id):
    if not os.path.exists(db_name):
        raise Exception("db doesn't exists")
    with open(db_name, 'rb') as f:
        record = pickle.load(f)
    record[_id] = instance
    with open(db_name, 'wb') as f:
        pickle.dump(record, f)

def get_random_id():
    return "".join([str(random.randrange(0, 9)) for _ in range(8)])


def get_records(db_name):
    with open(db_name, 'rb') as f:
        data = pickle.load(f)
    return data

def update_record(db_name, ins_id, ins):
    with open(db_name, 'rb') as f:
        record = pickle.load(f)
    del record[ins_id]
    record[ins_id] = ins
    with open(db_name, 'wb') as f:
        pickle.dump(record, f)


def get_project(project_id):
    records = get_records(config.DB_NAME)
    project = records.get(project_id)
    return project
