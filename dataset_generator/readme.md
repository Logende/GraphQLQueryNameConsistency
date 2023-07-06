# Building dataset

## Find suitable repos

Decision: focus on JavaScript/Typescript projects. 
Collect list of projects that use the [Apollo Client library](https://github.com/apollographql/apollo-client).

Dependent repositories are shown by Github [here](https://github.com/apollographql/apollo-client/network/dependents).

Use the [github-dependents-info](https://github.com/nvuillam/github-dependents-info) code to generate a list of the dependents.

Problem: Apollo Client has more than 160.000 dependent repositories. 
Scraping the website for all dependents would require accessing more than 5300 Github pages programmatically (as each page lists 30 dependent repositories).
After around 25 page accesses, we experienced a timeout that takes many seconds, until scraping can continue.
As for the project we stick to 1000 repositories for dataset generation, the repo scraper was modified to stop once it collected 1000 repos.
Additionally, the scraper was modified to collect the repositories of the `@apollo-client` and `apollo-client` only and ignore the other packages (`apollo-boost`, `apollo-cache`, ...).
We make use of the `min_stars` parameter of the script and collect repositories with at least 3 stars only.

Execute `python3 dataset_generator/find_dependent_repositories.py`

The resulting CSV of identified repositories is stored in `collected_dependents/dependents_apollo-client.csv`.

## Clone repositories

Execute
`python3 dataset_generator/clone_dependent_repos.py`

This will clone all of the dependent repositories (listed in `collected_dependents/dependents_apollo-client.csv`) into a `collected_repos` folder.

Problem: attempting to clone the repo `liferay/liferay-portal` lead to a `file too large` error. 
This was solved by manually removing this repo from the list of collected dependents.

## Extract GraphQL queries (and mutations)

### Step 1

Execute
`python3 dataset_generator/extract_gql_queries.py`

This will iterate over all repos and over all files within those repos.
All JavaScript and TypeScript files will be read.
It will be attempted to extract GQL operations from those files.

This is done by looking for the regex pattern gql\`<operation>\`.

It will be checked whether `<operation>` actually is an operation or whether it is a fragment or something else.
If neither operation nor fragment can be extracted in a trivial way, it will be checked whether the `<operation>` value is a placeholder expression of the form `${<variable_name>}'.
Should this be the case, the extraction algorithm will be applied on the value behind this placeholder.
This can be done by previously extracting all constant variables from all Javascript and Typescript files using regular expressions.

If it is an operation, it will be attempted to extract the operation type (`query`, `mutation` or `subscription`).
Next, it will be checked whether there exists a custom operation name (e.g. query name). This will be extracted too.
The rest of the operation will be stored as operation content.

Extracted fragments and operations will be persisted in a YAML file inside the `colleced_queries` folder, one file for each repository.

### Step 2

Execute
`python3 dataset_generator/combine_extracted_queries.py`

This will read all the extracted operations and fragments from Step 1 and combine them into one singular `dataset.json` file.
In this step, only operations are considered and fragments are ignored.
JSON format is used for increased performance in comparison to YAML.



TODO:
To queries add: file path, repo name, commit ID


Options: 
CodeT5: produce "consistent" or "inconsistent"

OR: attach smaller model on top of codet5 (classification head)