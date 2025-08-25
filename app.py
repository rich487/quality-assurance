import streamlit as st
import pandas as pd
import uuid
from io import BytesIO

# GitHub-like theme
st.set_page_config(page_title="Excel Error Checker", page_icon="🐙", layout="wide")

# Reference Number
if "ref_number" not in st.session_state:
    st.session_state.ref_number = str(uuid.uuid4())[:8]

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown(f"**Reference Number:** `{st.session_state.ref_number}`")
    uploaded_files = st.file_uploader("📂 Upload Excel files", type=["xlsx"], accept_multiple_files=True)

if uploaded_files:
    # File selection
    file_names = [f.name for f in uploaded_files]
    selected_file = st.sidebar.selectbox("Select File", file_names)

    file_obj = [f for f in uploaded_files if f.name == selected_file][0]
    xls = pd.ExcelFile(file_obj)

    # Sheet selection
    sheet_name = st.sidebar.selectbox("Select Sheet", xls.sheet_names)
    df = pd.read_excel(file_obj, sheet_name=sheet_name)

    st.markdown(f"### 📄 File: **{selected_file}** | Sheet: **{sheet_name}**")

    # Choose error type
    error_type = st.radio("Select Error Type (GitHub Label style):", ["🟥 Major Error", "🟨 Minor Error"], horizontal=True)

    # Display table like GitHub issues
    st.markdown("### ✅ Mark Rows with Errors")
    selected_rows = []
    for i, row in df.iterrows():
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            checked = st.checkbox("", key=f"row_{i}")
        with col2:
            st.write(row.to_dict())
        if checked:
            selected_rows.append(i)

    # Apply "X" replacement
    if st.button("🔧 Apply Changes"):
        df_updated = df.copy()
        for idx in selected_rows:
            df_updated.iloc[idx, :] = "X"

        st.success(f"Applied {error_type} to {len(selected_rows)} row(s).")
        st.dataframe(df_updated, use_container_width=True)

        # Export updated Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_updated.to_excel(writer, index=False, sheet_name="Updated_Data")

        st.download_button(
            label="📥 Download Updated Excel",
            data=output.getvalue(),
            file_name=f"updated_{selected_file}",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("👆 Upload one or more Excel files to get started.")
