import os
from pathlib import Path
from typing import List, Iterable, Tuple
import random

import json


def read_and_combine_datasets(files: Iterable):
    result: List[dict] = []
    for file in files:
        with open(file, 'r') as reader:
            data = json.load(reader)
            result.extend(data)
    return result


def split_dataset(dataset: List, train_perc: float, val_perc: float, test_perc: float) -> Tuple[List, List, List]:
    assert train_perc + val_perc + test_perc == 1
    train_dataset = random.choices(dataset, k=int(len(dataset) * train_perc))
    dataset_remaining = [entry for entry in dataset if entry not in train_dataset]

    validation_dataset = random.choices(dataset_remaining, k=int(len(dataset) * val_perc))
    dataset_remaining = [entry for entry in dataset_remaining if entry not in validation_dataset]

    test_dataset = dataset_remaining
    return train_dataset, validation_dataset, test_dataset


def persist_dataset(dataset: List, path_to_persist_at: Path):
    with open(path_to_persist_at, 'w') as writer:
        json.dump(dataset, writer)


def main():
    dir_name = os.path.dirname(os.path.realpath(__file__))
    root_path = Path(dir_name).parent
    datasets_path = root_path.joinpath("collected_datasets")
    final_datasets_path = root_path.joinpath("final_datasets")

    datasets_pos_path = datasets_path.rglob("dataset_pos_*")
    datasets_neg_path = datasets_path.rglob("dataset_neg_*")

    dataset_pos = read_and_combine_datasets(datasets_pos_path)
    dataset_neg = read_and_combine_datasets(datasets_neg_path)

    if not final_datasets_path.exists():
        final_datasets_path.mkdir()

    combined_pos_path = final_datasets_path.joinpath("dataset_pos.json")
    combined_neg_path = final_datasets_path.joinpath("dataset_neg.json")
    entry_count = len(dataset_pos)
    print("Dataset entry count: 2*" + str(entry_count))

    # Write complete dataset into document
    persist_dataset(dataset_pos, combined_pos_path)
    persist_dataset(dataset_neg, combined_neg_path)

    random.seed(42)
    dataset_train_pos, dataset_val_pos, dataset_test_pos = split_dataset(dataset_pos, 0.8, 0.1, 0.1)
    dataset_train_neg, dataset_val_neg, dataset_test_neg = split_dataset(dataset_neg, 0.8, 0.1, 0.1)

    persist_dataset(dataset_train_pos, final_datasets_path.joinpath("dataset_train_pos.json"))
    persist_dataset(dataset_val_pos, final_datasets_path.joinpath("dataset_val_pos.json"))
    persist_dataset(dataset_test_pos, final_datasets_path.joinpath("dataset_test_pos.json"))
    persist_dataset(dataset_train_neg, final_datasets_path.joinpath("dataset_train_neg.json"))
    persist_dataset(dataset_val_neg, final_datasets_path.joinpath("dataset_val_neg.json"))
    persist_dataset(dataset_test_neg, final_datasets_path.joinpath("dataset_test_neg.json"))


if __name__ == '__main__':
    main()
