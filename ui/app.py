import streamlit as st

from app.ingestion import load_project_files
from app.structuring import extract_structure
from app.generation import generate_brd
from app.task_generator import generate_tasks
from app.validation import validate_brd

st.title("AI Delivery Platform")

if st.button("Generate BRD"):
    files = load_project_files("inputs/")
    raw_text = "\n".join(files.values())
    structured = extract_structure(raw_text)
    issues = validate_brd(structured)

    if issues:
        st.error("Validation issues detected")
        for issue in issues:
            st.write(f"- {issue}")
    else:
        generate_brd(structured, "outputs/BRD.txt")
        st.success("BRD generated to outputs/BRD.txt")
        st.subheader("Extracted structure")
        st.json(structured)

        st.subheader("Suggested tasks")
        st.json(generate_tasks(structured))
