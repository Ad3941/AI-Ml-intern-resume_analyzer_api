import streamlit as st
import requests

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="centered")

st.title("📄 AI Resume Analyzer & Text Utility")
st.write("Upload a candidate resume (PDF) to instantly extract summaries, contact details, skills, and recommended roles using FastAPI & Groq.")

API_URL = "http://127.0.0.1:8000"

uploaded_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

if uploaded_file is not None:
    if st.button("Run Comprehensive Analysis", type="primary"):
        with st.spinner("Processing resume through FastAPI backend..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            try:
                response = requests.post(f"{API_URL}/api/v1/analyze-resume", files=files)
                if response.status_code == 200:
                    data = response.json()
                    st.success("Analysis Complete!")
                    
                    # Contact Details Section
                    contacts = data.get("contact_details", {})
                    st.subheader("👤 Candidate Contact Info")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Name:** {contacts.get('full_name', 'N/A')}")
                        st.markdown(f"**Email:** {contacts.get('email', 'N/A')}")
                    with col2:
                        st.markdown(f"**Phone:** {contacts.get('phone_number', 'N/A')}")
                        st.markdown(f"**LinkedIn:** {contacts.get('linkedin_url', 'N/A')}")
                    
                    st.divider()
                        # Summary & Experience
                    st.subheader("📌 Professional Summary")
                    st.write(data.get("summary"))
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        # Fixed metric display
                        exp = data.get('experience_years_estimated', 0)
                        st.metric("Estimated Experience", f"{exp if exp else 'N/A'} Years")
                    with col4:
                        st.subheader("⏳ Recommended Roles")
                        st.write(", ".join(data.get("recommended_roles", [])))

                    # Skills (Replaced st.pills with standard markdown/tags to prevent JS import errors)
                    st.subheader("🛠 Key Skills")
                    skills = data.get("key_skills", [])
                    skills_markdown = " ".join([f"`{skill}`" for skill in skills])
                    st.markdown(skills_markdown)
                    
                    # # Summary & Experience
                    # st.subheader("📌 Professional Summary")
                    # st.write(data.get("summary"))
                    
                    # col3, col4 = st.columns(2)
                    # with col3:
                    #     st.metric("Estimated Experience", f"{data.get('experience_years_estimated', 0)} Years")
                    # with col4:
                    #     st.subheader("⏳ Recommended Roles")
                    #     st.write(", ".join(data.get("recommended_roles", [])))

                    # # Skills
                    # st.subheader("🛠 Key Skills")
                    # st.pills("Skills", data.get("key_skills", []))

                else:
                    st.error(f"Error from server: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Could not connect to FastAPI backend at {API_URL}. Is Uvicorn running? Error: {e}")