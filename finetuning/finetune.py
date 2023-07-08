import os
from pathlib import Path
import argparse
import glob
import json
import time
import logging
import random
import re
import ipdb as pdb
from tqdm import tqdm
from itertools import chain
from string import punctuation
from transformers import T5Model, T5Tokenizer
import nltk

nltk.download('punkt')

from nltk.tokenize import sent_tokenize
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
import pytorch_lightning as pl

from transformers import (
    AdamW,
    T5ForConditionalGeneration,
    T5Tokenizer,
    get_linear_schedule_with_warmup
)

logger = logging.getLogger(__name__)


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class LoggingCallback(pl.Callback):
    def on_validation_end(self, trainer, pl_module):
        logger.info("***** Validation results *****")
        if pl_module.is_logger():
            metrics = trainer.callback_metrics
            # Log results
            for key in sorted(metrics):
                if key not in ["log", "progress_bar"]:
                    logger.info("{} = {}\n".format(key, str(metrics[key])))

    def on_test_end(self, trainer, pl_module):
        logger.info("***** Test results *****")

        if pl_module.is_logger():
            metrics = trainer.callback_metrics

            # Log and save results to file
            output_test_results_file = os.path.join(pl_module.hparams.output_dir, "test_results.txt")
            with open(output_test_results_file, "w") as writer:
                for key in sorted(metrics):
                    if key not in ["log", "progress_bar"]:
                        logger.info("{} = {}\n".format(key, str(metrics[key])))
                        writer.write("{} = {}\n".format(key, str(metrics[key])))


class GraphQlDataset(Dataset):
    def __init__(self, tokenizer, data_dir, type_path, max_len=512):
        self.pos_file_path = os.path.join(data_dir, 'dataset_' + type_path + "_pos.json")
        self.neg_file_path = os.path.join(data_dir, 'dataset_' + type_path + "_neg.json")

        self.max_len = max_len
        self.tokenizer = tokenizer
        self.inputs = []
        self.targets = []

        self._build()

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, index):
        source_ids = self.inputs[index]["input_ids"].squeeze()
        target_ids = self.targets[index]["input_ids"].squeeze()

        src_mask = self.inputs[index]["attention_mask"].squeeze()  # might need to squeeze
        target_mask = self.targets[index]["attention_mask"].squeeze()  # might need to squeeze

        return {"source_ids": source_ids, "source_mask": src_mask, "target_ids": target_ids, "target_mask": target_mask}

    def _build(self):
        self._build_examples_from_files(self.pos_file_path, 'consistent')
        self._build_examples_from_files(self.neg_file_path, 'inconsistent')

    def _build_examples_from_files(self, file_path, consistency):
        with open(file_path, 'r') as reader:
            dataset = json.load(reader)

        REPLACE_NO_SPACE = re.compile("[.;:!\'?,\"()\[\]]")
        REPLACE_WITH_SPACE = re.compile("(<br\s*/><br\s*/>)|(\-)|(\/)")

        for data_entry in tqdm(dataset):
            content = data_entry["content"].strip()
            content = REPLACE_NO_SPACE.sub("", content)
            content = REPLACE_WITH_SPACE.sub("", content)

            name = data_entry["name"].strip()
            name = REPLACE_NO_SPACE.sub("", name)
            name = REPLACE_WITH_SPACE.sub("", name)

            line = content + ' </s>' + name + ' </s>'

            target = consistency + " </s>"

            # tokenize inputs
            tokenized_inputs = self.tokenizer.batch_encode_plus(
                [line], max_length=self.max_len, pad_to_max_length=True, return_tensors="pt"
            )
            # tokenize targets
            tokenized_targets = self.tokenizer.batch_encode_plus(
                [target], max_length=2, pad_to_max_length=True, return_tensors="pt"
            )

            self.inputs.append(tokenized_inputs)
            self.targets.append(tokenized_targets)

def get_dataset(tokenizer, type_path, args):
  return GraphQlDataset(tokenizer=tokenizer, data_dir=args.data_dir, type_path=type_path,  max_len=args.max_seq_length)


