# Autonomous AI Data Analysis Agent

An intelligent, autonomous full-stack agent built with Python, Streamlit, Gemini API, ChromaDB, and Scikit-Learn that allows you to chat with your data, run machine learning models, and generate dynamic visualizations.

## Architecture

- **Frontend:** Streamlit with custom glassmorphic CSS
- **Orchestrator:** `app.py` coordinates data ingestion and chat flow.
- **LLM Engine:** `src/agent/llm.py` and `src/agent/router.py` handle natural language intent parsing via the Gemini API.
- **Data Pipeline:** `src/data_processing/cleaner.py` imputes missing values and drops duplicates automatically.
- **RAG & Context:** `src/rag/vector_store.py` (ChromaDB) stores column metadata to make the LLM aware of the available data structures.
- **ML Module:** `src/ml/automl.py` trains Regression/Classification models dynamically based on target dtype.
- **Visualization:** `src/visualization/plotter.py` constructs Plotly charts dynamically based on LLM outputs.

## Setup Instructions

1. Clone or download the repository.
2. Initialize virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or .\venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. Add your Gemini API key in `.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```
4. Run the app:
   ```bash
   streamlit run ui/app.py
   ```

A sample dataset is provided in `data/sample_data.csv`. Upload it to the UI and ask questions like:
- "What is the average customer satisfaction?"
- "Plot a bar chart of Active_Users grouped by Region"
- "Predict Revenue using New_Users and Active_Users"

