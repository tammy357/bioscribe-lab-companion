# BioScribe: The Intelligent Lab Companion

## What it does
BioScribe transforms handwritten lab notes into structured digital data using AI vision. It features:

- **Digital Microscope** — Upload lab notebook photos for AI-powered biochemistry analysis
- **Tutor Review** — Second-pass AI verification checking reaction mechanisms (SN2/E2), enzyme classifications and safety
- **Lab Ledger** — Persistent storage in Snowflake Data Cloud with export capability

## Tech Stack

- AI Engine: Snowflake Cortex AI API (claude-4-6-sonnet)

- Data Orchestration: Snowpark Python API

- Frontend: Streamlit in Snowflake

- Storage: Snowflake Stages (Files API) & Snowflake Tables

- Languages: Python, SQL

##  Setup Instructions

### Prerequisites

- A Snowflake account ([free trial](https://signup.snowflake.com/) works)
- `ACCOUNTADMIN` or `SYSADMIN` role

### Step 1: Create Snowflake Objects

Run these SQL commands in a Snowflake worksheet:

```sql
-- Create database and schema
CREATE DATABASE IF NOT EXISTS BIO_HACK;
CREATE SCHEMA IF NOT EXISTS BIO_HACK.LAB_DATA;

-- Create stage for image storage
CREATE OR REPLACE STAGE BIO_HACK.LAB_DATA.NOTEBOOK_IMAGES
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
  DIRECTORY = (ENABLE = TRUE);

-- Create table for saving analysis results
CREATE TABLE IF NOT EXISTS BIO_HACK.LAB_DATA.LAB_LEDGER (
    file_name STRING,
    analysis STRING,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- 1. Set your current role context (usually ACCOUNTADMIN or SYSADMIN for setup)
SET MY_USER_ROLE = CURRENT_ROLE();

-- 2. Grant usage on the hierarchy so the app can see the folders
GRANT USAGE ON DATABASE BIO_HACK TO ROLE identifier($MY_USER_ROLE);
GRANT USAGE ON SCHEMA BIO_HACK.LAB_DATA TO ROLE identifier($MY_USER_ROLE);

-- 3. Grant full access to the data objects
GRANT ALL PRIVILEGES ON TABLE BIO_HACK.LAB_DATA.LAB_LEDGER TO ROLE identifier($MY_USER_ROLE);
GRANT ALL PRIVILEGES ON STAGE BIO_HACK.LAB_DATA.NOTEBOOK_IMAGES TO ROLE identifier($MY_USER_ROLE);

-- 4. THE MOST IMPORTANT PART: Grant access to Snowflake Cortex AI
-- Without this claude-4-6-sonnet will not respond.
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE identifier($MY_USER_ROLE);

```

### Step 2: Create the Streamlit App

1. In Snowsight, go to **Projects** > **Streamlit**
2. Click **+ Streamlit App**
3. Configure:
   - **App name**: `BioScribe`
   - **Database**: `BIO_HACK`
   - **Schema**: `LAB_DATA`
   - **Warehouse**: `COMPUTE_WH` (or any active warehouse)
4. Click **Create**

### Step 3: Add the Code

1. In the Streamlit editor, select all default code (`Ctrl+A`) and delete it
2. Copy the contents of `streamlit_app.py` from this repo and paste it in
3. Ensure you click the "Packages" button in the Streamlit editor and verify that snowflake-snowpark-python is selected. If you are using any additional libraries (like pandas or pillow), add them there as well.

### Step 4: Upload the Logo

1. In the left file panel of the Streamlit editor, click the **+** or upload icon
2. Upload `bioscribe_logo.png` from this repo

### Step 5: Run

The app auto-runs after pasting the code. You should see:
- The BioScribe logo at the top
- Three tabs: **Digital Microscope**, **Tutor Review**, **Lab Ledger**
- A file uploader to analyze lab notebook photos

---

## 📖 How to Use

1. **Digital Microscope tab** — Upload a photo of handwritten lab notes or biochemistry diagrams
2. The AI analyzes the image and returns structured insights
3. Click **Save to Lab Ledger** to store results in Snowflake
4. Click **Export Lab Report** to download as Markdown
5. **Tutor Review tab** — Click **Verify Accuracy** to run a second AI pass that checks for mechanistic errors (SN2/E2, carbocation logic, etc.)
6. **Lab Ledger tab** — View your saved analysis history

---

## 📁 Repository Structure

```
bioscribe-lab-companion/
├── README.md              # This file
├── streamlit_app.py       # Main Streamlit application
└── bioscribe_logo.png     # App logo
```

---
