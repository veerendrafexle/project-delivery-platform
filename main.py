"""Entry point for the AI Delivery Platform."""
from app.ingestion import load_project_files
from app.structuring import extract_structure
from app.generation import generate_brd
from app.validation import validate_brd


def run() -> None:
    files = load_project_files("inputs/")
    raw_text = "\n".join(files.values())

    structured = extract_structure(raw_text)
    issues = validate_brd(structured)

    if issues:
        print("Validation issues found:")
        for issue in issues:
            print(f"- {issue}")
    else:
        generate_brd(structured, "outputs/BRD.txt")
        print("BRD generated at outputs/BRD.txt")
        print("You can also generate URS with app.generation.generate_urs()")


if __name__ == "__main__":
    run()
