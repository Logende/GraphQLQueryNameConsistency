import os
from pathlib import Path

import transformers
from datasets import load_dataset, load_metric

if __name__ == '__main__':

    dir_name = os.path.dirname(os.path.realpath(__file__))
    root_path = Path(dir_name).parent
    dataset_path = root_path.joinpath("dataset_generator").joinpath("dataset.json")

    datasets = load_dataset("json", data_files=str(dataset_path))
    print("dw")