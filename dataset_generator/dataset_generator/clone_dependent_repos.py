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

                if "fatal: could not read Username for 'https://github.com': No such device or address" in str(e):
                    print("Seems like repo " + repo_name + " does no longer exist.")
                    print("Creating empty folder so the program will not attempt cloning it again")

                    if result_folder.exists():
                        print("Warning: Folder " + str(result_folder) + " already exists.")
                    else:
                        result_folder.mkdir()


if __name__ == '__main__':
    args = sys.argv
    if len(args) >= 2:
        folder_suffix = args[1]
    else:
        folder_suffix = ""
    main(folder_suffix)
