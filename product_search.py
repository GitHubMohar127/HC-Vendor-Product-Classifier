import pandas as pd
from pathlib import Path
from rapidfuzz import fuzz

DATA_FILE = Path(__file__).parent / "data" / "Vendor_and_Product_details.xlsx"


# =========================================================
# LOAD DATA
# =========================================================

def load_data():
    """Load vendor-product relationship data."""

    df = pd.read_excel(DATA_FILE)

    required_columns = {"Product", "Vendor"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            "Excel file must contain 'Product' and 'Vendor' columns."
        )

    df = df.dropna(subset=["Product", "Vendor"]).copy()

    df["Product"] = (
        df["Product"]
        .astype(str)
        .str.strip()
    )

    df["Vendor"] = (
        df["Vendor"]
        .astype(str)
        .str.strip()
    )

    return df


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(text):
    """
    Normalize text before searching.

    Examples:
        LEO CHEMO PLAST -> leo chemo plast
        Leo-Chemo Plast -> leo chemo plast
        PHENOL -> phenol
    """

    text = str(text).lower().strip()

    for character in ["-", "_", "/", ".", ","]:
        text = text.replace(character, " ")

    text = " ".join(text.split())

    return text


# =========================================================
# GET UNIQUE VALUES
# =========================================================

def get_unique_values(df, column):
    """Return unique non-empty values from a column."""

    return (
        df[column]
        .dropna()
        .astype(str)
        .str.strip()
        .drop_duplicates()
        .tolist()
    )


# =========================================================
# EXACT MATCH
# =========================================================

def find_exact_product(df, query):
    """Find product using exact normalized matching."""

    query_normalized = normalize_text(query)

    products = get_unique_values(df, "Product")

    for product in products:

        if normalize_text(product) == query_normalized:
            return [product]

    return []


def find_exact_vendor(df, query):
    """Find vendor using exact normalized matching."""

    query_normalized = normalize_text(query)

    vendors = get_unique_values(df, "Vendor")

    for vendor in vendors:

        if normalize_text(vendor) == query_normalized:
            return [vendor]

    return []


# =========================================================
# TOKEN MATCHING
# =========================================================

def token_match_score(query, value):
    """
    Compare query tokens with value tokens.

    This helps with searches such as:

        LEO PLAST
        ->
        LEO CHEMO PLAST

    and:

        PHANOL
        ->
        PHENOL
    """

    query_normalized = normalize_text(query)
    value_normalized = normalize_text(value)

    if not query_normalized or not value_normalized:
        return 0

    query_tokens = query_normalized.split()
    value_tokens = value_normalized.split()

    scores = []

    for query_token in query_tokens:

        # Exact token
        if query_token in value_tokens:
            scores.append(100)
            continue

        best_token_score = 0

        for value_token in value_tokens:

            # Avoid fuzzy matching extremely short words
            if len(query_token) < 4:
                continue

            score = fuzz.ratio(
                query_token,
                value_token
            )

            if score > best_token_score:
                best_token_score = score

        scores.append(best_token_score)

    if not scores:
        return 0

    # Every query token should have a reasonable match
    return min(scores)


# =========================================================
# GENERAL MATCH SCORE
# =========================================================

def match_score(query, value):
    """
    Calculate a controlled matching score.

    Priority:
        1. Exact
        2. Substring
        3. Token matching
        4. Fuzzy matching
    """

    query_normalized = normalize_text(query)
    value_normalized = normalize_text(value)

    if not query_normalized or not value_normalized:
        return 0

    # -----------------------------------------
    # Exact match
    # -----------------------------------------

    if query_normalized == value_normalized:
        return 100


    # -----------------------------------------
    # Query is contained in value
    # -----------------------------------------

    if query_normalized in value_normalized:
        return 98


    # -----------------------------------------
    # Value is contained in query
    # -----------------------------------------

    if value_normalized in query_normalized:
        return 96


    # -----------------------------------------
    # Token matching
    # -----------------------------------------

    token_score = token_match_score(
        query_normalized,
        value_normalized
    )


    # -----------------------------------------
    # Full-string fuzzy matching
    # -----------------------------------------

    ratio_score = fuzz.ratio(
        query_normalized,
        value_normalized
    )

    partial_score = 0

    # Partial matching is useful for longer searches
    if len(query_normalized) >= 5:

        partial_score = fuzz.partial_ratio(
            query_normalized,
            value_normalized
        )


    # WRatio handles different string lengths better
    weighted_score = fuzz.WRatio(
        query_normalized,
        value_normalized
    )


    return max(
        token_score,
        ratio_score,
        partial_score,
        weighted_score
    )


