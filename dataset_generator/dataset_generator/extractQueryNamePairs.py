import re
import os
from pathlib import Path
from typing import List, Tuple


def extract_gql_sections_from_text(data: str) -> List[str]:
    all_results = []
    # Seems like query string literals have a gql prefix: gql`query_content'
    regex = r"gql`(\s|((?!`).)*)+`"
    matches = re.finditer(regex, data, re.MULTILINE)
    if matches:
        for _, match in enumerate(matches, start=1):
            all_results.append(match.group())
    return all_results


def extract_gql_sections_from_file(file_path: Path) -> List[str]:
    with open(file_path, 'r') as reader:
        return extract_gql_sections_from_text(reader.read())


def extract_gql_sections_from_repo(repo_path: Path) -> List[str]:
    all_results = []
    for file_path in Path(repo_path).rglob("*.js"):
        if not file_path.is_file() or file_path.is_dir():
            continue
        else:
            sub_results = extract_gql_sections_from_file(file_path)
            all_results.extend(sub_results)
    return all_results


def extract_query_name_pairs_from_repo(repo_path: Path) -> List[Tuple[str, str]]:
    print("Extracting query-name-pairs from repository " + str(repository_path) + ".")

    gql_sections = extract_gql_sections_from_repo(repo_path)

    print("Found " + (str(len(gql_sections))) + " gql strings in the repository.")

    # GraphQL queries can be anonymous or named. We care only about the named ones.
    # Besides read queries, there are mutations and fragments. ToDo: consider whether we should include those


if __name__ == '__main__':
    dir_name = os.path.dirname(os.path.realpath(__file__))
    repository_path = Path(dir_name).parent.joinpath("collected_repos/spectrum")
    extract_query_name_pairs_from_repo(repository_path)

