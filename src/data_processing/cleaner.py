import pandas as pd
import numpy as np

def load_data(file) -> pd.DataFrame:
    """Load data from a CSV or Excel file."""
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        else:
            raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")
        return df
    except Exception as e:
        raise Exception(f"Error loading file: {str(e)}")

def auto_clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Automatically clean the dataframe:
    - Drop duplicates
    - Impute or drop missing values appropriately
    - Convert datatypes if necessary
    """
    df_cleaned = df.copy()
    
    # 1. Drop duplicates
    df_cleaned = df_cleaned.drop_duplicates()
    
    # 1.5 Replace empty strings or whitespace-only with NaN
    df_cleaned = df_cleaned.replace(r'^\s*$', np.nan, regex=True)
    
    # Drop columns that are completely NaN
    df_cleaned = df_cleaned.dropna(axis=1, how='all')
    
    # 2. Handle missing values
    for col in df_cleaned.columns:
        if df_cleaned[col].isnull().sum() > 0:
            if pd.api.types.is_numeric_dtype(df_cleaned[col]):
                # Fill missing numeric values with median to avoid outlier skew
                median_val = df_cleaned[col].median()
                if pd.isna(median_val):
                    df_cleaned[col] = df_cleaned[col].fillna(0)
                else:
                    df_cleaned[col] = df_cleaned[col].fillna(median_val)
            else:
                # Fill categorical missing values with the mode
                mode_val = df_cleaned[col].mode()
                if not mode_val.empty and not pd.isna(mode_val[0]):
                    df_cleaned[col] = df_cleaned[col].fillna(mode_val[0])
                else:
                    df_cleaned[col] = df_cleaned[col].fillna("Unknown")
                    
    # 3. Optimize datatypes
    # Convert obvious date columns that might be read as objects
    for col in df_cleaned.columns:
        if df_cleaned[col].dtype == 'object':
            try:
                # Attempt to convert to datetime if it looks like one, ignoring errors if mostly failing
                df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='ignore')
            except Exception:
                pass
                
    return df_cleaned
