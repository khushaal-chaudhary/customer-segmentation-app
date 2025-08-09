# Customer Segmentation Apparatus 🔮

An interactive, full-stack web application for customer segmentation using RFM analysis and K-Means clustering. This tool allows users to analyze a sample dataset or upload their own to discover meaningful customer personas.

**[Link to Live Demo - We will add this later]**

---


*(You can add a screenshot here after taking one)*

## About The Project

This project was built to demonstrate a full-stack data science workflow, from backend data processing with Python to a sophisticated, interactive frontend with JavaScript. The application takes transactional customer data, calculates RFM (Recency, Frequency, Monetary) metrics, and uses the K-Means algorithm to group customers into distinct segments.

The results are presented in an interactive 3D plot and accompanied by auto-generated "personas" that give qualitative meaning to each customer group, making the insights immediately actionable for marketing and business strategy.

## Key Features

* **Dynamic Analysis:** Use the provided sample dataset or upload your own `.csv` or `.xlsx` files.
* **Interactive UI:** A modern, responsive interface built with a sophisticated dark theme and animations.
* **Configurable Parameters:** Users can dynamically select columns for analysis and choose the desired number of customer segments.
* **3D Visualization:** Customer segments are plotted in an interactive 3D space using Plotly.js.
* **Automatic Persona Generation:** The backend analyzes the clusters and assigns meaningful, descriptive personas (e.g., "👑 The VIPs," "👻 The Ghosts") to each segment.
* **Contextual Information:** Tooltips and an "About" modal explain the methodology to the user.
* **Optimized Backend:** The backend uses caching for the default dataset to ensure a near-instant user experience.

## Tech Stack

* **Backend:** Python, Flask, Pandas, Scikit-learn
* **Frontend:** HTML5, CSS3, JavaScript (ES6+)
* **Visualization:** Plotly.js

## How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone [your-repo-link]
    ```
2.  **Navigate to the `backend` directory and create a virtual environment:**
    ```bash
    cd backend
    python -m venv venv
    venv\Scripts\activate  # On Windows
    source venv/bin/activate # On Mac/Linux
    ```
3.  **Install backend dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the backend server:**
    ```bash
    python app.py
    ```
    The backend will be running at `http://127.0.0.1:5000`.

5.  **Run the frontend:**
    * Navigate to the `frontend` directory.
    * Open the `index.html` file in your web browser.

---
Created by Khushaal Chaudhary - Let's connect on [LinkedIn](https://www.linkedin.com/in/khushaal-chaudhary)!