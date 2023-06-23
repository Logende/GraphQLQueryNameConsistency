import os
from pathlib import Path
from typing import List

import json

from gql_model import Fragment, Operation


def load_extracted_data(file_path: Path) -> List[Operation | Fragment]:
    result_list = []
    with open(file_path, 'r') as reader:
        data = json.load(reader)
        fragments = data["fragments"]
        operations = data["operations"]
        for fragment_data in fragments:
            result_list.append(Fragment(content=fragment_data["content"]))
        for operation_data in operations:
            result_list.append(Operation(content=operation_data["content"], operation_type=operation_data["type"],
                                         operation_name=operation_data["name"]))
    return result_list


def persist_dataset(file_path: Path, data: List[Operation | Fragment]):
    operations = [operation.to_dict() for operation in data
                  if isinstance(operation, Operation) and operation.operation_name is not None]
    # Currently, we only care about operations for dataset
    with open(file_path, 'w') as writer:
        json.dump(operations, writer)


if __name__ == '__main__':
    dir_name = os.path.dirname(os.path.realpath(__file__))
    root_path = Path(dir_name).parent
    queries_path = root_path.joinpath("collected_queries")

    all_data = []
    for path in Path(queries_path).glob("*.json"):
        if path.is_file():
            print("Found query file " + str(path))
            subset_data = load_extracted_data(path)
            all_data.extend(subset_data)

    persist_dataset(root_path.joinpath("dataset.json"), all_data)
