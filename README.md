# Preprocessing & Data Cleaning

Preprocessing module for cleaning and normalizing business names and addresses before blocking and entity matching.

## What It Does

- Unicode NFKC normalization while preserving Hindi, French, and other non-ASCII characters.
- Whitespace normalization.
- Business-name normalization.
- Address normalization.
- Learned abbreviation normalization using `abbreviations_production.json`.
- `&` → `and` normalization.
- Unicode-safe punctuation removal.
- Country-agnostic address number extraction.
- Missing-value handling.
- Adds cleaned fields while preserving the original columns.

## ⚠️ Required Folder Structure

**Keep the following folder structure exactly as shown:**

```text
amazon-ml-2026/
├── abbreviations_production.json
└── src/
    └── preprocess.py
```
## How to Use the Code
- download the preprocess in src 
- download the abbreviations_production.json on the main file 
- follow the exact structure given above
-  write this code 
```python
import sys
import pandas as pd

sys.path.insert(0, "src")

import preprocess

# Load your raw dataset
df = pd.read_csv(
    "path/to/your/source.tsv",
    sep="\t"
)

# Run the complete preprocessing pipeline
df = preprocess.preprocess_dataframe(df)

# The following columns are now available:
# business_name_clean
# business_address_clean
# address_numbers

print(df.head())
