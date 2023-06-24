import re
import os
from pathlib import Path
from typing import List

import yaml

from gql_model import Fragment, Operation


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
        try:
            return extract_gql_sections_from_text(reader.read())
        except UnicodeDecodeError:
            print("Unable to decode file " + str(file_path))
            return []


def extract_gql_sections_from_repo(repo_path: Path) -> List[str]:
    all_results = []

    patterns = ('*.ts')
    all_relevant_files = []
    for pattern in patterns:
        all_relevant_files.extend(Path(repo_path).rglob(pattern))

    for file_path in all_relevant_files:
        if not file_path.is_file() or file_path.is_dir():
            continue
        else:
            sub_results = extract_gql_sections_from_file(file_path)
            all_results.extend(sub_results)
    return all_results


def strip_gql_boilerplate(gql_section: str) -> str:
    return gql_section.removeprefix("gql`").removesuffix("`").strip()


def extract_type_name_content_tuple(gql_section: str) -> Fragment | Operation | None:
    content = strip_gql_boilerplate(gql_section)

    re_result = re.match(r"^\w+", content)
    if re_result is None:
        print("Unable to extract operation type from GQL section '" + gql_section + "'.")
        return None

    operation_type = re_result.group()
    content = content.removeprefix(operation_type).strip()

    if operation_type == "fragment":
        return Fragment(content)

    elif operation_type == "query" or operation_type == "mutation" or operation_type == "subscription":
        next_curly_bracket = content.find("{")
        operation_name = content[0: next_curly_bracket].strip()
        operation_content = content[next_curly_bracket: len(content)].strip()
        return Operation(operation_type=operation_type, operation_name=operation_name, content=operation_content)


def extract_queries_from_repo(repo_path: Path) -> List[Operation | Fragment]:
    print("Extracting query-name-pairs from repository " + str(repo_path) + ".")

    gql_sections = extract_gql_sections_from_repo(repo_path)
    print("Found " + (str(len(gql_sections))) + " gql strings in the repository.")

    result_list = [extract_type_name_content_tuple(section) for section in gql_sections]
    return [v for v in result_list if v is not None]


def persist_extracted_data(file_path: Path, data: List[Operation | Fragment]):
    fragments = [fragment.to_dict() for fragment in data if isinstance(fragment, Fragment)]
    operations = [operation.to_dict() for operation in data if isinstance(operation, Operation)]
    new_data = {
        "fragments": fragments,
        "operations": operations
    }
    with open(file_path, 'w') as writer:
        yaml.safe_dump(new_data, writer)


if __name__ == '__main__':
    dir_name = os.path.dirname(os.path.realpath(__file__))
    root_path = Path(dir_name).parent
    repositories_path = root_path.joinpath("collected_repos")
    queries_path = root_path.joinpath("collected_queries")

    if not queries_path.exists():
        print("Folder " + str(queries_path) + " does not exist yet. Creating it.")
        queries_path.mkdir()
    else:
        print("Folder " + str(queries_path) + " already exists.")

    for path in Path(repositories_path).glob("*/"):
        if path.is_dir():
            print("Found repo dir " + str(path))

            repository_path = path
            result = extract_queries_from_repo(repository_path)
            repo_name = str(repository_path.name)
            persist_extracted_data(queries_path.joinpath(repo_name + ".yaml"), result)
