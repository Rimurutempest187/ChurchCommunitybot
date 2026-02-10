import os
import json

def init_data_files(data_dir):
    files = ["users.json", "groups.json", "admins.json", "events.json"]
    for f in files:
        path = os.path.join(data_dir, f)
        if not os.path.exists(path):
            with open(path, "w") as fp:
                json.dump([], fp)
