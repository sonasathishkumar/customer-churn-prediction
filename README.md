# 🛡️ ChurnIQ Enterprise — Customer Churn Prediction

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Deployed-ff4b4b?logo=streamlit)
![scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-orange?logo=scikit-learn)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)

> **Live Demo:** [customer-churn-sona.streamlit.app](https://customer-churn-sona.streamlit.app)
> **GitHub:** [sonasathishkumar/customer-churn-prediction](https://github.com/sonasathishkumar/customer-churn-prediction)

---

## 📌 Overview

ChurnIQ Enterprise is a production-grade, AI-powered customer churn prediction platform built for telecom businesses. It enables customer success teams to identify at-risk customers, understand churn drivers, and take proactive retention actions — all through an intuitive analytics portal.

---

## 🚀 Features

- **Predict Churn** — Real-time single customer churn prediction with risk score and SHAP explainability
- **Bulk Predict** — Upload CSV and predict churn for thousands of customers at once with PDF report generation
- **Simulator** — What-if analysis to simulate how customer changes affect churn probability
- **Model Comparison** — Compare Random Forest vs XGBoost performance metrics
- **Diagnostics** — Model health monitoring and feature importance analysis
- **Insights** — Business intelligence dashboard with revenue at risk and loyalty scores
- **Admin Panel** — Upload new data and retrain the model pipeline on demand
- **Secure Login** — SHA-256 authenticated user accounts

---

## 📊 Model Performance

| Metric | Score |
|--------|-------|
| Accuracy | 91% |
| ROC-AUC | 0.84 |
| Precision | 0.65 |
| Recall | 0.49 |
| F1-Score | 0.56 |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| ML Pipeline | Python, Scikit-learn, XGBoost |
| Explainability | SHAP (SHapley Additive exPlanations) |
| Frontend | Streamlit |
| Visualization | Plotly, Matplotlib, Seaborn |
| Reporting | FPDF2, ReportLab |
| Containerization | Docker |
| BI Dashboard | Power BI |
| Deployment | Streamlit Community Cloud |

---

## 📁 Project Structure

```
customer-churn-prediction/
├── app.py               # Main Streamlit application
├── churn_model.py       # ML training pipeline
├── churn_model.pkl      # Pre-trained model
├── data/
│   └── telco_churn.csv  # Training dataset
├── outputs/             # Generated reports
├── Dockerfile           # Docker configuration
├── requirements.txt     # Python dependencies
└── README.md
```

---

## ⚙️ Installation & Run Locally

```bash
# Clone the repo
git clone https://github.com/sonasathishkumar/customer-churn-prediction.git
cd customer-churn-prediction

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Run with Docker
```bash
docker build -t customer-churn-app .
docker run -p 8501:8501 customer-churn-app
```


