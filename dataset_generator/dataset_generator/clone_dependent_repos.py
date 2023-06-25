from git import Repo
import os
from pathlib import Path

import csv

if __name__ == '__main__':
    dir_name = os.path.dirname(os.path.realpath(__file__))
    root_path = Path(dir_name).parent
    dependents_csv_path = root_path.joinpath("collected_dependents").joinpath("dependents_apollo-client.csv")
    result_repositories_path = root_path.joinpath("collected_repos")

    print("Begin endless cloning process.")

    while True:
        with open(dependents_csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            try:
                print("Attempt cloning of Github Repos.")

                for row in reader:
                    repo_name: str = row['name']
                    result_folder = result_repositories_path.joinpath(repo_name.replace("/", "_"))
                    progress_file = result_repositories_path.joinpath(repo_name + ".progress")
                    if result_folder.exists():
                        print("Folder " + str(result_folder) + " already exists. Not cloning again.")
                    elif progress_file.exists():
                        print("Seems like another process is already cloning" + str(result_folder) + ".")
                    else:
                        print("Start cloning Repo " + repo_name + ".")
                        open(str(progress_file), 'a').close()
                        repo = Repo.clone_from("https://github.com/" + repo_name, result_folder)
                        os.remove(str(progress_file))

            except Exception as e:
                print("Exception occurred: '" + str(e) + "'.")
