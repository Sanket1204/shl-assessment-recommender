import io
import streamlit as st
import requests
from PyPDF2 import PdfReader

API_BASE = "http://api:8000"  # in Docker; locally use http://127.0.0.1:8000


def extract_text_from_file(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    if uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8", errors="ignore")
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    return ""


def main():
    st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")

    tab_main, tab_admin, tab_analytics = st.tabs(["Recommender", "Admin (view only)", "Analytics"])

    with tab_main:
        st.title("SHL Assessment Recommendation Engine")

        with st.form("recommendation_form"):
            col1, col2 = st.columns(2)

            with col1:
                job_title = st.text_input("Job Title", value="Customer Service Representative")
                job_family = st.selectbox(
                    "Job Family",
                    options=["customer_service", "retail", "sales", "it", "analytics", "operations", "leadership"],
                    index=0,
                )
                job_level = st.selectbox(
                    "Job Level",
                    options=["entry", "junior", "graduate", "professional", "manager", "executive"],
                    index=0,
                )
                use_case = st.selectbox(
                    "Use Case",
                    options=["selection", "development", "succession"],
                    index=0,
                )
                volume = st.selectbox(
                    "Hiring Volume",
                    options=["low", "medium", "high"],
                    index=2,
                )

            with col2:
                max_total_duration_min = st.slider(
                    "Max Total Assessment Duration (minutes)",
                    min_value=20, max_value=120, value=45, step=5
                )
                assessment_budget = st.selectbox(
                    "Assessment Budget Level",
                    options=["low", "medium", "high"],
                    index=1,
                )
                languages = st.multiselect(
                    "Languages",
                    options=["en", "fr", "de", "es"],
                    default=["en"],
                )
                unsupervised_ok = st.checkbox("Unsupervised Online OK?", value=True)

            st.markdown("### Upload JD / Resume (optional)")
            uploaded = st.file_uploader("Upload JD / resume (PDF/TXT)", type=["pdf", "txt"])
            extracted_text = extract_text_from_file(uploaded)

            job_description = st.text_area(
                "Job Description / Key Responsibilities",
                height=150,
                value=extracted_text or "Handle customer queries via phone and email..."
            )

            st.markdown("### Target Constructs")
            col3, col4 = st.columns(2)
            with col3:
                must_have_constructs = st.multiselect(
                    "Must-have constructs",
                    options=["cognitive_ability", "behavioral_fit", "personality", "motivation"],
                    default=["cognitive_ability", "behavioral_fit"],
                )
            with col4:
                nice_to_have_constructs = st.multiselect(
                    "Nice-to-have constructs",
                    options=["cognitive_ability", "behavioral_fit", "personality", "motivation"],
                    default=["personality"],
                )

            submitted = st.form_submit_button("Get Recommendations")

        if submitted:
            payload = {
                "job_title": job_title,
                "job_description": job_description,
                "job_family": job_family,
                "job_level": job_level,
                "use_case": use_case,
                "volume": volume,
                "assessment_budget": assessment_budget,
                "max_total_duration_min": max_total_duration_min,
                "must_have_constructs": must_have_constructs,
                "nice_to_have_constructs": nice_to_have_constructs,
                "languages": languages,
                "unsupervised_ok": unsupervised_ok,
            }
            with st.spinner("Contacting recommendation engine..."):
                r = requests.post(f"{API_BASE}/recommend", json=payload)
                if r.status_code != 200:
                    st.error(f"API error: {r.status_code} - {r.text}")
                    return
                data = r.json()

            st.subheader("Recommended Assessment Bundle")
            st.write(f"**Bundle ID:** `{data['bundle_id']}`")
            st.write(f"**Total Duration:** {data['total_duration_min']} minutes")
            st.write(f"**Constructs Covered:** {', '.join(data['constructs_covered']) or 'None'}")

            for p in data["products"]:
                with st.expander(f"{p['name']} ({p['product_id']}) – {p['max_duration_min']} min"):
                    st.write(p["reason"])

            if st.button("Download as PDF"):
                pdf_resp = requests.post(f"{API_BASE}/recommend/pdf", json=payload)
                if pdf_resp.status_code == 200:
                    st.download_button(
                        "Download PDF",
                        data=pdf_resp.content,
                        file_name="assessment_recommendation.pdf",
                        mime="application/pdf",
                    )
                else:
                    st.error("Failed to generate PDF")

    with tab_admin:
        st.header("Admin – Products (read-only demo)")
        try:
            r = requests.get(f"{API_BASE}/admin/products")
            if r.status_code == 200:
                products = r.json()
                for p in products:
                    with st.expander(f"{p['name']} ({p['product_id']})"):
                        st.json(p)
            else:
                st.error("Failed to load products")
        except Exception as e:
            st.error(f"Error: {e}")

    with tab_analytics:
        st.header("Analytics")
        try:
            r = requests.get(f"{API_BASE}/admin/analytics")
            if r.status_code == 200:
                data = r.json()
                st.write(f"Total recommendation requests: **{data['total_requests']}**")
                st.write("By Job Family:")
                st.json(data["by_job_family"])
            else:
                st.error("Failed to load analytics")
        except Exception as e:
            st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
