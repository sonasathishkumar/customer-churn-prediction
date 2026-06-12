# Customer Churn Prediction

A complete end-to-end Machine Learning web application to predict customer churn using the Telco Customer Churn dataset.

## Features
- **Predict Churn**: Interactive UI to predict whether a customer will churn based on their profile.
- **Model Performance**: Visualizations of the model's performance, including a Confusion Matrix and ROC Curve.
- **Data Insights**: Interactive EDA charts and global feature importance using SHAP values.
- **Dark Theme**: A beautiful, modern dark-themed user interface.

## Tech Stack
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-1?style=for-the-badge&logo=xgboost&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)

## How to Run Locally

1. **Clone the repository** (if applicable) and navigate to the directory:
   ```bash
   cd customer-churn-prediction
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Train the model** (This generates the required assets in the `outputs/` folder and saves `churn_model.pkl`):
   ```bash
   python churn_model.py
   ```

4. **Run the Streamlit application**:
   ```bash
   streamlit run app.py
   ```

5. Open your browser and navigate to `http://localhost:8501`.

## How to Run with Docker

1. **Build the Docker image**:
   ```bash
   docker build -t churn-app .
   ```

2. **Run the Docker container**:
   ```bash
   docker run -p 8501:8501 churn-app
   ```

3. Open your browser and navigate to `http://localhost:8501`.

## Screenshots
*(Placeholder for screenshots of the application)*
- **Predict Page**: Shows the prediction form.
- **Performance Page**: Displays evaluation metrics.
- **Insights Page**: Contains interactive charts.

---
**Author**: Sona S
[LinkedIn](#) | [GitHub](#)