# =========================================================
# FIND BEST MATCH
# =========================================================

def find_best_match(query, values):
    """
    Find the strongest matching value.

    Returns:
        (matched_value, score)

    If nothing is strong enough:
        (None, 0)
    """

    query_normalized = normalize_text(query)

    if not query_normalized:
        return None, 0

    best_value = None
    best_score = 0

    for value in values:

        score = match_score(
            query_normalized,
            value
        )

        if score > best_score:
            best_score = score
            best_value = value


    # -------------------------------------------------
    # Matching thresholds
    # -------------------------------------------------

    # Very short searches should not use aggressive
    # fuzzy matching because they can create false matches.
    if len(query_normalized) <= 3:

        if best_score >= 98:
            return best_value, best_score

        return None, 0


    # Normal searches
    if best_score >= 78:
        return best_value, best_score


    return None, 0


# =========================================================
# SEARCH PRODUCT
# =========================================================

def search_product(df, query):
    """
    Find all vendors associated with a product.
    """

    exact_products = find_exact_product(
        df,
        query
    )

    if exact_products:

        product = exact_products[0]

        vendors = (
            df[
                df["Product"] == product
            ]["Vendor"]
            .dropna()
            .astype(str)
            .str.strip()
            .drop_duplicates()
            .tolist()
        )

        return vendors


    products = get_unique_values(
        df,
        "Product"
    )

    matched_product, score = find_best_match(
        query,
        products
    )

    if matched_product is None:
        return []


    vendors = (
        df[
            df["Product"] == matched_product
        ]["Vendor"]
        .dropna()
        .astype(str)
        .str.strip()
        .drop_duplicates()
        .tolist()
    )

    return vendors


# =========================================================
# SEARCH VENDOR
# =========================================================

def search_vendor(df, query):
    """
    Find all products associated with a vendor.
    """

    exact_vendors = find_exact_vendor(
        df,
        query
    )

    if exact_vendors:

        vendor = exact_vendors[0]

        products = (
            df[
                df["Vendor"] == vendor
            ]["Product"]
            .dropna()
            .astype(str)
            .str.strip()
            .drop_duplicates()
            .tolist()
        )

        return products


    vendors = get_unique_values(
        df,
        "Vendor"
    )

    matched_vendor, score = find_best_match(
        query,
        vendors
    )

    if matched_vendor is None:
        return []


    products = (
        df[
            df["Vendor"] == matched_vendor
        ]["Product"]
        .dropna()
        .astype(str)
        .str.strip()
        .drop_duplicates()
        .tolist()
    )

    return products


# =========================================================
# FIND MATCHING PRODUCTS
# =========================================================

def find_matching_products(df, query):
    """
    Find product names that reasonably match the query.
    """

    products = get_unique_values(
        df,
        "Product"
    )

    matches = []

    for product in products:

        score = match_score(
            query,
            product
        )

        if score >= 78:
            matches.append(
                (score, product)
            )


    # Highest score first
    matches.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        product
        for score, product in matches
    ]


# =========================================================
# FIND MATCHING VENDORS
# =========================================================

def find_matching_vendors(df, query):
    """
    Find vendor names that reasonably match the query.
    """

    vendors = get_unique_values(
        df,
        "Vendor"
    )

    matches = []

    for vendor in vendors:

        score = match_score(
            query,
            vendor
        )

        if score >= 78:
            matches.append(
                (score, vendor)
            )


    # Highest score first
    matches.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        vendor
        for score, vendor in matches
    ]


