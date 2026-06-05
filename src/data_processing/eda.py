import pandas as pd
import numpy as np

def generate_summary(df: pd.DataFrame) -> dict:
    """
    Generate comprehensive summary statistics for the dataframe.
    """
    summary = {}
    
    # Basic info
    summary['n_rows'] = df.shape[0]
    summary['n_cols'] = df.shape[1]
    
    # Missing values before cleaning (if called on raw)
    summary['missing_cells'] = int(df.isnull().sum().sum())
    
    # Column types
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime']).columns.tolist()
    
    summary['numeric_cols'] = numeric_cols
    summary['categorical_cols'] = categorical_cols
    summary['datetime_cols'] = datetime_cols
    
    # Descriptive statistics
    if numeric_cols:
        summary['numeric_describe'] = df[numeric_cols].describe().to_dict()
    else:
        summary['numeric_describe'] = {}
        
    if categorical_cols:
        try:
            summary['categorical_describe'] = df[categorical_cols].describe(include=['object', 'category']).to_dict()
        except:
            summary['categorical_describe'] = {}
    else:
        summary['categorical_describe'] = {}
    
    return summary