class T5FineTuner(pl.LightningModule):
    def __init__(self, hparams):
        super(T5FineTuner, self).__init__()
        self.save_hyperparameters(hparams)
        self.training_step_outputs = []
        self.validation_step_outputs = []
        # pdb.set_trace()
        self.model = T5ForConditionalGeneration.from_pretrained(hparams.model_name_or_path)
        self.tokenizer = T5Tokenizer.from_pretrained(hparams.tokenizer_name_or_path)

    def is_logger(self):
        return self.trainer.global_rank <= 0

    def forward(
            self, input_ids, attention_mask=None, decoder_input_ids=None, decoder_attention_mask=None, labels=None
    ):
        return self.model(
            input_ids,
            attention_mask=attention_mask,
            decoder_input_ids=decoder_input_ids,
            decoder_attention_mask=decoder_attention_mask,
            labels=labels,
        )

    def _step(self, batch):
        labels = batch["target_ids"]
        labels[labels[:, :] == self.tokenizer.pad_token_id] = -100
        outputs = self(
            input_ids=batch["source_ids"],
            attention_mask=batch["source_mask"],
            labels=labels,
            decoder_attention_mask=batch['target_mask']
        )

        loss = outputs[0]

        return loss

    def training_step(self, batch, batch_idx):
        loss = self._step(batch)
        self.training_step_outputs.append(loss)
        return {"loss": loss}

    def on_train_epoch_end(self):
        epoch_average = torch.stack(self.training_step_outputs).mean()
        self.log("training_epoch_average", epoch_average)
        self.training_step_outputs.clear()  # free memory
        return {"avg_train_loss": epoch_average}

    def validation_step(self, batch, batch_idx):
        loss = self._step(batch)
        self.validation_step_outputs.append(loss)
        return {"val_loss": loss}

    def on_validation_epoch_end(self):
        epoch_average = torch.stack(self.validation_step_outputs).mean()
        self.log("val_loss", epoch_average)
        self.validation_step_outputs.clear()  # free memory
        return {"val_loss": epoch_average}

    def configure_optimizers(self):
        """Prepare optimizer and schedule (linear warmup and decay)"""

        model = self.model
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
                "weight_decay": self.hparams.weight_decay,
            },
            {
                "params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)],
                "weight_decay": 0.0,
            },
        ]
        optimizer = AdamW(optimizer_grouped_parameters, lr=self.hparams.learning_rate, eps=self.hparams.adam_epsilon)
        self.opt = optimizer
        return [optimizer]

    def get_tqdm_dict(self):
        tqdm_dict = {"loss": "{:.3f}".format(self.trainer.avg_loss), "lr": self.lr_scheduler.get_last_lr()[-1]}

        return tqdm_dict

    def train_dataloader(self):
        print('loadingtrain data')
        train_dataset = get_dataset(tokenizer=self.tokenizer, type_path="train", args=self.hparams)
        dataloader = DataLoader(train_dataset, batch_size=self.hparams.train_batch_size, drop_last=True, shuffle=True,
                                num_workers=4)
        t_total = (
                (len(dataloader.dataset) // (self.hparams.train_batch_size * max(1, self.hparams.n_gpu)))
                // self.hparams.gradient_accumulation_steps
                * float(self.hparams.num_train_epochs)
        )
        scheduler = get_linear_schedule_with_warmup(
            self.opt, num_warmup_steps=self.hparams.warmup_steps, num_training_steps=t_total
        )
        self.lr_scheduler = scheduler
        return dataloader

    def val_dataloader(self):
        print('loading val data')
        val_dataset = get_dataset(tokenizer=self.tokenizer, type_path="val", args=self.hparams)
        return DataLoader(val_dataset, batch_size=self.hparams.eval_batch_size, num_workers=4)


if __name__ == '__main__':
    set_seed(42)

    dir_name = os.path.dirname(os.path.realpath(__file__))
    root_path = Path(dir_name).parent
    dataset_pos_path = root_path.joinpath("dataset_generator").joinpath("dataset_pos.json")
    dataset_neg_path = root_path.joinpath("dataset_generator").joinpath("dataset_pos.json")

    args_dict = dict(
        data_dir="",  # path for data files
        output_dir="",  # path to save the checkpoints
        model_name_or_path='t5-base',
        tokenizer_name_or_path='t5-base',
        max_seq_length=512,
        learning_rate=3e-4,
        weight_decay=0.0,
        adam_epsilon=1e-8,
        warmup_steps=0,
        train_batch_size=8,
        eval_batch_size=8,
        num_train_epochs=2,
        gradient_accumulation_steps=16,
        n_gpu=1,
        early_stop_callback=False,
        fp_16=False,  # if you want to enable 16-bit training then install apex and set this to true
        opt_level='O1',
        max_grad_norm=1.0,  # if you enable 16-bit training then set this to a sensible value, 0.5 is a good default
        seed=42,
    )

    # Prepare tokenizer
    tokenizer = T5Tokenizer.from_pretrained('t5-base')

    ids_neg = tokenizer.encode('inconsistent </s>')
    ids_pos = tokenizer.encode('consistent </s>')
    len(ids_neg), len(ids_pos)

    # Prepare dataset
    dataset = GraphQlDataset(tokenizer, 'graphql_dataset', 'val', max_len=512)
    len(dataset)

    data = dataset[28]
    print(tokenizer.decode(data['source_ids']))
    print(tokenizer.decode(data['target_ids']))

    # Continue with model
    args_dict.update({'data_dir': 'graphql_dataset', 'output_dir': 't5_graphql_consistency', 'num_train_epochs': 2})
    args = argparse.Namespace(**args_dict)

    checkpoint_callback = pl.callbacks.ModelCheckpoint(
        dirpath=args.output_dir, filename="checkpoint", monitor="val_loss", mode="min", save_top_k=5
    )

    train_params = dict(
        accumulate_grad_batches=args.gradient_accumulation_steps,
        accelerator='gpu',
        max_epochs=args.num_train_epochs,
        precision=16 if args.fp_16 else 32,
        gradient_clip_val=args.max_grad_norm,
        callbacks=[LoggingCallback(), checkpoint_callback],
    )

    model = T5FineTuner(args)
    # Temporary for more speed:
    train_params["precision"] = '16-mixed'

    trainer = pl.Trainer(**train_params)
    trainer.fit(model)

    ## save the model this way so next time you can load it using T5ForConditionalGeneration.from_pretrained
    model.model.save_pretrained('t5_base_graphql_consistency')