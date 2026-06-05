import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report

def train_and_evaluate(df: pd.DataFrame, target_col: str, feature_cols: list):
    """
    Train a simple model (Regression or Classification) right away based on the target column type.
    """
    if target_col not in df.columns:
        raise ValueError(f"Target column {target_col} not found in dataset.")
        
    df_clean = df.dropna(subset=[target_col] + feature_cols).copy()
    
    # Preprocess categorical features
    label_encoders = {}
    for col in feature_cols:
        if df_clean[col].dtype == 'object' or str(df_clean[col].dtype) == 'category':
            le = LabelEncoder()
            df_clean[col] = le.fit_transform(df_clean[col].astype(str))
            label_encoders[col] = le

    X = df_clean[feature_cols]
    y = df_clean[target_col]
    
    is_classification = False
    if y.dtype == 'object' or str(y.dtype) == 'category' or y.nunique() < 10:
        is_classification = True
        le_target = LabelEncoder()
        y = le_target.fit_transform(y.astype(str))
        label_encoders[target_col] = le_target
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    results = {}
    
    if is_classification:
        model = DecisionTreeClassifier(max_depth=5, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        results['task'] = 'Classification'
        results['model'] = 'Decision Tree'
        results['accuracy'] = float(accuracy_score(y_test, y_pred))
        # simplify classification report
        report = classification_report(y_test, y_pred, output_dict=True)
        results['report'] = {k: v for k, v in report.items() if isinstance(v, dict)}
    else:
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        results['task'] = 'Regression'
        results['model'] = 'Linear Regression'
        results['mse'] = float(mean_squared_error(y_test, y_pred))
        results['r2'] = float(r2_score(y_test, y_pred))
        
    return results, model
