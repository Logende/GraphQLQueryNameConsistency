import os
import re
from pathlib import Path

if __name__ == '__main__':
    repository_path = "collected_repos/spectrum"

    print("Extracting query-name-pairs from repository " + repository_path + ".")

    # GraphQL queries can be anonymous or named. We care only about the named ones.
    # Besides read queries, there are mutations. ToDo: consider whether we should include those
    #
    all_results = []
    for filePath in Path(repository_path).rglob("*.js"):
        with open(filePath, 'r') as reader:
            content = reader.read()
            results = re.findall("gql`(\\s|((?!`).)*)+`", content)
            if results:
                print(str(results))
                for result in results:
                    #all_results = all_results.append(result)
                    print("found " + str(result))
    print("found " + (str(len(all_results)))+ " queries")

    # TODO: loop through files and extract relevant lines
    # Seems like query string literals have a gql prefix: gql`query_content'

