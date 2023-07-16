import os
import sys
from pathlib import Path
from typing import List

import json
import yaml

from gql_model import Fragment, Operation


def load_extracted_data(file_path: Path) -> List[Operation | Fragment]:
    result_list = []
    with open(file_path, 'r') as reader:
        try:
            data = yaml.safe_load(reader)
        except UnicodeDecodeError:
            print("Unable to decode " + str(file_path))
            return []

        fragments = data["fragments"]
        operations = data["operations"]
        for fragment_data in fragments:
            result_list.append(Fragment(content=fragment_data["content"], metadata=fragment_data["metadata"]))
        for operation_data in operations:
            result_list.append(Operation(content=operation_data["content"], operation_type=operation_data["type"],
                                         operation_name=operation_data["name"], metadata=operation_data["metadata"]))
    return result_list


def persist_dataset(file_path: Path, data: List[Operation | Fragment]):
    operations = [operation.to_dict() for operation in data
                  if isinstance(operation, Operation)
                  and operation.operation_name is not None
                  and len(operation.operation_name) > 0]
    # Currently, we only care about operations for dataset
    with open(file_path, 'w') as writer:
        json.dump(operations, writer)


def main(suffix=None):
    dir_name = os.path.dirname(os.path.realpath(__file__))
    root_path = Path(dir_name).parent
    queries_path = root_path.joinpath("collected_queries" + suffix)
    datasets_path = root_path.joinpath("collected_datasets")

    if not datasets_path.exists():
        datasets_path.mkdir()

    all_data = []
    for path in Path(queries_path).glob("*.yaml"):
        if path.is_file():
            print("Found query file " + str(path))
            subset_data = load_extracted_data(path)
            all_data.extend(subset_data)

    persist_dataset(datasets_path.joinpath("dataset_pos" + suffix + ".json"), all_data)


if __name__ == '__main__':
    args = sys.argv
    if len(args) >= 2:
        folder_suffix = args[1]
    else:
        folder_suffix = ""
    main(folder_suffix)
