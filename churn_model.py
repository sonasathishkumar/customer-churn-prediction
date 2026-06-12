import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report, confusion_matrix, roc_curve
import xgboost as xgb
import shap
import pickle
import os

def load_and_preprocess_data():
    df = pd.read_csv('data/telco_churn.csv')
    
    # TotalCharges contains empty strings for some rows, replace and drop
    if 'TotalCharges' in df.columns:
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    df = df.dropna()
    
    # Drop customerID
    if 'customerID' in df.columns:
        df = df.drop('customerID', axis=1)
    
    # Identify categorical columns
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    # Label Encoding
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
        
    df.to_csv('data/processed.csv', index=False)
    
    X = df.drop('Churn', axis=1)
    y = df['Churn']
    
    return train_test_split(X, y, test_size=0.2, random_state=42), label_encoders

def train_and_evaluate():
    (X_train, X_test, y_train, y_test), label_encoders = load_and_preprocess_data()
    
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(random_state=42)
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    print(f"Random Forest Accuracy: {accuracy_score(y_test, rf_preds):.4f}")
    
    print("Training XGBoost with GridSearchCV...")
    xgb_model = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
    
    param_grid = {
        'n_estimators': [50, 100],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2]
    }
    
    grid_search = GridSearchCV(estimator=xgb_model, param_grid=param_grid, cv=3, scoring='accuracy', n_jobs=-1)
    grid_search.fit(X_train, y_train)
    
    best_xgb = grid_search.best_estimator_
    print(f"Best XGBoost Params: {grid_search.best_params_}")
    
    y_pred = best_xgb.predict(X_test)
    y_prob = best_xgb.predict_proba(X_test)[:, 1]
    
    # Metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)
    
    print("\nBest Model (XGBoost) Performance:")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    
    # Save Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.savefig('outputs/confusion_matrix.png')
    plt.close()
    
    # Save ROC Curve
    fpr, tpr, thresholds = roc_curve(y_test, y_prob)
    plt.figure(figsize=(6, 4))
    plt.plot(fpr, tpr, label=f'AUC = {roc_auc:.2f}')
    plt.plot([0, 1], [0, 1], 'r--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend(loc='lower right')
    plt.savefig('outputs/roc_curve.png')
    plt.close()
    
    # SHAP Summary Plot
    explainer = shap.Explainer(best_xgb)
    shap_values = explainer(X_train)
    
    plt.figure()
    shap.summary_plot(shap_values, X_train, show=False)
    plt.savefig('outputs/shap_summary.png', bbox_inches='tight')
    plt.close()
    
    # Save Best Model and Encoders
    model_data = {
        'model': best_xgb,
        'label_encoders': label_encoders,
        'features': X_train.columns.tolist()
    }
    with open('churn_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    print("\nModel saved to churn_model.pkl")

if __name__ == '__main__':
    if not os.path.exists('outputs'):
        os.makedirs('outputs')
    train_and_evaluate()