# =========================================================
# MAIN SEARCH FUNCTION
# =========================================================

def search(df, query):
    """
    Main search engine.

    Priority:

    1. Exact Product
    2. Exact Vendor
    3. Strong Product Match
    4. Strong Vendor Match
    5. No Match

    Returns a dictionary containing:

        type
        matched_name
        results
    """

    query = str(query).strip()

    if not query:
        return {
            "type": "NO_MATCH",
            "matched_name": None,
            "results": []
        }


    # =====================================================
    # 1. EXACT PRODUCT
    # =====================================================

    exact_products = find_exact_product(
        df,
        query
    )

    if exact_products:

        product = exact_products[0]

        vendors = (
            df[
                df["Product"] == product
            ]["Vendor"]
            .dropna()
            .astype(str)
            .str.strip()
            .drop_duplicates()
            .tolist()
        )

        return {
            "type": "PRODUCT",
            "matched_name": product,
            "results": vendors
        }


    # =====================================================
    # 2. EXACT VENDOR
    # =====================================================

    exact_vendors = find_exact_vendor(
        df,
        query
    )

    if exact_vendors:

        vendor = exact_vendors[0]

        products = (
            df[
                df["Vendor"] == vendor
            ]["Product"]
            .dropna()
            .astype(str)
            .str.strip()
            .drop_duplicates()
            .tolist()
        )

        return {
            "type": "VENDOR",
            "matched_name": vendor,
            "results": products
        }


    # =====================================================
    # 3. FUZZY PRODUCT MATCH
    # =====================================================

    products = get_unique_values(
        df,
        "Product"
    )

    matched_product, product_score = find_best_match(
        query,
        products
    )


    # =====================================================
    # 4. FUZZY VENDOR MATCH
    # =====================================================

    vendors = get_unique_values(
        df,
        "Vendor"
    )

    matched_vendor, vendor_score = find_best_match(
        query,
        vendors
    )


    # =====================================================
    # Compare Product vs Vendor
    # =====================================================

    if matched_product and matched_vendor:

        # Product has stronger match
        if product_score > vendor_score:

            result_vendors = (
                df[
                    df["Product"] == matched_product
                ]["Vendor"]
                .dropna()
                .astype(str)
                .str.strip()
                .drop_duplicates()
                .tolist()
            )

            return {
                "type": "PRODUCT",
                "matched_name": matched_product,
                "results": result_vendors
            }


        # Vendor has stronger match
        elif vendor_score > product_score:

            result_products = (
                df[
                    df["Vendor"] == matched_vendor
                ]["Product"]
                .dropna()
                .astype(str)
                .str.strip()
                .drop_duplicates()
                .tolist()
            )

            return {
                "type": "VENDOR",
                "matched_name": matched_vendor,
                "results": result_products
            }


        # Same score
        else:

            return {
                "type": "MULTIPLE_MATCH",
                "matched_name": None,
                "results": {
                    "products": [matched_product],
                    "vendors": [matched_vendor]
                }
            }


    # =====================================================
    # Only Product matched
    # =====================================================

    if matched_product:

        result_vendors = (
            df[
                df["Product"] == matched_product
            ]["Vendor"]
            .dropna()
            .astype(str)
            .str.strip()
            .drop_duplicates()
            .tolist()
        )

        return {
            "type": "PRODUCT",
            "matched_name": matched_product,
            "results": result_vendors
        }


    # =====================================================
    # Only Vendor matched
    # =====================================================

    if matched_vendor:

        result_products = (
            df[
                df["Vendor"] == matched_vendor
            ]["Product"]
            .dropna()
            .astype(str)
            .str.strip()
            .drop_duplicates()
            .tolist()
        )

        return {
            "type": "VENDOR",
            "matched_name": matched_vendor,
            "results": result_products
        }


    # =====================================================
    # No Match
    # =====================================================

    return {
        "type": "NO_MATCH",
        "matched_name": None,
        "results": []
    }