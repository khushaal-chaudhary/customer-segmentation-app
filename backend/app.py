import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime as dt
import json
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import io
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# We will not use the lazy loading or data for this test
# DEFAULT_RFM_DF = None

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# The original prepare_default_data and assign_persona functions are still here,
# but they won't be called by the /analyze route in this test.
def prepare_default_data():
    # ...
    return None
def assign_persona(rfm_with_clusters):
    # ...
    return []

@app.route('/get-headers', methods=['POST'])
def get_headers():
    if 'file' not in request.files: return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400
    try:
        if file.filename.endswith('.csv'): df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'): df = pd.read_excel(file)
        else: return jsonify({"error": "Unsupported file type"}), 400
        return jsonify({"headers": df.columns.tolist()})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_data():
    # ### TEMPORARY DEBUGGING CODE ###
    # We are bypassing all data processing and returning an instant, dummy response.
    print("--- DEBUG: Bypassing analysis and returning dummy data ---")

    # Create fake data that looks like our real data structure
    dummy_plot_data = {"schema": {"fields":[]}, "data": []}
    dummy_persona_data = [
        {"cluster_id": 0, "persona": "Test Persona", "description": "This is a test to check the connection.", 
         "avg_recency": 0, "avg_frequency": 0, "avg_monetary": 0}
    ]

    final_response = {"plotData": dummy_plot_data, "personaData": dummy_persona_data}
    return jsonify(final_response)

if __name__ == '__main__':
    app.run(debug=True)