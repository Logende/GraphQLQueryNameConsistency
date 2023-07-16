import argparse
import seaborn as sn
import pandas as pd
import matplotlib.pyplot as plt

from torch.utils.data import DataLoader
from tqdm.auto import tqdm
from sklearn import metrics

from transformers import T5ForConditionalGeneration

import finetune_with_baset5

if __name__ == '__main__':

    args_dict = dict(
    )

    args_dict.update({'data_dir': 'tune', 'output_dir': 'graphql_consistency_model', 'num_train_epochs': 2})
    args = argparse.Namespace(**args_dict)
    model = finetune_with_baset5.T5FineTuner(args)

    # Load pretrained model
    model.model = T5ForConditionalGeneration.from_pretrained("/content/drive/MyDrive/finetune/graphql_consistency_model")
    model.model.to('cuda')

    # Load test dataset
    dataset = finetune_with_baset5.GraphQlDataset(finetune_with_baset5.tokenizer, 'tune', 'test', 512)
    loader = DataLoader(dataset, batch_size=32, num_workers=4)

    # Evaluate
    model.model.eval()
    outputs = []
    targets = []
    scores = []
    for batch in tqdm(loader):
        outs = model.model.generate(input_ids=batch['source_ids'].cuda(),
                                    attention_mask=batch['source_mask'].cuda(),
                                    max_length=2,
                                    return_dict_in_generate=True,
                                    output_scores=True)

        dec = [finetune_with_baset5.tokenizer.decode(ids).replace("<pad>", "") for ids in outs]
        target = [finetune_with_baset5.tokenizer.decode(ids).replace("</s>", "") for ids in batch["target_ids"]]
        score = outs['scores']

        outputs.extend(dec)
        targets.extend(target)
        scores.extend(score)

    for i, out in enumerate(outputs):
        if out not in ["consistent", "inconsistent"]:
            print(i, 'detected invalid prediction ' + str(out))

    metrics.accuracy_score(targets, outputs)
    print(str(targets))

    print(metrics.classification_report(targets, outputs))

    cm = metrics.confusion_matrix(targets, outputs)
    df_cm = pd.DataFrame(cm, index=["consistent", "inconsistent"], columns=["consistent", "inconsistent"])
    plt.figure(figsize=(10, 7))
    sn.heatmap(df_cm, annot=True, cmap='Purples', fmt='g')
