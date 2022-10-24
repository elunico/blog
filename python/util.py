import json
import os.path


def serialize(metadata, folder, file_prefix):
    if not os.path.isdir(folder):
        os.makedirs(folder)

    with open(os.path.join(folder, '{}.json'.format(file_prefix)), 'w') as f:
        json.dump(metadata, f)


def unserialize(folder, file_prefix):
    with open(os.path.join(folder, '{}.json'.format(file_prefix))) as f:
        return json.load(f)

def birthtime_for_filename(filename):
    return os.stat(os.path.join('source', filename)).st_birthtime
