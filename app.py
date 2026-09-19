import streamlit as st

from product_search import (
    load_data,
    search_product,
    search_vendor,
    find_exact_product,
    find_exact_vendor,
    find_matching_products,
    find_matching_vendors,
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
# Session State
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("🔎 Vendor–Product Search System")

st.write(
    "Search for a product to find its vendors, "
    "or search for a vendor to find its products."
)


# --------------------------------------------------
# Display Previous Messages
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# --------------------------------------------------
# Chat Input
# --------------------------------------------------

query = st.chat_input(
    "Search for a product or vendor..."
)


# --------------------------------------------------
# Process New Message
# --------------------------------------------------

if query:

    query = query.strip()

    if not query:
        st.stop()


    # ----------------------------------------------
    # Display User Message
    # ----------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    with st.chat_message("user"):
        st.markdown(query)


    # ----------------------------------------------
    # Generate Response
    # ----------------------------------------------

    response = ""


    # ----------------------------------------------
    # 1. Exact Product Match
    # ----------------------------------------------

    exact_products = find_exact_product(
        df,
        query
    )

    if exact_products:

        product_name = exact_products[0]

        vendors = search_product(
            df,
            product_name
        )

        response += f"### Product: {product_name}\n\n"

        response += "**Associated Vendors:**\n\n"

        for index, vendor in enumerate(
            vendors,
            start=1
        ):
            response += f"{index}. {vendor}\n"


    else:

        # ------------------------------------------
        # 2. Exact Vendor Match
        # ------------------------------------------

        exact_vendors = find_exact_vendor(
            df,
            query
        )

        if exact_vendors:

            vendor_name = exact_vendors[0]

            products = search_vendor(
                df,
                vendor_name
            )

            response += f"### Vendor: {vendor_name}\n\n"

            response += "**Associated Products:**\n\n"

            for index, product in enumerate(
                products,
                start=1
            ):
                response += f"{index}. {product}\n"


        else:

            # --------------------------------------
            # 3. Partial Product Match
            # --------------------------------------

            matching_products = find_matching_products(
                df,
                query
            )


            # --------------------------------------
            # 4. Partial Vendor Match
            # --------------------------------------

            matching_vendors = find_matching_vendors(
                df,
                query
            )


            # --------------------------------------
            # Partial Product Results
            # --------------------------------------

            if matching_products:

                response += "### Matching Products\n\n"

                for product in matching_products:

                    response += f"**{product}**\n\n"

                    vendors = search_product(
                        df,
                        product
                    )

                    for vendor in vendors:
                        response += f"- {vendor}\n"

                    response += "\n"


            # --------------------------------------
            # Partial Vendor Results
            # --------------------------------------

            if matching_vendors:

                response += "### Matching Vendors\n\n"

                for vendor in matching_vendors:

                    response += f"**{vendor}**\n\n"

                    products = search_vendor(
                        df,
                        vendor
                    )

                    for product in products:
                        response += f"- {product}\n"

                    response += "\n"


            # --------------------------------------
            # No Match
            # --------------------------------------

            if not matching_products and not matching_vendors:

                response = (
                    "No matching product or vendor "
                    "was found in the database."
                )


    # ----------------------------------------------
    # Display Assistant Response
    # ----------------------------------------------

    with st.chat_message("assistant"):

        st.markdown(response)


    # ----------------------------------------------
    # Save Assistant Response
    # ----------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )