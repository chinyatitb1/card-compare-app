import streamlit as st
import pandas as pd
import numpy as np
from typing import Optional

# ---------- Page config ----------
st.set_page_config(
    page_title="Smartcard Comparison Tool",
    layout="wide",
    page_icon="💳",
)

# ---------- Header ----------
st.markdown(
    """
    <h1 style="text-align:center; margin-bottom:0.2rem;">Smartcard Comparison Tool</h1>
    <p style="text-align:center; color: #888; font-size:0.9rem;">
        Upload two datasets and compare distinct smartcard numbers across them.
    </p>
    """,
    unsafe_allow_html=True,
)

st.write("")  # spacer


# ---------- Helpers ----------
def load_table(uploaded_file) -> Optional[pd.DataFrame]:
    if uploaded_file is None:
        return None

    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file)

    uploaded_file.seek(0)
    return pd.read_excel(uploaded_file)


def guess_sc_col(cols):
    for c in cols:
        if "smartcard" in c.lower():
            return c
    return cols[0] if len(cols) > 0 else None


def normalize_smartcards(series: pd.Series) -> pd.Series:
    """
    Convert values to clean string smartcard numbers:
    - Handle ints/floats without leaving `.0`
    - Strip whitespace
    - Drop nulls
    """
    def _norm(x):
        if pd.isna(x):
            return None
        if isinstance(x, (int, np.integer)):
            return str(x)
        if isinstance(x, float):
            # If it's effectively an integer, drop .0
            if x.is_integer():
                return str(int(x))
            # Otherwise format nicely without scientific notation
            return f"{x:.15g}"
        s = str(x).strip()
        return s

    return series.map(_norm).dropna()


# ---------- Sidebar: Inputs ----------
with st.sidebar:
    st.markdown("### 📂 Upload Files")

    file1 = st.file_uploader(
        "File 1 (CSV / Excel, no password)",
        type=["csv", "xlsx", "xls"],
        key="file1",
    )
    file2 = st.file_uploader(
        "File 2 (CSV / Excel, no password)",
        type=["csv", "xlsx", "xls"],
        key="file2",
    )

    df1 = df2 = None
    col1_name = col2_name = None

    file1_label = file1.name if file1 is not None else "File 1"
    file2_label = file2.name if file2 is not None else "File 2"

    if file1 is not None:
        df1 = load_table(file1)

    if file2 is not None:
        df2 = load_table(file2)

    if df1 is not None and df2 is not None:
        st.markdown("---")
        st.markdown("### 🔑 Select Smartcard Columns")

        default_col1 = guess_sc_col(df1.columns)
        default_col2 = guess_sc_col(df2.columns)

        col1_name = st.selectbox(
            f"Smartcard column in {file1_label}",
            options=df1.columns,
            index=list(df1.columns).index(default_col1) if default_col1 else 0,
        )
        col2_name = st.selectbox(
            f"Smartcard column in {file2_label}",
            options=df2.columns,
            index=list(df2.columns).index(default_col2) if default_col2 else 0,
        )

        st.markdown("---")
        run_compare = st.button("🚀 Run Comparison", use_container_width=True)
    else:
        run_compare = False

# ---------- Main area: show uploaded file structures ----------
if df1 is not None or df2 is not None:
    st.markdown("### 📁 Uploaded Files Overview")

    colA, colB = st.columns(2)

    if df1 is not None:
        with colA:
            st.markdown(f"#### {file1_label}")
            st.dataframe(
                pd.DataFrame(
                    {"Column": df1.columns, "Data Type": [str(t) for t in df1.dtypes]}
                ),
                use_container_width=True,
                height=300,
            )

    if df2 is not None:
        with colB:
            st.markdown(f"#### {file2_label}")
            st.dataframe(
                pd.DataFrame(
                    {"Column": df2.columns, "Data Type": [str(t) for t in df2.dtypes]}
                ),
                use_container_width=True,
                height=300,
            )

    st.write("")  # spacer

# ---------- Comparison logic ----------
if df1 is not None and df2 is not None and col1_name and col2_name and run_compare:
    # Normalize to distinct smartcard strings
    norm_sc1 = normalize_smartcards(df1[col1_name])
    norm_sc2 = normalize_smartcards(df2[col2_name])

    sc1 = set(norm_sc1)
    sc2 = set(norm_sc2)

    common = sorted(sc1.intersection(sc2))
    only_in_1 = sorted(sc1 - sc2)
    only_in_2 = sorted(sc2 - sc1)

    df_common = pd.DataFrame({"Smartcard Number": common})
    df_only1 = pd.DataFrame({"Smartcard Number": only_in_1})
    df_only2 = pd.DataFrame({"Smartcard Number": only_in_2})

    total1 = len(sc1)
    total2 = len(sc2)

    # ---------- Summary cards ----------
    st.markdown("### 📊 Summary")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Distinct in {file1_label}", total1)
    c2.metric(f"Distinct in {file2_label}", total2)
    c3.metric("In Both Files", len(common))
    c4.metric("Total Unique Across Both", len(sc1.union(sc2)))

    st.markdown(
        f"""
        <p style="color:#888; font-size:0.85rem;">
        Comparing <b>{col1_name}</b> from <b>{file1_label}</b> with
        <b>{col2_name}</b> from <b>{file2_label}</b>.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # ---------- Tabs for results ----------
    tab_both, tab_f1, tab_f2 = st.tabs(
        [f"✅ In Both ({file1_label} & {file2_label})",
         f"📁 Only in {file1_label}",
         f"📁 Only in {file2_label}"]
    )

    with tab_both:
        st.markdown("#### Smartcards in **both** files")
        st.dataframe(df_common, use_container_width=True, height=400)

        st.download_button(
            "⬇️ Download smartcards in both files (CSV)",
            data=df_common.to_csv(index=False),
            file_name="smartcards_in_both_files.csv",
            mime="text/csv",
        )

    with tab_f1:
        st.markdown(f"#### Smartcards **only** in {file1_label}")
        st.dataframe(df_only1, use_container_width=True, height=400)

        st.download_button(
            f"⬇️ Download smartcards only in {file1_label} (CSV)",
            data=df_only1.to_csv(index=False),
            file_name="smartcards_only_in_file1.csv",
            mime="text/csv",
        )

    with tab_f2:
        st.markdown(f"#### Smartcards **only** in {file2_label}")
        st.dataframe(df_only2, use_container_width=True, height=400)

        st.download_button(
            f"⬇️ Download smartcards only in {file2_label} (CSV)",
            data=df_only2.to_csv(index=False),
            file_name="smartcards_only_in_file2.csv",
            mime="text/csv",
        )

elif run_compare:
    st.warning("Please upload both files and select the smartcard columns in the sidebar.")

# ---------- Footer tag ----------
st.markdown(
    """
    <hr style="margin-top:2rem; margin-bottom:0.5rem;"/>
    <p style="text-align:center; color:#aaa; font-size:0.8rem;">
        Developed by <b>Tinashe Chinyati</b>
    </p>
    """,
    unsafe_allow_html=True,
)
