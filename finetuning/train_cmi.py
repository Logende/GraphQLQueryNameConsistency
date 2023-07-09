import argparse
import json
from finetune_like_cmi_finder import FineTuneCodeT5

parser = argparse.ArgumentParser()


parser.add_argument(
    "--class0",
    help="path to data file for consistent statementcls",
    required=True
)

parser.add_argument(
    "--class1",
    help="path to data file for inconsistent statements",
    required=True
)

parser.add_argument(
    "--config",
    help="path to file containing models configuration and hyperparams"
)

parser.add_argument(
    "--output",
    help="path to folder where to save the trained model",
    required=True
)

parser.add_argument(
    "--workers",
    help="number of workers to tokenize and batch data",
    default=8
)

parser.add_argument(
    "--seed",
    help="the randomization seed",
    default=152
)

parser.add_argument(
    "--validation",
    help="path to file containing validation data"
)
if __name__ == "__main__":

    args = parser.parse_args()
    class0 = args.class0
    class1 = args.class1
    config = args.config
    output = args.output

    if config is not None:
        with open(config) as cfg:
            training_config = json.load(cfg)
    else:
        training_config = None
    output_dir = output
    data_path = "./"
    data_cache_path = output
    workers = int(args.workers)
    seed = int(args.seed)
    codet5_finetune = FineTuneCodeT5(training_config, output_dir, data_path, data_cache_path, workers, seed)
    codet5_finetune.set_train_data_file(class0)
    if not args.validation:
        validation = "src/neural_models/empty_validation.jsonl"
    else:
        validation = args.validation
    codet5_finetune.set_validation_data_file(validation)
    codet5_finetune.train_from_scratch()
    codet5_finetune.save_model(output)
