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

The resulting CSV of identified repositories is stored in `collected_dependents/dependents_apollo-client.csv`.

## Clone repositories

Todo: script that goes over repos and clones them.