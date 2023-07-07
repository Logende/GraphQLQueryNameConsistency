import os
import random
from pathlib import Path
from typing import List, Tuple
from itertools import combinations

import json

from gql_model import Operation


def generate_negative_dataset(file_path: Path, dataset_pos: List[dict]):
    result: List[dict] = []

    combs: List[Tuple[dict, dict]] = list(combinations(dataset_pos, 2))
    for pair in combs:
        operation_1 = pair[0]
        operation_2 = pair[1]
        if operation_1 != operation_2:
            result.append({"type": operation_1["type"],
                           "name": operation_1["name"],
                           "content": operation_2["content"]})
            result.append({"type": operation_2["type"],
                           "name": operation_2["name"],
                           "content": operation_1["content"]})

    # result is exponentially bigger than dataset_pos. Therefore, randomly pick len(dataset_pos) entry
    # to get dataset with same amount of negative samples as positive
    result = random.choices(result, k=len(dataset_pos))
    with open(file_path, 'w') as writer:
        json.dump(result, writer)


if __name__ == '__main__':
    dir_name = os.path.dirname(os.path.realpath(__file__))
    root_path = Path(dir_name).parent
    dataset_pos_path = root_path.joinpath("dataset_pos.json")
    dataset_neg_path = root_path.joinpath("dataset_neg.json")
    with open(dataset_pos_path, 'r') as reader:
        dataset_pos = json.load(reader)

    generate_negative_dataset(dataset_neg_path, dataset_pos)
