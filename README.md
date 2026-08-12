# CSV Q&A with an LLM

Asking natural-language questions about a CSV by putting the whole table in the
prompt — the simplest thing that works, and worth knowing before reaching for a
vector store.

```
CSV → CSVLoader (one Document per row) → whole table into the prompt → Claude → answer
```

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add your ANTHROPIC_API_KEY
python lauch.py
```

## Why no embeddings here

The sample data is 50 rows (~945 tokens), about 0.5% of the context window. At
that size, stuffing every row into the prompt beats retrieval on every axis: no
index to build, no chunking decisions, and the model sees all the data — so it can
answer aggregate questions like "who has the highest salary?" that top-k retrieval
would get wrong.

The rough crossover:

| Rows | Tokens | Approach |
| --- | --- | --- |
| < ~1,000 | < 13K | Put it all in the prompt |
| 1k–100k, lookup | — | RAG over rows (one Document per row, no text splitter) |
| Any size, aggregation | — | Text-to-SQL — let the model write the query, let SQLite do the arithmetic |

Aggregation is the one that fails silently: retrieval hands the model three rows
out of thousands, and it confidently sums those three.

## Data

`docs/employees.csv` — the Oracle HR sample schema (fictional employees).
