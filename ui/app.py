import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from src.data_processing.cleaner import load_data, auto_clean_data
from src.data_processing.eda import generate_summary
from src.rag.vector_store import VectorStore
from src.agent.memory import ConversationMemory
from src.agent.router import AgentRouter
from src.agent.llm import generate_response
from src.visualization.plotter import generate_plot
from ui.components import (
    load_css, render_hero_header, render_metric_card,
    render_section_header, render_chat_message, render_agent_status
)
import json
import traceback

st.set_page_config(
    page_title="Data.AI Agent",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

def main():
    load_css("ui/styles.css")
    
    # ── Session State Init ──
    if 'memory' not in st.session_state:
        st.session_state.memory = ConversationMemory()
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = VectorStore(persist_directory=".chroma_db")
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'columns_context' not in st.session_state:
        st.session_state.columns_context = ""
    if 'summary' not in st.session_state:
        st.session_state.summary = None

    # ═══════════════════ SIDEBAR ═══════════════════
    with st.sidebar:
        st.markdown("### 📂 Data Upload")
        st.caption("Supports CSV and Excel files")
        uploaded_file = st.file_uploader(
            "Drop your dataset here",
            type=['csv', 'xlsx'],
            label_visibility="collapsed"
        )
        
        if uploaded_file and st.session_state.df is None:
            with st.spinner("🔄 Auto-cleaning & indexing dataset..."):
                raw_df = load_data(uploaded_file)
                clean_df = auto_clean_data(raw_df)
                st.session_state.df = clean_df
                st.session_state.summary = generate_summary(clean_df)
                st.session_state.vector_store.embed_dataset_columns(clean_df)
                st.session_state.columns_context = ", ".join(clean_df.columns)
            st.success("✅ Dataset cleaned, missing values handled, and ready!")

        if st.session_state.df is not None:
            st.divider()
            st.markdown("### 📥 Export")
            from src.visualization.report import generate_pdf_report
            try:
                pdf_bytes = generate_pdf_report(
                    st.session_state.summary,
                    st.session_state.memory.messages
                )
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_bytes,
                    file_name="ai_analysis_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF error: {e}")
                
            st.divider()
            st.markdown("### ℹ️ Quick Stats")
            s = st.session_state.summary
            st.markdown(f"**Rows:** {s['n_rows']}")
            st.markdown(f"**Columns:** {s['n_cols']}")
            st.markdown(f"**Numeric:** {len(s['numeric_cols'])}")
            st.markdown(f"**Categorical:** {len(s['categorical_cols'])}")

    # ═══════════════════ MAIN AREA ═══════════════════
    render_hero_header()

    if st.session_state.df is None:
        # Empty state
        st.markdown("""
            <div style="text-align:center; padding: 4rem 2rem; color: #475569;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
                <div style="font-size: 1.2rem; font-weight: 500; color: #64748b;">
                    Upload a dataset to get started
                </div>
                <div style="font-size: 0.9rem; color: #475569; margin-top: 0.5rem;">
                    Use the sidebar to upload a CSV or Excel file
                </div>
            </div>
        """, unsafe_allow_html=True)
        return

    df = st.session_state.df
    summary = st.session_state.summary

    # ── Metric Cards ──
    render_section_header("📊", "Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1: render_metric_card("📋", "ROWS", f"{summary['n_rows']:,}")
    with col2: render_metric_card("📐", "COLUMNS", summary['n_cols'])
    with col3: render_metric_card("🔢", "NUMERIC", len(summary['numeric_cols']))
    with col4: render_metric_card("🏷️", "CATEGORICAL", len(summary['categorical_cols']))

    # ── Data Preview ──
    with st.expander("🔍 Preview Data (first 10 rows)", expanded=False):
        st.dataframe(df.head(10), width='stretch')

    st.divider()

    # ═══════════════════ CHAT INTERFACE ═══════════════════
    render_section_header("💬", "Chat with your Data")

    # Display chat history
    for msg in st.session_state.memory.messages:
        render_chat_message(msg['role'], msg['content'])

    user_query = st.chat_input(
        "Ask anything — e.g. 'Show a bar chart of Revenue by Region' or 'Predict New_Users'"
    )

    if user_query:
        render_chat_message("user", user_query)
        st.session_state.memory.add_user_message(user_query)

        with st.spinner(""):
            render_agent_status("Thinking — analyzing your question...")
            try:
                # Step 1: Retrieve context
                relevant_docs = st.session_state.vector_store.search_relevant_columns(user_query)
                context = f"All Columns: {st.session_state.columns_context}. Relevant Details: {relevant_docs}"

                # Step 2: Route intent
                intent_json = AgentRouter.classify_intent(user_query, context)
                intent = intent_json.get("intent", "DESCRIPTIVE")
                reasoning = intent_json.get("reasoning", "")

                st.markdown(f"""
                    <div class="agent-status">
                        🧭 <strong>Intent:</strong> {intent} &nbsp;|&nbsp; 💡 {reasoning}
                    </div>
                """, unsafe_allow_html=True)

                # Step 3: Execute
                reply = ""
                if intent == "VISUALIZATION":
                    render_agent_status("Generating visualization...")
                    plot_prompt = (
                        f"Given columns {st.session_state.columns_context}, the user wants: '{user_query}'. "
                        f"Determine the best plot type (bar, line, scatter, pie, histogram, box) and columns to use. "
                        f"Return ONLY JSON: {{\"plot_type\": \"type\", \"x_col\": \"col1\", \"y_col\": \"col2\"}}. "
                        f"If a dimension isn't needed, use null."
                    )
                    resp = generate_response(plot_prompt).strip()
                    if resp.startswith("```json"): resp = resp[7:-3]
                    elif resp.startswith("```"): resp = resp[3:-3]

                    try:
                        plot_args = json.loads(resp)
                        fig = generate_plot(
                            df, plot_args['plot_type'],
                            plot_args.get('x_col'),
                            plot_args.get('y_col')
                        )
                        fig.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Inter", color="#e2e8f0"),
                            margin=dict(t=50, b=30, l=40, r=20)
                        )
                        st.plotly_chart(fig, width='stretch')
                        reply = "Here's the visualization you requested. ✨"
                    except Exception as e:
                        reply = f"Couldn't generate the plot. Please ensure the required columns exist in your dataset."
                        st.error(str(e))

                elif intent == "PREDICTION":
                    render_agent_status("Training ML model...")
                    from src.ml.automl import train_and_evaluate
                    ml_prompt = (
                        f"User query: '{user_query}'. Available cols: {st.session_state.columns_context}. "
                        f"Identify the target variable and features. "
                        f"Return exactly JSON: {{\"target\": \"col_name\", \"features\": [\"col1\",\"col2\"]}}"
                    )
                    resp = generate_response(ml_prompt).strip()
                    if resp.startswith("```json"): resp = resp[7:-3]
                    elif resp.startswith("```"): resp = resp[3:-3]

                    try:
                        ml_args = json.loads(resp)
                        results, model = train_and_evaluate(df, ml_args['target'], ml_args['features'])

                        # Display results in nice columns
                        r1, r2 = st.columns(2)
                        with r1:
                            st.markdown("#### 🏷️ Model Info")
                            st.markdown(f"**Task:** {results['task']}")
                            st.markdown(f"**Algorithm:** {results['model']}")
                        with r2:
                            st.markdown("#### 📈 Performance")
                            if results['task'] == 'Regression':
                                st.markdown(f"**R² Score:** {results['r2']:.4f}")
                                st.markdown(f"**MSE:** {results['mse']:.2f}")
                            else:
                                st.markdown(f"**Accuracy:** {results['accuracy']:.2%}")

                        reply = f"✅ Trained a **{results['model']}** for **{results['task']}** successfully."
                    except Exception as e:
                        reply = "ML training failed. Ensure you specified valid target/feature columns."
                        st.error(str(e))

                else:  # DESCRIPTIVE
                    qa_prompt = (
                        f"Data context: {context}\n"
                        f"Chat History:\n{st.session_state.memory.get_context_string(3)}\n"
                        f"User: {user_query}\n\n"
                        f"Provide a helpful, concise, data-driven answer."
                    )
                    reply = generate_response(qa_prompt)

                render_chat_message("assistant", reply)
                st.session_state.memory.add_assistant_message(reply)
            except Exception as e:
                st.error(f"Error: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
