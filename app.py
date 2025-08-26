# ---------- Styled Job Board (Streamlit) ----------
import streamlit as st
import pandas as pd
import os
from uuid import uuid4

# ---------- Page setup
st.set_page_config(page_title="Job Board", page_icon="📋", layout="wide")

# ---------- Minimal CSS styling
st.markdown("""
<style>
/* page container */
.main .block-container {padding-top: 2rem; padding-bottom: 3rem;}
/* title */
h1, h2, h3, h4 { color:#2C3E50; }
/* cards */
.job-card {
  border:1px solid #e5e7eb; border-radius:14px; padding:16px; background:#ffffff;
  box-shadow: 0 8px 20px rgba(0,0,0,0.04); height: 100%;
}
.jd-btn {
  display:inline-block; padding:10px 14px; border-radius:10px; text-decoration:none;
  background:#3498db; color:#fff; font-weight:600;
}
.jd-btn:hover { background:#2d83bd; }
.small { color:#6b7280; font-size:0.9rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 📋 Job Roles & Descriptions")

# ---------- Storage
DATA_DIR = "uploaded_jds"     # where files are saved
CSV_PATH = "jobs.csv"         # where metadata is saved
os.makedirs(DATA_DIR, exist_ok=True)

# ---------- Load / init data
if "jobs_df" not in st.session_state:
    if os.path.exists(CSV_PATH):
        st.session_state.jobs_df = pd.read_csv(CSV_PATH)
    else:
        st.session_state.jobs_df = pd.DataFrame(
            columns=["role", "stored_filename", "original_filename"]
        )

def save_df():
    st.session_state.jobs_df.to_csv(CSV_PATH, index=False)

# ---------- Sidebar (search + quick stats)
with st.sidebar:
    st.header("🔎 Filter")
    q = st.text_input("Search by role").strip().lower()
    st.write("—")
    st.metric("Total roles", len(st.session_state.jobs_df))

# ---------- Add Job form
with st.form("job_form", clear_on_submit=True):
    c1, c2 = st.columns([2, 3])
    with c1:
        role = st.text_input("Job Role Name", placeholder="e.g., API Developer (WMS)")
    with c2:
        file = st.file_uploader("Upload Job Description (PDF/DOCX/TXT)", type=["pdf","docx","txt"])
    submitted = st.form_submit_button("➕ Add Job")
    if submitted:
        if not role:
            st.error("Please enter a Job Role name.")
        elif not file:
            st.error("Please upload a Job Description file.")
        else:
            # save file with unique name
            unique_name = f"{uuid4().hex}_{file.name}"
            save_path = os.path.join(DATA_DIR, unique_name)
            with open(save_path, "wb") as f:
                f.write(file.getbuffer())
            # update table
            new_row = {
                "role": role,
                "stored_filename": unique_name,
                "original_filename": file.name
            }
            st.session_state.jobs_df = pd.concat(
                [st.session_state.jobs_df, pd.DataFrame([new_row])],
                ignore_index=True
            )
            save_df()
            st.success(f"✅ '{role}' added.")

st.divider()

# ---------- Filter
df = st.session_state.jobs_df.copy()
if q:
    df = df[df["role"].str.lower().str.contains(q, na=False)]

# ---------- Empty state
if df.empty:
    st.info("No jobs to show. Add one using the form above.")
    st.stop()

# ---------- Cards layout (3 per row)
st.markdown("### 📑 Job List")
cards_per_row = 3
rows = range(0, len(df), cards_per_row)
for start in rows:
    cols = st.columns(cards_per_row)
    for i, col in enumerate(cols):
        idx = start + i
        if idx >= len(df): break
        row = df.iloc[idx]
        with col:
            st.markdown(
                f"""
                <div class="job-card">
                  <h4>{row['role']}</h4>
                  <div class="small">{row['original_filename']}</div>
                """,
                unsafe_allow_html=True
            )
            # download/view button
            filepath = os.path.join(DATA_DIR, row["stored_filename"])
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    st.download_button(
                        "📄 View Job Description",
                        data=f,
                        file_name=row["original_filename"],
                        key=f"dl_{idx}"
                    )
            else:
                st.warning("File missing on disk.")
            st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ---------- Admin: delete
with st.expander("🗑️ Admin: Delete a Job"):
    if not st.session_state.jobs_df.empty:
        options = [f"{i}: {r}" for i, r in enumerate(st.session_state.jobs_df["role"].tolist())]
        choice = st.selectbox("Select a job to delete", options) if options else None
        if st.button("Delete selected"):
            if choice:
                i = int(choice.split(":")[0])
                # remove file
                fname = st.session_state.jobs_df.iloc[i]["stored_filename"]
                fpath = os.path.join(DATA_DIR, fname)
                if os.path.exists(fpath):
                    try: os.remove(fpath)
                    except Exception: pass
                # remove row + save
                st.session_state.jobs_df = st.session_state.jobs_df.drop(index=i).reset_index(drop=True)
                save_df()
                st.success("Deleted.")
                st.rerun()
