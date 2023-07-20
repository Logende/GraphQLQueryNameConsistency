import os
from functools import reduce
from pathlib import Path
from typing import List, Iterable, Tuple
import random

import json


def read_dataset(file: Path):
    with open(file, 'r') as reader:
        result = json.load(reader)
    print("Dataset has " + str(len(result)) + " entries")
    result_filtered = filter_entries(result)
    print("Filter removed " + str(len(result) - len(result_filtered)) + " entries from dataset.")
    return result_filtered


def filter_entries(entries: List[dict]) -> List[dict]:
    return [entry for entry in entries
            if len(entry["name"]) > 0
            #and entry["type"] == "subscription"
            ]


def compute_average_content_length(entries: List[dict]):
    lengths = [len(entry["content"]) for entry in entries]
    total_length = reduce(lambda x, y: x+y, lengths, 0)
    return total_length / len(entries)


def main():
    dir_name = os.path.dirname(os.path.realpath(__file__))
    root_path = Path(dir_name).parent
    final_datasets_path = root_path.joinpath("final_datasets_difficult_no_args")

    if not final_datasets_path.exists():
        raise FileNotFoundError("Dataset folder " + str(final_datasets_path) + " does not exist.")

    combined_pos_path = final_datasets_path.joinpath("dataset_pos.json")
    combined_neg_path = final_datasets_path.joinpath("dataset_neg.json")

    dataset_pos = read_dataset(combined_pos_path)
    dataset_neg = read_dataset(combined_neg_path)

    avg_content_length_pos = compute_average_content_length(dataset_pos)
    avg_content_length_neg = compute_average_content_length(dataset_neg)

    print("Avg content length pos " + str(avg_content_length_pos))
    print("Avg content length neg " + str(avg_content_length_neg))


if __name__ == '__main__':
    main()
