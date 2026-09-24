import streamlit as st

from product_search import (
    load_data,
    search,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Hindcon-Speciality-Vendor–Product-Search",
    page_icon="🔎",
    layout="wide",
)


# ============================================================
# LOAD DATABASE
# ============================================================

try:
    df = load_data()

except Exception as e:
    st.error(
        f"Unable to load database: {e}"
    )
    st.stop()


# ============================================================
# CHAT HISTORY
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# TITLE
# ============================================================

st.title(
    "Hindcon Speciality Vendor & Product Search System"
)

st.write(
    "Search for a product to find its vendors, "
    "or search for a vendor to find its products."
)


# ============================================================
# DISPLAY PREVIOUS CHAT
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):
        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

query = st.chat_input(
    "Search for a product or vendor..."
)


# ============================================================
# PROCESS SEARCH
# ============================================================

if query:

    query = query.strip()

    if not query:
        st.stop()

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    with st.chat_message("user"):
        st.markdown(query)

    # --------------------------------------------------------
    # SEARCH DATABASE
    # --------------------------------------------------------

    result = search(
        df,
        query,
    )

    result_type = result["type"]
    matched_name = result["matched_name"]
    results = result["results"]

    # ========================================================
    # PRODUCT RESULT
    # ========================================================

    if result_type == "PRODUCT":

        response = (
            f"### 📦 Product: {matched_name}\n\n"
        )

        response += (
            "### 🏢 Associated Vendors\n\n"
        )

        if results:

            # Excel-style Markdown table
            response += (
                "| Vendor | Contact No | Mail_id |\n"
            )

            response += (
                "|---|---|---|\n"
            )

            for vendor_info in results:

                vendor = vendor_info["vendor"]
                contact = vendor_info["contact"]
                mail_id = vendor_info["mail_id"]

                response += (
                    f"| {vendor} | "
                    f"{contact} | "
                    f"{mail_id} |\n"
                )

        else:

            response += (
                "No vendors found for this product."
            )

    # ========================================================
    # VENDOR RESULT
    # ========================================================

    elif result_type == "VENDOR":

        vendor_details = result.get(
            "vendor_details",
            {},
        )

        contact = vendor_details.get(
            "contact",
            "",
        )

        mail_id = vendor_details.get(
            "mail_id",
            "",
        )

        response = (
            f"### 🏢 Vendor: {matched_name}\n\n"
        )

        # ----------------------------------------------------
        # Vendor details table
        # ----------------------------------------------------

        response += (
            "### 📋 Vendor Details\n\n"
        )

        response += (
            "| Vendor | Contact No | Mail_id |\n"
        )

        response += (
            "|---|---|---|\n"
        )

        response += (
            f"| {matched_name} | "
            f"{contact} | "
            f"{mail_id} |\n\n"
        )

        # ----------------------------------------------------
        # Products
        # ----------------------------------------------------

        response += (
            "### 📦 Associated Products\n\n"
        )

        if results:

            for index, product in enumerate(
                results,
                start=1,
            ):

                response += (
                    f"{index}. {product}\n"
                )

        else:

            response += (
                "No products found for this vendor."
            )

    # ========================================================
    # MULTIPLE MATCH
    # ========================================================

    elif result_type == "MULTIPLE_MATCH":

        response = (
            "### 🔍 Multiple Matches Found\n\n"
        )

        response += (
            "**Matching Products:**\n\n"
        )

        for product in results["products"]:

            response += (
                f"- {product}\n"
            )

        response += (
            "\n**Matching Vendors:**\n\n"
        )

        for vendor in results["vendors"]:

            response += (
                f"- {vendor}\n"
            )

        response += (
            "\nPlease enter the exact product "
            "or vendor name."
        )

    # ========================================================
    # NO MATCH
    # ========================================================

    else:

        response = (
            "No matching product or vendor "
            "was found in the database."
        )

    # ========================================================
    # DISPLAY ASSISTANT RESPONSE
    # ========================================================

    with st.chat_message("assistant"):

        st.markdown(response)

    # ========================================================
    # SAVE ASSISTANT RESPONSE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )