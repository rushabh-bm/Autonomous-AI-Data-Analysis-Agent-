import plotly.express as px
import pandas as pd

def generate_plot(df: pd.DataFrame, plot_type: str, x_col: str, y_col: str = None, color_col: str = None, title: str = None):
    """
    Generate dynamic plotly charts based on LLM instruction.
    plot_type can be: "bar", "line", "scatter", "pie", "histogram", "box"
    """
    try:
        # Prevent errors if columns don't exist
        missing_cols = [c for c in [x_col, y_col, color_col] if c and c not in df.columns]
        if missing_cols:
            raise ValueError(f"Columns not found in dataset: {missing_cols}")

        if plot_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title or f"Bar Chart of {y_col} by {x_col}")
        elif plot_type == "line":
            # For lines, sort by x-axis usually makes sense, especially dates
            if x_col:
                df_sorted = df.sort_values(by=x_col)
            else:
                df_sorted = df
            fig = px.line(df_sorted, x=x_col, y=y_col, color=color_col, title=title or f"Line Chart of {y_col} over {x_col}")
        elif plot_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=title or f"Scatter Plot: {x_col} vs {y_col}")
        elif plot_type == "pie":
            fig = px.pie(df, names=x_col, values=y_col, title=title or f"Pie Chart of {x_col}")
        elif plot_type == "histogram":
            fig = px.histogram(df, x=x_col, color=color_col, title=title or f"Histogram of {x_col}")
        elif plot_type == "box":
            fig = px.box(df, x=x_col, y=y_col, color=color_col, title=title or f"Box Plot of {y_col} by {x_col}")
        else:
            raise ValueError(f"Unsupported plot type: {plot_type}")
            
        return fig
    except Exception as e:
        raise Exception(f"Failed to generate {plot_type} plot: {str(e)}")
