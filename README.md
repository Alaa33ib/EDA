# 📱 Samsung Global Sales Intelligence: Strategic EDA Dashboard

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📌 Project Overview
This project performs a comprehensive **Exploratory Data Analysis (EDA)** on a synthetic dataset of **15,500 Samsung Global Sales transactions** (2021–2024). The goal was to transform a messy, high-dimensional sales ledger into an interactive **Business Intelligence Dashboard** that provides actionable insights for regional managers and product strategists.

### 🎯 Key Objectives
* **Market Segmentation:** Identify which regions (e.g., Middle East, Europe) drive the highest revenue for flagship series like the Galaxy Z.
* **Data Quality Engineering:** Handle significant missing values (Storage, Customer Ratings, Previous OS) using logical and statistical imputation.
* **Price Optimization:** Analyze the relationship between discount percentages and sales volume across different customer segments.
* **Global Footprint:** Visualize sales density across 52 countries using interactive geospatial mapping.

---

## 📊 Visual Highlights

### 1. Global Revenue Distribution
Interactive Choropleth map identifying high-performing markets and expansion opportunities.
> *[Insert Screenshot of your Plotly Map here]*

### 2. Product Seasonality Heatmap
A matrix view showing which quarters see the highest demand for specific product categories (e.g., Q4 peaks for Smart TVs).
> *[Insert Screenshot of your Seaborn Heatmap here]*

### 3. Galaxy Z Series Deep Dive
Analysis of the adoption of foldable technology (Flip vs. Fold) across different age groups and years.
> *[Insert Screenshot of your Galaxy Z Histplot here]*

---

## 🛠️ Data Engineering & Cleaning
The raw dataset contained several "real-world" data quality issues that were resolved:
* **Missing Value Imputation:**
    * `storage`: Filled using the **Mode** per product name (e.g., Galaxy S24 → 256GB).
    * `previous_device_os`: Categorized as **'Unknown'** to preserve data for customer loyalty analysis.
    * `customer_rating`: Filled using the **Median** to avoid skewing sentiment analysis.
* **Outlier Strategy:** Instead of deleting high-value "Success Spikes" (e.g., B2B bulk orders), I used **Winsorization** and **Binary Flagging** to highlight these VIP transactions for the business users.

---

## 💻 Tech Stack
* **Language:** Python 3.x
* **Data Wrangling:** Pandas, NumPy
* **Visualization:** Matplotlib, Seaborn, Plotly Express
* **Dashboarding:** Streamlit
* **Environment:** Google Colab / Jupyter Notebook

---

## 🚀 How to Run the Dashboard
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/samsung-sales-eda.git](https://github.com/yourusername/samsung-sales-eda.git)
   
2. **Install dependencies:**
   ```bash
    pip install -r requirements.txt

3. **Run the app:**
  ```bash
  streamlit run app.py
