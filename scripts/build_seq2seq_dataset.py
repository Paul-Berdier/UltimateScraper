#!/usr/bin/env python
import argparse
import json
from pathlib import Path

from ultimate_crawler.dataset import Seq2SeqDatasetBuilder


def main():
    parser = argparse.ArgumentParser(description="Build seq2seq dataset from crawled docs.")
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input JSONL (docs_filtered_with_slots.jsonl)"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output JSONL (seq2seq dataset)"
    )
    parser.add_argument(
        "--max-input-len",
        type=int,
        default=2048,
        help="Max chars for input text."
    )
    parser.add_argument(
        "--max-target-len",
        type=int,
        default=256,
        help="Max chars for target text."
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    def doc_iter():
        with in_path.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                yield json.loads(line)

    builder = Seq2SeqDatasetBuilder(
        max_input_len=args.max_input_len,
        max_target_len=args.max_target_len,
    )

    examples = builder.build_from_docs(doc_iter())
    builder.write_jsonl(examples, out_path)

    print(f"[INFO] Seq2seq dataset written to {out_path}")


if __name__ == "__main__":
    main()
