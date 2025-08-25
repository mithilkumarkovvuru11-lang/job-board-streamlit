
# Simple Job Board (Streamlit)

A lightweight web app to store **Job Roles** with an uploaded **Job Description** file (PDF/DOCX/TXT).
- Add a job role + attach JD
- Search by role
- View/download JD
- Persistent storage using `jobs.csv` and `uploaded_jds/` folder
- Optional delete from the "Admin" expander

## Local Setup

1. Install Python 3.10+
2. (Recommended) Create a virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run:
   ```bash
   streamlit run app.py
   ```

## Deploy to Streamlit Community Cloud

1. Push these files to a GitHub repo.
2. Go to https://share.streamlit.io/ and connect the repo.
3. Set the entry point to `app.py` and deploy.

⚠️ Note: On Streamlit Cloud, local disk storage is ephemeral. For long-term file storage, connect S3/Drive or use
a database + object storage.
