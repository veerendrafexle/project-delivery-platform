"""Entry point for the AI Delivery Platform."""
import time
from pathlib import Path

from app.figma_integration import generate_ui_screens, save_ui_screens, validate_ui_screens
from app.ingestion import load_project_files
from app.logging_config import logger, log_pipeline_step, LoggedOperation, handle_exceptions
from app.rag import build_vector_store, query_vector_store
from app.salesforce_mapper import map_requirements_to_salesforce
from app.structuring import extract_structure
from app.task_generator import generate_user_stories, save_task_backlog
from app.generation import build_brd_content
from app.validation import validate_brd
from app.traceability import save_traceability_graph
from app.versioning import save_versioned_json, save_versioned_text


@handle_exceptions()
def run() -> None:
    """Main pipeline execution with comprehensive logging."""
    start_time = time.time()
    logger.info("Starting AI Delivery Platform pipeline")

    try:
        # Load project files
        with LoggedOperation("File Ingestion"):
            files = load_project_files("inputs/")
            raw_text = "\n".join(files.values())
            logger.info(f"Loaded {len(files)} input files")

        # Build RAG store
        with LoggedOperation("RAG Store Building"):
            build_vector_store(Path("inputs"), persist_directory=Path("rag_store"))
            logger.info("RAG vector store built successfully")

        # Query RAG for context
        with LoggedOperation("RAG Query"):
            query_response = query_vector_store(
                "Find the most relevant context for extracting business goals, pain points, requirements, current state, and future state.",
                top_n=3,
                persist_directory=Path("rag_store"),
            )
            context_chunks = [item["text"] for item in query_response]
            logger.info(f"Retrieved {len(context_chunks)} context chunks from RAG")

        # Extract structured data
        with LoggedOperation("Requirements Structuring"):
            structured = extract_structure(raw_text, context_chunks=context_chunks)
            logger.info("Requirements structured successfully")

        # Validate structured data
        with LoggedOperation("Data Validation"):
            issues = validate_brd(structured)
            if issues:
                logger.warning(f"Validation issues found: {len(issues)} issues")
                for issue in issues:
                    logger.warning(f"- {issue}")
                return

        # Version and save structured data
        data_output_dir = Path("data")
        data_history = data_output_dir / "history.json"
        with LoggedOperation("Structured Data Versioning"):
            structured_path = save_versioned_json(
                base_name="structured_data",
                data=structured,
                output_dir=data_output_dir,
                extension=".json",
                history_path=data_history,
                metadata={"source": "ai_extraction"},
            )
            logger.info(f"Structured data saved to {structured_path}")

        # Generate BRD
        brd_output_dir = Path("outputs")
        brd_history = brd_output_dir / "history.json"
        with LoggedOperation("BRD Generation"):
            brd_content = build_brd_content(structured)
            brd_path = save_versioned_text(
                base_name="BRD",
                content=brd_content,
                output_dir=brd_output_dir,
                extension=".txt",
                history_path=brd_history,
                metadata={"structured_data_path": str(structured_path)},
            )
            logger.info(f"BRD generated at {brd_path}")

        # Generate traceability
        with LoggedOperation("Traceability Generation"):
            trace_path = save_traceability_graph(
                source_texts=files,
                structured_data=structured,
                output_path=Path("data/traceability.json"),
                brd_name="BRD",
                brd_version=str(brd_path.stem.split("_v")[-1]),
            )
            logger.info(f"Traceability graph saved to {trace_path}")

        # Generate UI screens
        with LoggedOperation("UI Screen Generation"):
            ui_screens = generate_ui_screens(
                requirements=structured.get("requirements", []),
                pain_points=structured.get("pain_points", []),
                context_chunks=context_chunks,
            )

            ui_issues = validate_ui_screens(ui_screens)
            if ui_issues:
                logger.warning(f"UI generation issues: {len(ui_issues)} issues")
                for issue in ui_issues:
                    logger.warning(f"- {issue}")
            else:
                ui_path = save_ui_screens(ui_screens, Path("outputs/ui_screens.json"))
                logger.info(f"UI screens saved to {ui_path}")

        # Generate Salesforce mapping
        with LoggedOperation("Salesforce Mapping"):
            salesforce_mapping = map_requirements_to_salesforce(
                requirements=structured.get("requirements", []),
                pain_points=structured.get("pain_points", []),
                context_chunks=context_chunks,
            )
            sf_path = save_versioned_json(
                base_name="salesforce_mapping",
                data=salesforce_mapping,
                output_dir=data_output_dir,
                extension=".json",
                history_path=data_history,
                metadata={"source": "ai_mapping", "structured_data_path": str(structured_path)},
            )
            logger.info(f"Salesforce mapping saved to {sf_path}")

        # Generate task backlog
        with LoggedOperation("Task Backlog Generation"):
            user_stories = generate_user_stories(
                requirements=structured.get("requirements", []),
                pain_points=structured.get("pain_points", []),
                context_chunks=context_chunks,
            )

            if user_stories:
                backlog_path = save_task_backlog(user_stories, "outputs/task_backlog.json")
                logger.info(f"Task backlog saved to {backlog_path} with {len(user_stories)} user stories")
            else:
                logger.warning("No user stories generated")

        # Log completion
        total_duration = time.time() - start_time
        log_pipeline_step("Full Pipeline", True, total_duration)
        logger.info(f"Pipeline completed successfully in {total_duration:.2f} seconds")

        print(f"Structured data saved to {structured_path}")
        print(f"BRD generated at {brd_path}")
        print(f"Traceability graph saved to {trace_path}")
        print(f"Salesforce mapping saved to {sf_path}")
        print(f"Version history stored in {brd_history}")

    except Exception as e:
        total_duration = time.time() - start_time
        log_pipeline_step("Full Pipeline", False, total_duration, str(e))
        logger.error(f"Pipeline failed after {total_duration:.2f} seconds: {e}")
        raise


if __name__ == "__main__":
    run()
