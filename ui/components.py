import streamlit as st

def load_css(file_path):
    try:
        with open(file_path, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def render_hero_header():
    st.markdown("""
        <div class="hero-header">
            <h1>🧠 Data.AI Agent</h1>
            <p>Upload your dataset, ask anything in plain English — the AI agent will
            autonomously analyze, visualize, and predict for you.</p>
        </div>
    """, unsafe_allow_html=True)

def render_metric_card(icon, title, value):
    st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">{icon}</span>
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)

def render_section_header(icon, title):
    st.markdown(f"""
        <div class="section-header">
            <span style="font-size:1.5rem">{icon}</span>
            <h2>{title}</h2>
        </div>
    """, unsafe_allow_html=True)

def render_chat_message(role, content):
    css_class = "user-msg" if role == "user" else "bot-msg"
    avatar = "🧑‍💻" if role == "user" else "🤖"
    align = "flex-end" if role == "user" else "flex-start"
    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:{align}; margin-bottom:4px;">
            <div style="font-size:0.7rem; color:#64748b; margin-bottom:2px; padding:0 8px;">{avatar} {'You' if role=='user' else 'Agent'}</div>
            <div class="{css_class}">{content}</div>
        </div>
    """, unsafe_allow_html=True)

def render_agent_status(text):
    st.markdown(f"""
        <div class="agent-status">
            <span style="animation: pulseGlow 1s infinite;">⚡</span> {text}
        </div>
    """, unsafe_allow_html=True)
