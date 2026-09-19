import pandas as pd
from pathlib import Path

from rapidfuzz import fuzz


DATA_FILE = Path(__file__).parent / "data" / "Vendor_and_Product_details.xlsx"


# --------------------------------------------------
# Load Data
# --------------------------------------------------

def load_data():
    """Load vendor-product relationship data."""

    df = pd.read_excel(DATA_FILE)

    required_columns = {"Product", "Vendor"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            "Excel file must contain 'Product' and 'Vendor' columns."
        )

    df = df.dropna(subset=["Product", "Vendor"])

    df["Product"] = df["Product"].astype(str).str.strip()
    df["Vendor"] = df["Vendor"].astype(str).str.strip()

    return df


# --------------------------------------------------
# Text Normalization
# --------------------------------------------------

def normalize_text(text):
    """
    Normalize text for searching.

    Example:
    'LEO CHEMO PLAST' -> 'leo chemo plast'
    'Leo-Chemo Plast' -> 'leo chemo plast'
    """

    text = str(text).lower().strip()

    # Replace common separators with spaces
    for character in ["-", "_", "/", ".", ","]:
        text = text.replace(character, " ")

    # Remove extra spaces
    text = " ".join(text.split())

    return text


# --------------------------------------------------
# Fuzzy Matching
# --------------------------------------------------

def is_fuzzy_match(query, value):
    """
    Determine whether the query reasonably matches
    a database value.
    """

    query_normalized = normalize_text(query)
    value_normalized = normalize_text(value)

    if not query_normalized or not value_normalized:
        return False

    # Exact match
    if query_normalized == value_normalized:
        return True

    # Normal substring match
    if query_normalized in value_normalized:
        return True

    # Token-based matching
    query_tokens = set(query_normalized.split())
    value_tokens = set(value_normalized.split())

    if query_tokens and query_tokens.issubset(value_tokens):
        return True

    # Fuzzy matching
    score = fuzz.ratio(
        query_normalized,
        value_normalized
    )

    # Partial fuzzy matching
    partial_score = fuzz.partial_ratio(
        query_normalized,
        value_normalized
    )

    return (
        score >= 75
        or partial_score >= 80
    )


# --------------------------------------------------
# Exact Product
# --------------------------------------------------

def find_exact_product(df, query):

    query_normalized = normalize_text(query)

    products = []

    for product in df["Product"].drop_duplicates():

        if normalize_text(product) == query_normalized:
            products.append(product)

    return products


# --------------------------------------------------
# Exact Vendor
# --------------------------------------------------

def find_exact_vendor(df, query):

    query_normalized = normalize_text(query)

    vendors = []

    for vendor in df["Vendor"].drop_duplicates():

        if normalize_text(vendor) == query_normalized:
            vendors.append(vendor)

    return vendors


# --------------------------------------------------
# Product Search
# --------------------------------------------------

def search_product(df, query):

    vendors = []

    for product in df["Product"].drop_duplicates():

        if is_fuzzy_match(query, product):

            matches = df[
                df["Product"] == product
            ]["Vendor"].tolist()

            vendors.extend(matches)

    return list(dict.fromkeys(vendors))


# --------------------------------------------------
# Vendor Search
# --------------------------------------------------

def search_vendor(df, query):

    products = []

    for vendor in df["Vendor"].drop_duplicates():

        if is_fuzzy_match(query, vendor):

            matches = df[
                df["Vendor"] == vendor
            ]["Product"].tolist()

            products.extend(matches)

    return list(dict.fromkeys(products))


# --------------------------------------------------
# Partial Product Search
# --------------------------------------------------

def find_matching_products(df, query):

    products = []

    for product in df["Product"].drop_duplicates():

        if is_fuzzy_match(query, product):
            products.append(product)

    return products


# --------------------------------------------------
# Partial Vendor Search
# --------------------------------------------------

def find_matching_vendors(df, query):

    vendors = []

    for vendor in df["Vendor"].drop_duplicates():

        if is_fuzzy_match(query, vendor):
            vendors.append(vendor)

    return vendors