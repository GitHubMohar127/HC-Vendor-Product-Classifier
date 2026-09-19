import pandas as pd
from pathlib import Path


DATA_FILE = Path(__file__).parent / "data" / "Vendor_and_Product_details.xlsx"


def load_data():
    """Load vendor-product relationship data."""
    df = pd.read_excel(DATA_FILE)

    # Check required columns
    required_columns = {"Product", "Vendor"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            "Excel file must contain 'Product' and 'Vendor' columns."
        )

    # Remove empty rows
    df = df.dropna(subset=["Product", "Vendor"])

    # Convert values to strings
    df["Product"] = df["Product"].astype(str).str.strip()
    df["Vendor"] = df["Vendor"].astype(str).str.strip()

    return df


def search_product(df, query):
    """Find all vendors associated with a product."""
    matches = df[
        df["Product"].str.contains(
            query,
            case=False,
            na=False
        )
    ]

    vendors = (
        matches["Vendor"]
        .drop_duplicates()
        .tolist()
    )

    return vendors


def search_vendor(df, query):
    """Find all products associated with a vendor."""
    matches = df[
        df["Vendor"].str.contains(
            query,
            case=False,
            na=False
        )
    ]

    products = (
        matches["Product"]
        .drop_duplicates()
        .tolist()
    )

    return products


if __name__ == "__main__":

    df = load_data()

    print("\nProduct Search: Phenol")

    vendors = search_product(df, "Phenol")

    for vendor in vendors:
        print("-", vendor)

    print("\nVendor Search: LEO CHEMO PLAST")

    products = search_vendor(df, "LEO CHEMO PLAST")

    for product in products:
        print("-", product)