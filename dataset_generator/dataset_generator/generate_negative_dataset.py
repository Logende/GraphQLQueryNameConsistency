import os
import random
import sys
from pathlib import Path
from typing import List, Tuple
from itertools import combinations

import json

from gql_model import Operation


def generate_negative_entries_by_mixing_up(dataset_pos: List[dict], enforce_same_repo_for_pairs):
    result: List[dict] = []

    combs: List[Tuple[dict, dict]] = list(combinations(dataset_pos, 2))
    for pair in combs:
        operation_1 = pair[0]
        operation_2 = pair[1]
        if operation_1 != operation_2 \
                and operation_1["name"] != operation_2["name"] \
                and operation_1["content"] != operation_2["content"] \
                and (not enforce_same_repo_for_pairs
                     or operation_1["metadata"]["repo"] == operation_2["metadata"]["repo"]):
            result.append({
                "type": operation_1["type"],
                "name": operation_1["name"],
                "content": operation_2["content"],
                "metadata_type": operation_1["metadata"],
                "metadata_name": operation_1["metadata"],
                "metadata_content": operation_2["metadata"]
            })
            result.append({
                "type": operation_2["type"],
                "name": operation_2["name"],
                "content": operation_1["content"],
                "metadata_type": operation_2["metadata"],
                "metadata_name": operation_2["metadata"],
                "metadata_content": operation_1["metadata"]
            })
    return result


def generate_negative_dataset(file_path: Path, dataset_pos: List[dict], percentage_difficult: float):
    count_difficult = int(len(dataset_pos) * percentage_difficult)
    count_simple = len(dataset_pos) - count_difficult

    all_samples_simple: List[dict] = generate_negative_entries_by_mixing_up(dataset_pos, False)
    result_simple: List[dict] = random.choices(all_samples_simple, k=count_simple)

    all_samples_difficult: List[dict] = generate_negative_entries_by_mixing_up(dataset_pos, True)
    result_difficult: List[dict] = random.choices(all_samples_difficult, k=count_difficult)

    result = result_simple
    result.extend(result_difficult)
    with open(file_path, 'w') as writer:
        json.dump(result, writer)


def main(suffix=None):
    random.seed(42)
    dir_name = os.path.dirname(os.path.realpath(__file__))
    root_path = Path(dir_name).parent
    datasets_path = root_path.joinpath("collected_datasets")

    dataset_pos_path = datasets_path.joinpath("dataset_pos" + suffix + ".json")
    dataset_neg_path = datasets_path.joinpath("dataset_neg" + suffix + ".json")
    with open(dataset_pos_path, 'r') as reader:
        dataset_pos = json.load(reader)

    generate_negative_dataset(dataset_neg_path, dataset_pos, percentage_difficult=0.3)


if __name__ == '__main__':
    args = sys.argv
    if len(args) >= 2:
        folder_suffix = args[1]
    else:
        folder_suffix = ""
    main(folder_suffix)
