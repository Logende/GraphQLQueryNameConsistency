import unittest
from pathlib import Path
import os
from GraphQLQueryNameConsistency.dataset_generator.dataset_generator.extractQueryNamePairs import extract_gql_sections_from_file


class MyTestCase(unittest.TestCase):
    def test_gql_regex(self):
        dir_name = os.path.dirname(os.path.realpath(__file__))
        file_path = Path(dir_name).joinpath("ExampleFileWithGQLQueries.js")
        result = extract_gql_sections_from_file(file_path)
        assert len(result) == 4
        assert result[1] == "gql`bla`"


if __name__ == '__main__':
    unittest.main()
