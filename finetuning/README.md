# Finetuning

This folder deals with fine-tuning (Code-)T5 with the data generated in the data_generator step.

`finetune_with_baset5.py` was built upon the code in `example_imdb`.
The biggest change from the imdb code was dataset loading (combined dataset files instead of each data point in a separate file) and the input provided to the tokenizer.
For the graphQL use case, the input that is encoded is the query code, then a separator and then the query name.

`finetune_with_codet5` builds upon that but uses CodeT5 instead of base-t5 and replaces T5Tokenizer with RobertaTokenizer.
There currently is some issue with it (see `notebooks/finetuning_codet5_with_graphql_issue.ipynb`).

Finally, in the `cmi_finder` folder is adapted code from the paper https://software-lab.org/publications/icse2023_CMI-Finder.pdf, where
CodeT5 and RobertaTokenizer are being used for fine-tuning for a binary classification task.
I've attempted to get their code running but have not succeeded with it so far.

As GraphQl queries are not very close to general purpose programming languages, it seems to be good enough to stick with base-t5.

# Evaluation

The fine-tuned base-t5 model was evaluated using the test dataset.

In the initially used dataset, most of the negative samples differed considerably from the positive samples, leading to very high accuracy.
![Classification report simple dataset](eval_simple_dataset_1.png)
![Confusion matrix simple dataset](eval_simple_dataset_2.png)

After discovering that the samples still contained entries with an empty query name, I cleaned up the dataset by removing those samples with empty query names.
I repeated the training process, as well as the evaluation (on the new test dataset) and got even higher accuracy (as before it was random and not learnable for the model whether a pair is consistent or not when the query name is empty).

![Classification report simple dataset filtered](eval_simple_dataset_filtered_1.png)
![Confusion matrix simple dataset_filtered](eval_simple_dataset_filtered_2.png)

As the accuracy was so high, I decided to introduce more difficult negative samples to make it more challenging for the model.
Trained with the simple dataset, but tested on the more difficult dataset (30% of negative samples generated using method 2), we get the following results:

![Classification report difficult dataset simple model](eval_difficult_dataset_simple_model_1.png)
![Confusion matrix difficult simple model](eval_difficult_dataset_simple_model_2.png)

The results are as expected with the change: more inconsistent samples are now falsely detected as consistent by the model.
The number of false negatives does not change.
It is surprising that the overall difference in the results is very low (179 false positive compared to 128 before) and the f-1 score still is 97%.
This leads to the assumption that the dataset has gotten only slightly more difficult.

After training the model on the more difficult dataset, the evaluation results on the test dataset are as follows:

![Classification report difficult dataset](eval_difficult_dataset_1.png)
![Confusion matrix difficult dataset](eval_difficult_dataset_2.png)

The number of false positives is lower (69 compared to 179) but the number of false negatives is higher (103 compared to  43).