import os
import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Contract Intelligence Platform",
    layout="wide",
)

st.title("Contract Intelligence Platform")

page = st.sidebar.radio(
    "Navigation",
    [
        "Upload Contract",
        "Contracts",
        "Semantic Search",
        "Chat",
        "Expiring Contracts",
    ],
)


def get_contracts():
    response = requests.get(f"{BACKEND_URL}/contracts", timeout=60)
    response.raise_for_status()
    return response.json()["contracts"]


if page == "Upload Contract":
    st.header("Upload Contract")

    uploaded_file = st.file_uploader(
        "Upload PDF, DOCX or TXT",
        type=["pdf", "docx", "txt"],
    )

    if uploaded_file is not None:
        if st.button("Process contract"):
            with st.spinner("Processing contract..."):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type,
                    )
                }

                response = requests.post(
                    f"{BACKEND_URL}/contracts/upload",
                    files=files,
                    timeout=300,
                )

                if response.ok:
                    st.success("Contract processed successfully.")
                    st.json(response.json())
                else:
                    st.error(response.text)


elif page == "Contracts":
    st.header("Contracts")

    try:
        contracts = get_contracts()

        if contracts:
            df = pd.DataFrame(contracts)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No contracts found.")

    except Exception as e:
        st.error(str(e))


elif page == "Semantic Search":
    st.header("Semantic Search")

    query = st.text_input(
        "Search query",
        placeholder="contracts with early termination penalties",
    )

    contract_id_input = st.text_input(
        "Optional contract ID",
        placeholder="Leave empty to search all contracts",
    )

    k = st.slider("Number of results", 1, 10, 5)

    if st.button("Search"):
        payload = {
            "query": query,
            "k": k,
            "contract_id": int(contract_id_input) if contract_id_input else None,
        }

        response = requests.post(
            f"{BACKEND_URL}/search/semantic",
            json=payload,
            timeout=120,
        )

        if response.ok:
            data = response.json()

            for result in data["results"]:
                st.markdown("---")
                st.write(result["content"])
                st.json(result["metadata"])
                st.caption(f"Score: {result['score']}")
        else:
            st.error(response.text)


elif page == "Chat":
    st.header("Chat")

    mode = st.radio("Mode", ["Global", "Specific contract"])

    contract_id = None

    if mode == "Specific contract":
        contract_id = st.number_input("Contract ID", min_value=1, step=1)

    question = st.text_area(
        "Question",
        placeholder="What are the tenant's maintenance obligations?",
    )

    k = st.slider("Context chunks", 1, 10, 5)

    if st.button("Ask"):
        payload = {
            "question": question,
            "k": k,
        }

        if mode == "Global":
            url = f"{BACKEND_URL}/chat/global"
        else:
            url = f"{BACKEND_URL}/chat/contract/{contract_id}"

        response = requests.post(
            url,
            json=payload,
            timeout=180,
        )

        if response.ok:
            data = response.json()

            st.subheader("Answer")
            st.write(data["answer"])

            st.subheader("Sources")
            st.json(data["sources"])
        else:
            st.error(response.text)


elif page == "Expiring Contracts":
    st.header("Expiring Contracts")

    days = st.number_input("Days", min_value=1, value=90)

    if st.button("Generate report"):
        response = requests.get(
            f"{BACKEND_URL}/contracts/reports/expiring",
            params={"days": days},
            timeout=60,
        )

        if response.ok:
            data = response.json()
            contracts = data["contracts"]

            if contracts:
                st.dataframe(pd.DataFrame(contracts), use_container_width=True)
            else:
                st.info("No expiring contracts found.")
        else:
            st.error(response.text)
