import streamlit as st

from product_search import (
    load_data,
    search_product,
    search_vendor,
)


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Vendor–Product Search",
    page_icon="🔎",
    layout="wide",
)


# --------------------------------------------------
# Load Data
# --------------------------------------------------

try:
    df = load_data()

except Exception as e:
    st.error(f"Unable to load database: {e}")
    st.stop()


# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("🔎 Vendor–Product Search System")

st.write(
    "Search for a product to find its vendors, "
    "or search for a vendor to find its products."
)


# --------------------------------------------------
# Search Box
# --------------------------------------------------

query = st.text_input(
    "Search Product or Vendor",
    placeholder="Example: Phenol or LEO CHEMO PLAST",
)


# --------------------------------------------------
# Search
# --------------------------------------------------

if query.strip():

    query = query.strip()

    # ----------------------------------------------
    # Search as Product
    # ----------------------------------------------

    product_vendors = search_product(df, query)

    # ----------------------------------------------
    # Search as Vendor
    # ----------------------------------------------

    vendor_products = search_vendor(df, query)


    # ----------------------------------------------
    # Product Result
    # ----------------------------------------------

    if product_vendors:

        st.subheader(f"Product: {query}")

        st.write("**Associated Vendors:**")

        for index, vendor in enumerate(product_vendors, start=1):
            st.write(f"{index}. {vendor}")


    # ----------------------------------------------
    # Vendor Result
    # ----------------------------------------------

    if vendor_products:

        st.subheader(f"Vendor: {query}")

        st.write("**Associated Products:**")

        for index, product in enumerate(vendor_products, start=1):
            st.write(f"{index}. {product}")


    # ----------------------------------------------
    # No Match
    # ----------------------------------------------

    if not product_vendors and not vendor_products:

        st.warning(
            "No matching product or vendor was found in the database."
        )