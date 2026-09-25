
import re
import unicodedata
import pandas as pd
import json
from pathlib import Path

def normalize_unicode(text):
    """
    Normalize Unicode text while preserving non-ASCII characters.

    Handles:
    - None / missing values
    - Unicode compatibility normalization (NFKC)
    - Leading/trailing whitespace
    - Repeated whitespace
    """

    if text is None or pd.isna(text):
        return ""

    text = str(text)

    # Normalize Unicode while preserving characters such as
    # Hindi, French accents, etc.
    text = unicodedata.normalize("NFKC", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text




def extract_address_features(text):
    """
    Extract country-agnostic numeric information from an address.

    Returns:
        A dictionary containing:
        - numbers: numeric sequences found in the address

    No country-specific postal-code assumptions are made.
    """

    text = normalize_unicode(text)

    if not text:
        return {
            "numbers": []
        }

    # Extract standalone numeric sequences.
    # Examples:
    # "2100 Cameron Drive" -> ["2100"]
    # "Unit 4 Building 12" -> ["4", "12"]
    numbers = re.findall(r"\d+", text)

    return {
        "numbers": numbers
    }

import pandas as pd


def preprocess_dataframe(df):
    """
    Apply preprocessing to a source dataframe.

    Original columns are preserved.
    New columns:
        - business_name_clean
        - business_address_clean
        - address_numbers
    """

    df = df.copy()

    # Normalize business names
    df["business_name_clean"] = (
        df["business_name"]
        .apply(normalize_business_name)
    )

    # Normalize business addresses
    df["business_address_clean"] = (
        df["business_address"]
        .apply(normalize_business_address)
    )

    # Extract numeric address information
    df["address_numbers"] = (
        df["business_address"]
        .apply(lambda x: extract_address_features(x)["numbers"])
    )

    return df

# ============================================================
# Learned abbreviation system
# ============================================================

import json
from pathlib import Path

ABBREVIATION_JSON = (
    Path(__file__).resolve().parent.parent
    / "abbreviations_production.json"
)


def load_abbreviation_rules():
    """
    Load production abbreviation mappings learned from
    the training data.
    """
    with open(ABBREVIATION_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


ABBREVIATION_RULES = load_abbreviation_rules()

BUSINESS_NAME_ABBREVIATIONS = ABBREVIATION_RULES.get(
    "business_name", {}
)

BUSINESS_ADDRESS_ABBREVIATIONS = ABBREVIATION_RULES.get(
    "business_address", {}
)


def apply_abbreviations(text, mapping):
    """
    Apply token-level abbreviation replacements.

    Only complete tokens are replaced, so substrings inside
    normal words are not accidentally modified.
    """
    if not text or not mapping:
        return text

    # Longer tokens first
    tokens = sorted(mapping.keys(), key=len, reverse=True)

    for token in tokens:
        replacement = mapping[token]

        pattern = rf"\b{re.escape(token)}\b"

        text = re.sub(
            pattern,
            replacement,
            text
        )

    return text

# ============================================================
# Normalization using learned abbreviation mappings
# ============================================================

def normalize_business_name(text):
    """
    Normalize business names using learned production
    abbreviation mappings.
    """
    text = normalize_unicode(text)

    if not text:
        return ""

    # Lowercase while preserving Unicode
    text = text.lower()

    # Apply learned business-name abbreviations
    text = apply_abbreviations(
        text,
        BUSINESS_NAME_ABBREVIATIONS
    )

    # '&' -> 'and'
    text = text.replace("&", " and ")

    # Remove punctuation while preserving Unicode
    cleaned = []

    for char in text:
        category = unicodedata.category(char)

        if category.startswith("P"):
            cleaned.append(" ")
        else:
            cleaned.append(char)

    text = "".join(cleaned)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def normalize_business_address(text):
    """
    Normalize business addresses using learned production
    abbreviation mappings.
    """
    text = normalize_unicode(text)

    if not text:
        return ""

    # Lowercase while preserving Unicode
    text = text.lower()

    # Apply learned address abbreviations
    text = apply_abbreviations(
        text,
        BUSINESS_ADDRESS_ABBREVIATIONS
    )

    # '&' -> 'and'
    text = text.replace("&", " and ")

    # Remove punctuation while preserving Unicode
    cleaned = []

    for char in text:
        category = unicodedata.category(char)

        if category.startswith("P"):
            cleaned.append(" ")
        else:
            cleaned.append(char)

    text = "".join(cleaned)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text
