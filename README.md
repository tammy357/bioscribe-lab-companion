# BioScribe: The Intelligent Lab Companion

## What it does
BioScribe transforms handwritten lab notes into structured digital data using AI vision. It features:

- **Digital Microscope** — Upload lab notebook photos for AI-powered biochemistry analysis
- **Tutor Review** — Second-pass AI verification checking reaction mechanisms (SN2/E2), enzyme classifications and safety
- **Lab Ledger** — Persistent storage in Snowflake Data Cloud with export capability

## Tech Stack
- Snowflake Cortex AI (claude-3-7-sonnet multimodal)
- Streamlit in Snowflake
- Snowflake Stages (image storage)
- Snowflake Tables (structured data persistence)

## Setup
1. Create database, schema, stage, and table:
```sql
CREATE DATABASE BIO_HACK;
CREATE SCHEMA BIO_HACK.LAB_DATA;
CREATE STAGE BIO_HACK.LAB_DATA.NOTEBOOK_IMAGES ENCRYPTION=(TYPE='SNOWFLAKE_SSE') DIRECTORY=(ENABLE=TRUE);
CREATE TABLE BIO_HACK.LAB_DATA.LAB_LEDGER (file_name STRING, analysis STRING, created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP());
