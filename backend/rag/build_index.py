"""Build the local vector index from an existing records.jsonl file."""

import argparse
import json
from pathlib import Path

from .embedding import MODEL_NAME, SentenceEmbedder
from .ingest import rechunk_records
from .index import DEFAULT_VECTOR_INDEX, build_index


def read_records(path):
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_records(path, records):
    with Path(path).open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "records",
        nargs="?",
        type=Path,
        default=Path(__file__).parent / "data" / "records.jsonl",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_VECTOR_INDEX)
    parser.add_argument(
        "--rechunk",
        action="store_true",
        help="rewrite legacy records.jsonl into section-aware chunks before embedding",
    )
    args = parser.parse_args()

    records = read_records(args.records)
    if args.rechunk:
        records = rechunk_records(records)
        write_records(args.records, records)
        print(f"wrote {len(records)} chunks to {args.records}")
    build_index(records, SentenceEmbedder(MODEL_NAME), args.output, MODEL_NAME)
    print(f"wrote {len(records)} vectors to {args.output}")


if __name__ == "__main__":
    main()
