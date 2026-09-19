import streamlit as st

from product_search import (
    load_data,
    search,
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Vendor–Product Search",
    page_icon="🔎",
    layout="wide",
)


# =========================================================
# LOAD DATABASE
# =========================================================

try:

    df = load_data()

except Exception as e:

    st.error(
        f"Unable to load database: {e}"
    )

    st.stop()


# =========================================================
# CHAT MEMORY
# =========================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# =========================================================
# PAGE TITLE
# =========================================================

st.title(
    "🔎 Vendor–Product Search System"
)

st.write(
    "Search for a product to find its vendors, "
    "or search for a vendor to find its products."
)


# =========================================================
# DISPLAY PREVIOUS CHAT
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

query = st.chat_input(
    "Search for a product or vendor..."
)


# =========================================================
# PROCESS SEARCH
# =========================================================

if query:

    query = query.strip()

    if not query:
        st.stop()


    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    with st.chat_message("user"):

        st.markdown(query)


    # -----------------------------------------------------
    # SEARCH DATABASE
    # -----------------------------------------------------

    result = search(
        df,
        query
    )


    result_type = result["type"]

    matched_name = result["matched_name"]

    results = result["results"]


    # =====================================================
    # PRODUCT RESULT
    # =====================================================

    if result_type == "PRODUCT":

        response = (
            f"### Product: {matched_name}\n\n"
        )

        response += (
            "**Associated Vendors:**\n\n"
        )

        if results:

            for index, vendor in enumerate(
                results,
                start=1
            ):

                response += (
                    f"{index}. {vendor}\n"
                )

        else:

            response += (
                "No vendors found for this product."
            )


    # =====================================================
    # VENDOR RESULT
    # =====================================================

    elif result_type == "VENDOR":

        response = (
            f"### Vendor: {matched_name}\n\n"
        )

        response += (
            "**Associated Products:**\n\n"
        )

        if results:

            for index, product in enumerate(
                results,
                start=1
            ):

                response += (
                    f"{index}. {product}\n"
                )

        else:

            response += (
                "No products found for this vendor."
            )


    # =====================================================
    # MULTIPLE MATCH
    # =====================================================

    elif result_type == "MULTIPLE_MATCH":

        response = (
            "### Multiple Matches Found\n\n"
        )

        response += (
            "**Matching Product:**\n\n"
        )

        for product in results["products"]:

            response += (
                f"- {product}\n"
            )

        response += (
            "\n**Matching Vendor:**\n\n"
        )

        for vendor in results["vendors"]:

            response += (
                f"- {vendor}\n"
            )

        response += (
            "\nPlease enter the exact product "
            "or vendor name."
        )


    # =====================================================
    # NO MATCH
    # =====================================================

    else:

        response = (
            "No matching product or vendor "
            "was found in the database."
        )


    # =====================================================
    # ASSISTANT MESSAGE
    # =====================================================

    with st.chat_message("assistant"):

        st.markdown(
            response
        )


    # -----------------------------------------------------
    # SAVE ASSISTANT MESSAGE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )