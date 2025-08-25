
import streamlit as st
import pandas as pd
import os
from uuid import uuid4

st.set_page_config(page_title="Job Board", layout="wide")
st.title("📋 Job Roles & Descriptions")

# ---- Storage locations
DATA_DIR = "uploaded_jds"
CSV_PATH = "jobs.csv"
os.makedirs(DATA_DIR, exist_ok=True)

# ---- Load existing data
if "jobs_df" not in st.session_state:
    if os.path.exists(CSV_PATH):
        st.session_state.jobs_df = pd.read_csv(CSV_PATH)
    else:
        st.session_state.jobs_df = pd.DataFrame(columns=["role", "stored_filename", "original_filename"])

def save_df():
    st.session_state.jobs_df.to_csv(CSV_PATH, index=False)

# ---- Add new job form
with st.form("job_form", clear_on_submit=True):
    role = st.text_input("Job Role Name", placeholder="e.g., API Developer (WMS)")
    file = st.file_uploader("Upload Job Description (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
    submitted = st.form_submit_button("➕ Add Job")
    if submitted:
        if not role:
            st.error("Please enter a Job Role name.")
        elif file is None:
            st.error("Please upload a Job Description file.")
        else:
            # Store file with a unique name to avoid collisions
            unique_name = f"{uuid4().hex}_{file.name}"
            save_path = os.path.join(DATA_DIR, unique_name)
            with open(save_path, "wb") as f:
                f.write(file.getbuffer())
            # Update DataFrame
            new_row = {"role": role, "stored_filename": unique_name, "original_filename": file.name}
            st.session_state.jobs_df = pd.concat([st.session_state.jobs_df, pd.DataFrame([new_row])], ignore_index=True)
            save_df()
            st.success(f"✅ '{role}' added.")

st.divider()

# ---- Search box
q = st.text_input("Search by Job Role", placeholder="Type to filter...").strip().lower()
df = st.session_state.jobs_df.copy()
if q:
    df = df[df["role"].str.lower().str.contains(q, na=False)]

if df.empty:
    st.info("No jobs yet. Add one using the form above.")
    st.stop()

# ---- Display table-like list with download buttons
st.markdown("### Job List")
for i, row in df.reset_index(drop=True).iterrows():
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"**{row['role']}**")
        st.caption(row['original_filename'])
    with c2:
        filepath = os.path.join(DATA_DIR, row["stored_filename"])
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                st.download_button("📄 View Job Description", data=f, file_name=row["original_filename"], key=f"dl_{i}")
        else:
            st.error("File missing on disk.")

st.divider()

# ---- (Optional) Admin: delete entries
with st.expander("🗑️ Admin: Delete a Job Entry"):
    if not st.session_state.jobs_df.empty:
        options = [f"{idx}: {r}" for idx, r in enumerate(st.session_state.jobs_df["role"].tolist())]
        choice = st.selectbox("Select a job to delete", options) if options else None
        if st.button("Delete Selected"):
            if choice:
                idx = int(choice.split(":")[0])
                # Delete file from disk
                fname = st.session_state.jobs_df.iloc[idx]["stored_filename"]
                fpath = os.path.join(DATA_DIR, fname)
                if os.path.exists(fpath):
                    try:
                        os.remove(fpath)
                    except Exception:
                        pass
                # Remove from dataframe and save
                st.session_state.jobs_df = st.session_state.jobs_df.drop(index=idx).reset_index(drop=True)
                save_df()
                st.success("Deleted.")
                st.rerun()
