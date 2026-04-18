import streamlit as st
import base64
from snowflake.snowpark.context import get_active_session

session = get_active_session()

STAGE_PATH = "@BIO_HACK.LAB_DATA.NOTEBOOK_IMAGES"

st.markdown("""
    <style>
    .stApp {
        background-color: #F0FFF4;
    }
    h1, h2, h3 {
        color: #1E293B;
        font-weight: 700;
    }
    [data-testid="stMetricValue"] {
        color: #16A34A;
    }
    [data-testid="stSidebar"] {
        background-color: #BBF7D0;
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: #14532D;
    }
    div.stButton > button {
        border-radius: 8px;
        background-color: #86EFAC;
        color: #14532D;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #4ADE80;
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.header("Configuration")
    user_mode = st.radio(
        "Select Target Audience:",
        ["Primary School (Ages 5-11)", "University / Professional"],
        help="Adjusts the AI explanation complexity."
    )
    st.divider()
    st.info("Built for MLH Hackfest 2026 using Snowflake Cortex Multimodal AI.")


try:
    st.image("bioscribe_logo.png", width=400)
except Exception:
    st.title("BioScribe: The Intelligent Lab Companion")

st.write("Bridging physical lab notes with the Snowflake Data Cloud.")

tab1, tab2, tab3 = st.tabs(["Digital Microscope", "Tutor Review", "Lab Ledger"])

with tab1:
    st.header("Real-time Specimen Analysis")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Capture Lab Notes")
        img = st.file_uploader("Upload a photo of your notebook or specimen", type=["png", "jpg", "jpeg"])

    if img:
        file_name = img.name

        with st.spinner("Uploading to Snowflake Stage..."):
            session.file.put_stream(img, f"{STAGE_PATH}/{file_name}", overwrite=True, auto_compress=False)

        if user_mode == "Primary School (Ages 5-11)":
            prompt_logic = "Explain this like a fun science teacher. Use analogies, emojis, and simple language. Focus on the Why behind the science."
        else:
            prompt_logic = "Provide a technical analysis. Convert handwritten notes to Markdown, identify molecular motifs, and cite enzyme EC numbers where applicable."

        full_prompt = f"You are an expert Biochemist and Educator. {prompt_logic} If you see any safety hazards, highlight them in a SAFETY ALERT section. Structure your output with clear headers."

        with st.spinner("AI is analyzing biochemistry..."):
            try:
                analysis_result = session.sql(f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE(
                        'claude-3-7-sonnet',
                        $${full_prompt}$$,
                        TO_FILE('{STAGE_PATH}', '{file_name}')
                    )
                """).collect()[0][0]

                st.session_state["analysis_result"] = analysis_result
                st.session_state["file_name"] = file_name

                with col2:
                    st.subheader("AI Insights")
                    st.markdown(analysis_result)

                    btn_col1, btn_col2, btn_col3 = st.columns(3)

                    with btn_col1:
                        if st.button("Save to Lab Ledger", use_container_width=True):
                            session.sql(f"""
                                INSERT INTO BIO_HACK.LAB_DATA.LAB_LEDGER (file_name, analysis)
                                VALUES ('{file_name}', $${analysis_result}$$)
                            """).collect()
                            st.success("Analysis saved to Snowflake database!")

                    with btn_col2:
                        st.download_button(
                            "Export Lab Report",
                            data=analysis_result,
                            file_name="lab_report.md",
                            mime="text/markdown",
                            use_container_width=True
                        )

                    with btn_col3:
                        if st.button("Send to Tutor Review", use_container_width=True):
                            st.info("Switch to the Tutor Review tab to verify accuracy.")

                if "SN2" in analysis_result or "sn2" in analysis_result.lower():
                    st.info("SN2 mechanism detected. Remember: SN2 involves a concerted backside attack with no intermediate.")
                if "E2" in analysis_result or "e2" in analysis_result.lower():
                    st.info("E2 mechanism detected. Remember: E2 is concerted -- no carbocation intermediate forms.")

            except Exception as e:
                st.error(f"Cortex Vision Error: {e}")

with tab2:
    st.header("Mechanistic Verification")
    st.write("Run a second AI pass to fact-check your lab notes against established biochemistry standards.")

    if "analysis_result" in st.session_state:
        st.subheader("Notes Under Review")
        st.markdown(st.session_state["analysis_result"][:500] + "..." if len(st.session_state.get("analysis_result", "")) > 500 else st.session_state.get("analysis_result", ""))

        if st.button("Verify Accuracy", use_container_width=True):
            with st.spinner("Professor is reviewing for errors..."):
                stored_analysis = st.session_state["analysis_result"]
                validation_prompt = f"""You are a Senior Chemistry Professor. Review the following extracted lab notes for mechanistic accuracy.
Pay specific attention to:
1. Reaction Mechanisms (SN2 vs E2): Ensure concerted reactions are not described with intermediates.
2. Intermediate Logic: Flag any mentions of carbocations in primary haloalkane reactions. If the user mentions a carbocation for a primary haloalkane, always flag it as a Level 1 error. Primary carbocations are too unstable to form in these conditions.
3. Stereochemistry/Sterics: Ensure the reasoning for backside attack is correct.
4. Enzyme Classifications: Verify EC numbers if mentioned.
5. Safety Claims: Cross-check any safety statements.

Notes to review:
{stored_analysis}

Output Format:
- Accuracy Score (0-100)
- What is Correct
- Critical Errors
- The Proper Mechanism
- Educational Tip: If an error is found, explain the correct concept using a simple analogy."""

                critique = session.sql(f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE(
                        'claude-3-7-sonnet',
                        $${validation_prompt}$$
                    )
                """).collect()[0][0]

                st.warning("Professor's Feedback")
                st.markdown(critique)

                st.subheader("Detected Parameters")
                m1, m2, m3 = st.columns(3)
                if "SN2" in stored_analysis or "sn2" in stored_analysis.lower():
                    m3.metric("Mechanism", "Concerted (SN2)")
                elif "E2" in stored_analysis or "e2" in stored_analysis.lower():
                    m3.metric("Mechanism", "Concerted (E2)")
                else:
                    m3.metric("Mechanism", "See analysis")
                m1.metric("Review Status", "Complete")
                m2.metric("AI Model", "Claude 3.7")
    else:
        st.write("Upload and analyze an image in the Digital Microscope tab first.")

with tab3:
    st.header("Stored Research")
    try:
        history = session.sql("""
            SELECT created_at, file_name, analysis
            FROM BIO_HACK.LAB_DATA.LAB_LEDGER
            ORDER BY created_at DESC
            LIMIT 5
        """).collect()

        if history:
            for row in history:
                with st.expander(f"Entry: {row['FILE_NAME']} - {row['CREATED_AT']}"):
                    st.write(row['ANALYSIS'])
        else:
            st.write("No entries in the ledger yet. Start by scanning a document!")
    except Exception as e:
        st.write("Ledger history is ready for your first entry.")
