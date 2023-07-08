import re
import os
import sys
from pathlib import Path
from typing import List, Dict

import yaml

from gql_model import Fragment, Operation


relevant_file_patterns = ("*.js", "*.ts", "*.jsx", "*.tsx")


def extract_constants_from_text(data: str) -> Dict:
    all_results = {}
    # Seems like query string literals have a gql prefix: gql`query_content'
    regex = r"export\s+const\s+(\w+)\s*\=\s*`((\s|((?!`).)*)+)`"
    matches = re.finditer(regex, data, re.MULTILINE)
    if matches:
        for _, match in enumerate(matches, start=1):
            all_results[match.group(1)] = match.group(2)
    return all_results


def extract_constants_from_file(file_path: Path) -> Dict:
    with open(file_path, 'r') as reader:
        try:
            data = reader.read()
            return extract_constants_from_text(data)
        except UnicodeDecodeError:
            print("Unable to decode file " + str(file_path))
            return {}


def extract_constants(all_relevant_files: List[Path]) -> {}:
    all_results = {}

    for file_path in all_relevant_files:
        if not file_path.is_file() or file_path.is_dir():
            continue
        else:
            sub_results = extract_constants_from_file(file_path)
            # note that if the same variable name is exported multiple times, it will be overwritten and the
            # dict will contain just one instance of it
            all_results = {**all_results, **sub_results}
    return all_results


def extract_gql_sections_from_text(data: str) -> List[str]:
    all_results = []
    # Seems like query string literals have a gql prefix: gql`query_content'
    regex = r"gql`(\s|((?!`).)*)+`"
    matches = re.finditer(regex, data, re.MULTILINE)
    if matches:
        index = 0
        for _, match in enumerate(matches, start=1):
            all_results.append(match.group())
            index += 1
            print("match index " + str(index))
    return all_results


def extract_gql_sections_from_file(file_path: Path) -> List[str]:
    with open(file_path, 'r') as reader:
        try:
            data = reader.read()
            matches = extract_gql_sections_from_text(data)
            return matches
        except UnicodeDecodeError:
            print("Unable to decode file " + str(file_path))
            return []


def extract_gql_sections(all_relevant_files: List[Path]) -> List[str]:
    all_results = []

    for file_path in all_relevant_files:
        print("Extract GQL sections from file " + str(file_path))
        if not file_path.is_file() or file_path.is_dir():
            continue
        else:
            sub_results = extract_gql_sections_from_file(file_path)
            all_results.extend(sub_results)
    return all_results


def glob_relevant_files(repo_path: Path) -> List[Path]:
    all_relevant_files = []
    for pattern in relevant_file_patterns:
        all_relevant_files.extend(Path(repo_path).rglob(pattern))
    return all_relevant_files


def strip_gql_boilerplate(gql_section: str) -> str:
    return gql_section.removeprefix("gql`").removesuffix("`").strip()


def extract_operation_or_fragment(gql_section: str, constants: Dict) -> Fragment | Operation | None:
    content = strip_gql_boilerplate(gql_section)

    re_result = re.match(r"^\w+", content)
    if re_result is None:
        # If first thing in string is not word: no operation name.
        # But one rescue attempt possible: by replacing constants
        re_result = re.match(r"\$\{(\w+)\}", content)
        if re_result is not None:
            variable_name = re_result.group(1)
            if variable_name in constants:
                return extract_operation_or_fragment(constants[variable_name], constants)
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
    all_relevant_files = glob_relevant_files(repo_path)
    print("Extracting query-name-pairs from repository " + str(repo_path) +
          " having " + str(len(all_relevant_files)) + " candidate files.")

    gql_sections = extract_gql_sections(all_relevant_files)
    print("Found " + (str(len(gql_sections))) + " gql strings in the repository.")

    constants = extract_constants(all_relevant_files)
    print("Found " + (str(len(constants))) + " constants in the repository.")

    result_list = [extract_operation_or_fragment(section, constants) for section in gql_sections]
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


def main(suffix=None):
    dir_name = os.path.dirname(os.path.realpath(__file__))
    root_path = Path(dir_name).parent
    repositories_path = root_path.joinpath("collected_repos" + suffix)
    queries_path = root_path.joinpath("collected_queries" + suffix)

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


if __name__ == '__main__':
    arg1 = sys.argv[1]
    folder_suffix = arg1 if arg1 is not None else ""
    main(folder_suffix)
