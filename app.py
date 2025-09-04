# app.py
# -*- coding: utf-8 -*-
"""
A Streamlit web application for generating ER physician notes using the Gemini API.
"""
import os
import google.generativeai as genai
import streamlit as st

# --- Core Logic Functions (from our previous script) ---

def setup_api_key():
    """Retrieves and configures the Gemini API key from Streamlit secrets."""
    try:
        # For local development, use environment variables.
        # For deployment, use Streamlit's st.secrets.
        api_key = os.environ.get("GEMINI_API_KEY") or st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return True
    except (KeyError, AttributeError):
        return False

def generate_er_note(text_content):
    """Sends text content to the Gemini API and returns the note."""
    if not text_content or not text_content.strip():
        return "⚠️ Error: Input text cannot be empty."

    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"""
    Use the information in the document provided below to draft an ER physician note with the following structure. Fill in the placeholders (e.g., @DEPTNME@, @ED@) with the relevant information from the document. If information for a specific field is not available in the document, write "Not Available". As part of the summary narrative, include a focused differential for the presenting complaint, and exclude all but the final diagnosis implied by the note, and provide a rationale for finding the other diagnoses to be unlikely. Use CDRs where available. Suppress the patient's name from the note as well as their address. The only PHI should be their DOB and MRN.

    **Document Content:**
    ---
    {text_content}
    ---

    **ER Note Template:**
    @DEPTNME@ DEPARTMENT ENCOUNTER NOTE

    Date of Visit:       @ED@ (dd/mm/yyyy)
    Location:            @DEPTNME@

    MRN:         @MRN@
    Birth Date & Age:    @BDAY@ | @AGEPEDS@

    Primary Concern:     @CHIEFCOMPLAINTNNOLINE@

    Appropriate PPE donned and doffed with serial handwashing in accordance with hospital policies.
    Additional notes may appear in the written record.

    Identified myself to the patient, requested use of my preferred pronouns, and showed the patient my badge indicating name and pronouns.

    Triage note, nursing note, past medical history and medications reviewed.

    IDENTIFICATION
    @AGE@ year old individual. Preferred pronouns asked and used as applicable.

    FOCUSED PAST MEDICAL HISTORY
    @PMH@ @PSH@ @PROB@

    FOCUSED MEDICATIONS & ALLERGIES
    @HOMEMEDS@
    @CERMSG(160084265:16010)@@ALLERGYNOHEADER@

    NOTE
    @EDCOURSE@

    Refer to ED Course (above) for subsequent assessments and impressions.

    @MDNAME@
    Emergency Medicine Physician

    Note: This ED Encounter Note was completed using voice recognition software. It may not have been proofread and there may be errors related to sound-alike phrases and homonyms. Pronoun errors, if present, are unintentional. Verbal consent obtained for any photos included in record. To request error correction contact UHN Health Records.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.replace("```", "").strip()
    except Exception as e:
        return f"❌ An error occurred with the API: {e}"

# --- Streamlit App UI ---

# Set the title and a descriptive header for the app
st.set_page_config(page_title="ER Note Generator", layout="centered")
st.title("ER Physician Note Generator 🩺")

# Check for API key and display a warning if not found
if not setup_api_key():
    st.error("GEMINI_API_KEY is not set. Please set it as an environment variable or a Streamlit secret.")
else:
    # Create the text area for user input
    source_text = st.text_area(
        "Paste the raw patient information below:",
        height=250,
        placeholder="e.g., Triage note, nursing note, labs, etc."
    )

    # Create the button to trigger the generation
    if st.button("Generate Note", type="primary"):
        # Show a spinner while the API call is in progress
        with st.spinner("🧠 Calling the Gemini API... please wait."):
            generated_note = generate_er_note(source_text)
            
            # Display the result
            st.subheader("Generated ER Note:")
            st.markdown(generated_note) # Using markdown for better formatting
