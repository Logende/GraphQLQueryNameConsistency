import re
import os
from pathlib import Path
from typing import List, Tuple

import json

from gql_model import Fragment, Operation
from extract_gql_queries import persist_extracted_data


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

    persist_extracted_data(root_path.joinpath("dataset.json"), all_data)
