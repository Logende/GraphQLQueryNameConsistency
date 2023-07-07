import csv
import os
import sys
from pathlib import Path
import clone_dependent_repos
import extract_gql_queries
import combine_extracted_queries
import generate_negative_dataset


if __name__ == '__main__':
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]

    start_index = int(arg1)
    end_index = int(arg2)
    suffix = "_" + str(start_index) + "_" + str(end_index)

    dir_name = os.path.dirname(os.path.realpath(__file__))
    root_path = Path(dir_name).parent
    dependents_csv_path = root_path.joinpath("collected_dependents").joinpath("dependents_apollo-client.csv")
    dependents_csv_path_new = root_path.joinpath("collected_dependents" + suffix).joinpath("dependents_apollo-client.csv")

    if not dependents_csv_path_new.parent.exists():
        dependents_csv_path_new.parent.mkdir()

    print("Start generator toolchain with repo " + str(start_index) + " to " + str(end_index) + ".")
    print("Create subset of dependents file: " + str(dependents_csv_path_new))
    with open(dependents_csv_path, encoding='utf-8') as f, open(dependents_csv_path_new, 'w') as o:
        reader = csv.reader(f)
        writer = csv.writer(o, delimiter=',')  # adjust as necessary
        index = 0
        for row in reader:
            if index >= start_index:
                if index > end_index:
                    break
                writer.writerow(row)
            index += 1

    print("Clone repos")
    clone_dependent_repos.main(suffix)

    print("Extract queries")
    extract_gql_queries.main(suffix)

    print("Combine queries")
    combine_extracted_queries.main(suffix)

    print("Generate negative dataset")
    generate_negative_dataset.main(suffix)

    print("Positive dataset:")
    dataset_pos_path = root_path.joinpath("dataset_pos" + suffix + ".json")
    with open(dataset_pos_path, 'r') as reader:
        print(reader.read())

    print("Negative dataset:")
    dataset_neg_path = root_path.joinpath("dataset_neg" + suffix + ".json")
    with open(dataset_neg_path, 'r') as reader:
        print(reader.read())
