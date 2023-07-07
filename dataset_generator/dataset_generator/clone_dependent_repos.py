from git import Repo
import os
import sys
from pathlib import Path

import csv


def main(suffix=None):
    dir_name = os.path.dirname(os.path.realpath(__file__))
    root_path = Path(dir_name).parent
    dependents_csv_path = root_path.joinpath("collected_dependents" + suffix).joinpath("dependents_apollo-client.csv")
    result_repositories_path = root_path.joinpath("collected_repos" + suffix)

    if not result_repositories_path.exists():
        result_repositories_path.mkdir()

    print("Begin endless cloning process.")

    while True:
        with open(dependents_csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            try:
                print("Attempt cloning of Github Repos.")

                for row in reader:
                    repo_name: str = row['name']
                    result_folder = result_repositories_path.joinpath(repo_name.replace("/", "_"))
                    if result_folder.exists():
                        print("Folder " + str(result_folder) + " already exists. Not cloning again.")
                    else:
                        print("Start cloning Repo " + repo_name + ".")
                        repo = Repo.clone_from("https://github.com/" + repo_name, result_folder)

                print("Went through all requested repos!")
                break

            except Exception as e:
                print("Exception occurred: '" + str(e) + "'.")


if __name__ == '__main__':
    arg1 = sys.argv[1]
    folder_suffix = arg1 if arg1 is not None else ""
    main(folder_suffix)
