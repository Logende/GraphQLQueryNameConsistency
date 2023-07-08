import os
from pathlib import Path
from typing import List, Iterable

import json


def read_and_combine_datasets(files: Iterable):
    result: List[dict] = []
    for file in files:
        with open(file, 'r') as reader:
            data = json.load(reader)
            result.extend(data)
    return result


def main():
    dir_name = os.path.dirname(os.path.realpath(__file__))
    root_path = Path(dir_name).parent
    datasets_path = root_path.joinpath("collected_datasets")

    datasets_pos_path = datasets_path.rglob("dataset_pos_*")
    datasets_neg_path = datasets_path.rglob("dataset_pos_*")

    datasets_pos = read_and_combine_datasets(datasets_pos_path)
    datasets_neg = read_and_combine_datasets(datasets_neg_path)

    combined_pos_path = root_path.joinpath("dataset_pos.json")
    combined_neg_path = root_path.joinpath("dataset_neg.json")

    with open(combined_pos_path, 'w') as writer:
        json.dump(datasets_pos, writer)

    with open(combined_neg_path, 'w') as writer:
        json.dump(datasets_neg, writer)


if __name__ == '__main__':
    main()
