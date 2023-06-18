if __name__ == '__main__':
    repository = "todo"

    print("Extracting query-name-pairs from repository " + repository + ".")

    # GraphQL queries can be anonymous or named. We care only about the named ones.
    # Besides read queries, there are mutations. ToDo: consider whether we should include those
    #

    # TODO: Clone Repo
    desired_count = 10

    # TODO: loop through files and extract relevant lines
    # Seems like query string literals have a gql prefix: gql`query_content'

