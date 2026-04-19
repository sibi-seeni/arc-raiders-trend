"""
RoBERTa Sentiment Classification

Author: Sibi Seenivasan
Date: March 2026
"""

import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import DataLoader, Dataset
import os, time, warnings, gc
from tqdm.auto import tqdm

warnings.filterwarnings("ignore")


class TextDataset(Dataset):
    def __init__(self, texts):
        self.texts = texts
    def __len__(self):
        return len(self.texts)
    def __getitem__(self, idx):
        return self.texts[idx]


def setup_model():
    torch.set_num_threads(4)
    torch.set_num_interop_threads(2)

    device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
    print(f"Device: {device}")

    model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()
    model.to(device)

    return model, tokenizer, device


def classify_chunk(texts, model, tokenizer, device, batch_size=64, max_length=128):
    dataset = TextDataset(texts)
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=False,
        collate_fn=lambda batch: tokenizer(
            batch,
            padding="longest",
            truncation=True,
            max_length=max_length,
            return_tensors="pt"
        )
    )

    prob_chunks = []
    with torch.inference_mode():
        for batch in dataloader:
            batch = {k: v.to(device) for k, v in batch.items()}
            logits = model(**batch, return_dict=False)[0]
            probs = torch.softmax(logits, dim=1)
            prob_chunks.append(probs.cpu().numpy())

    all_probs = np.concatenate(prob_chunks, axis=0)

    neg, neu, pos = all_probs[:, 0], all_probs[:, 1], all_probs[:, 2]

    labels_idx = np.argmax(all_probs, axis=1)
    conf = np.max(all_probs, axis=1)

    label_map = np.array([-1, 0, 1])
    labels = label_map[labels_idx]

    return pd.DataFrame({
        'roberta_sentiment_neg': neg,
        'roberta_sentiment_neu': neu,
        'roberta_sentiment_pos': pos,
        'roberta_sentiment_label': labels,
        'roberta_confidence': conf
    })


def main(input_file='data/comments_for_analysis.csv',
         output_file='data/roberta_classifications.csv',
         batch_size=128,
         chunk_size=10000,
         sample_size=None):

    start_time = time.time()

    print("\n" + "=" * 80)
    print("ROBERTA SENTIMENT CLASSIFICATION")
    print("=" * 80 + "\n")

    if not os.path.exists(input_file):
        print("Input file not found")
        return

    model, tokenizer, device = setup_model()

    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)

    chunk_iter = pd.read_csv(input_file, chunksize=chunk_size)

    first_write = True
    total_rows = 0
    classification_time = 0

    print(f"Chunk size: {chunk_size}")
    print(f"Batch size: {batch_size}\n")

    for chunk_id, chunk in enumerate(chunk_iter):
        if sample_size:
            if total_rows >= sample_size:
                break
            remaining = sample_size - total_rows
            chunk = chunk.iloc[:remaining]

        print(f"Processing chunk {chunk_id + 1}")

        texts = chunk['text_preprocessed'].fillna('').astype(str).tolist()

        chunk_start = time.time()

        results = classify_chunk(texts, model, tokenizer, device, batch_size=batch_size)

        classification_time += time.time() - chunk_start

        chunk_out = pd.concat([chunk, results], axis=1)

        chunk_out.to_csv(
            output_file,
            mode='w' if first_write else 'a',
            header=first_write,
            index=False
        )

        first_write = False
        total_rows += len(chunk)

        print(f"Chunk rows: {len(chunk):,}")
        print(f"Total processed: {total_rows:,}\n")

        del chunk, texts, results, chunk_out
        gc.collect()

    total_time = time.time() - start_time
    speed = total_rows / classification_time

    print("\n" + "=" * 80)
    print("PERFORMANCE")
    print("=" * 80)

    print(f"Rows processed: {total_rows:,}")
    print(f"Classification time: {classification_time / 60:.1f} min")
    print(f"Total runtime: {total_time / 60:.1f} min")
    print(f"Speed: {speed:.1f} comments/sec")

    print("\nDone\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='data/comments_for_analysis.csv')
    parser.add_argument('--output', default='data/roberta_classifications.csv')
    parser.add_argument('--batch-size', type=int, default=128)
    parser.add_argument('--chunk-size', type=int, default=10000)
    parser.add_argument('--sample', type=int, default=None)

    args = parser.parse_args()

    main(
        input_file=args.input,
        output_file=args.output,
        batch_size=args.batch_size,
        chunk_size=args.chunk_size,
        sample_size=args.sample
    )