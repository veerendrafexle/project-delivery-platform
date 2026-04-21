# AI Delivery Platform

A scaffold for an AI delivery and project documentation platform.

## Project structure

- `app/` — Main application logic and services.
  - `ingestion.py` — Load input files.
  - `ai_engine.py` — AI calls for Ollama/OpenRouter.
  - `structuring.py` — Convert raw input to structured JSON.
  - `validation.py` — Quality and rule validation.
  - `generation.py` — BRD / URS generation.
  - `governance.py` — Phase and approval logic.
  - `traceability.py` — Link artifacts end-to-end.
  - `rag.py` — Chroma vector DB and retrieval logic.
  - `salesforce_mapper.py` — Requirement to Salesforce mapping.
  - `task_generator.py` — Jira/task generation.
- `data/` — Stored structured data, generated datasets, or serialized models.
  - `project.json` — Project state and governance.
  - `structured.json` — Extracted structured data.
  - `traceability.json` — Mapping graph.
- `inputs/` — Raw discovery files, requirements, and user input documents.
  - `transcript.txt` — Sample discovery transcript.
  - `sow.txt` — Statement of work.
  - `painpoints.txt` — Pain points.
  - `flows.txt` — Current flows.
- `outputs/` — Generated documents, reports, and exported artifacts.
  - `BRD.pdf` — Generated Business Requirements Document.
  - `URS.pdf` — Generated User Requirements Specification.
- `templates/` — BRD, URS, and other document templates.
- `workflows/` — Orchestration configs, workflows, and automation definitions.
- `ui/` — Streamlit UI components.
- `utils/` — Shared helper functions and common utilities.
- `config/` — Configuration files and environment settings.
- `logs/` — Runtime logs and diagnostic output.

## Quick start

### Prerequisites
- Python 3.8+
- pip package manager

### Setup
1. Clone or copy the project directory.

2. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment (optional):
   - Copy `.env.example` to `.env`
   - Add your API keys if using remote AI

### Run the pipeline
```bash
python main.py
```
This will:
- Load sample inputs from `inputs/`
- Extract structured requirements using AI
- Generate `outputs/BRD.pdf`

### Run the UI
```bash
streamlit run ui/app.py
```
Open the provided URL in your browser for the web interface.

## AI configuration

- **Local AI**: Uses Ollama (default `http://localhost:11434/api/generate`)
- **Remote AI**: Supports OpenRouter API
- **Fallback**: Built-in development fallback for testing without AI

Set in `.env` or environment variables:
- `OPENROUTER_API_KEY` — Your OpenRouter API key
- `OPENROUTER_API_URL` — API endpoint (usually `https://api.openrouter.ai/v1/chat/completions`)
- `LOCAL_LLM_URL` — Local Ollama URL
- `MODEL` — Model name (default: `mistral`)

## What this scaffold includes

- ✅ Input ingestion from text files
- ✅ AI-powered requirement extraction
- ✅ Document generation (PDF)
- ✅ Validation and governance logic
- ✅ Traceability mapping
- ✅ Task generation for Jira
- ✅ Web UI with Streamlit
- ✅ Configuration management
- ✅ Extensible architecture for Salesforce, RAG, etc.

## Development notes

- Sample data is provided in `inputs/` and `data/`
- The pipeline uses a development fallback if no AI is configured
- Outputs are generated in `outputs/`
- Logs can be written to `logs/`

## Extending the platform

- Add new input formats in `app/ingestion.py`
- Integrate Salesforce in `app/salesforce_mapper.py`
- Add RAG with Chroma in `app/rag.py`
- Connect Jira in `app/task_generator.py`
- Add n8n workflows in `workflows/`

The scaffold is production-ready and follows best practices for maintainability and extensibility.
