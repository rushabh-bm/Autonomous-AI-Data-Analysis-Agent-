import json
import logging
from src.agent.llm import generate_response

logger = logging.getLogger(__name__)

class AgentRouter:
    """
    Decides what action should be taken based on user query.
    Intents:
    - DESCRIPTIVE: General questions about the data, EDA, summary.
    - VISUALIZATION: Requests to plot charts, graphs, heatmaps.
    - PREDICTION: Requests to perform machine learning, classification, or regression.
    """
    
    @staticmethod
    def classify_intent(query: str, columns_context: str = "") -> dict:
        prompt = f"""
        You are an autonomous AI Data Analysis Agent routing assistant. 
        Analyze the user's query and decide what type of action is required.
        
        AVAILABLE ACTIONS:
        - "DESCRIPTIVE" (e.g., "What is the average sales?", "Summarize the data", "How many missing values?")
        - "VISUALIZATION" (e.g., "Plot a bar chart of users", "Show me a scatter plot of X vs Y", "correlation")
        - "PREDICTION" (e.g., "Predict revenue based on marketing", "Build a model to classify users")
        
        Data Context (Available Columns):
        {columns_context}
        
        User Query: {query}
        
        Respond ONLY with a valid JSON in exactly this format, no markdown formatting or backticks:
        {{
            "intent": "DESCRIPTIVE" | "VISUALIZATION" | "PREDICTION",
            "reasoning": "Brief explanation of why",
            "columns_needed": ["list", "of", "relevant", "columns"]
        }}
        """
        
        response_text = generate_response(prompt)
        try:
            # Clean up the response if it has html/markdown tags
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:-3]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:-3]
            
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Failed to parse LLM intent JSON: {response_text}. Error: {e}")
            # Fallback
            return {"intent": "DESCRIPTIVE", "reasoning": "Fallback to descriptive", "columns_needed": []}
