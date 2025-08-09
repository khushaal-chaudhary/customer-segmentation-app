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

DEFAULT_RFM_DF = None

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

def prepare_default_data():
    use_sample = os.getenv('USE_SAMPLED_DATA', 'true').lower() == 'true'
    filename = 'online_retail_sampled.csv' if use_sample else 'online_retail_II.csv'
    print(f"--- LAZY LOADING: Preparing {filename}... ---")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, filename)
    df = pd.read_csv(csv_path)

    df.dropna(subset=['Customer ID'], inplace=True)
    df = df[df['Quantity'] > 0]
    df['Customer ID'] = df['Customer ID'].astype(str)
    df['TotalPrice'] = df['Quantity'] * df['Price']

    # ### THIS LINE IS NOW CORRECTED ###
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    snapshot_date = df['InvoiceDate'].max() + dt.timedelta(days=1)
    rfm_df = df.groupby(['Customer ID']).agg({
        'InvoiceDate': lambda date: (snapshot_date - date.max()).days, 
        'Invoice': 'nunique', 
        'TotalPrice': 'sum'
    })
    rfm_df.rename(columns={'InvoiceDate': 'Recency', 'Invoice': 'Frequency', 'TotalPrice': 'MonetaryValue'}, inplace=True)
    print("--- LAZY LOADING: Default dataset is now cached. ---")
    return rfm_df

def assign_persona(rfm_with_clusters):
    agg_df = rfm_with_clusters.groupby('Cluster').agg(Recency=('Recency', 'mean'), Frequency=('Frequency', 'mean'), MonetaryValue=('MonetaryValue', 'mean')).round(2)
    agg_df['r_rank'] = agg_df['Recency'].rank(ascending=True)
    agg_df['f_rank'] = agg_df['Frequency'].rank(ascending=False)
    agg_df['m_rank'] = agg_df['MonetaryValue'].rank(ascending=False)
    agg_df['score'] = agg_df['r_rank'] + agg_df['f_rank'] + agg_df['m_rank']
    persona_list = []
    best_cluster, lapsed_cluster = agg_df['score'].idxmin(), agg_df['Recency'].idxmax()
    for cluster_id, row in agg_df.iterrows():
        persona, description = "Unknown", "A distinct customer segment."
        if cluster_id == best_cluster:
            persona, description = "👑 The VIPs", "They basically live here. They buy often, spend big, and probably have a favorite parking spot. Don't upset them."
        elif cluster_id == lapsed_cluster:
            persona, description = "👻 The Ghosts", "We remember them, but do they remember us? They haven't been seen in ages. Send a search party (with a discount code)."
        else:
            if row['f_rank'] < row['r_rank'] and row['f_rank'] < row['m_rank']:
                persona, description = "💡 The Hopefuls", "They keep showing up to the party but aren't spending much yet. A little encouragement could turn them into VIPs."
            elif row['r_rank'] == 1:
                persona, description = "🌱 The Newbies", "Fresh faces! They just walked in. Be nice, show them around, and maybe they'll stick around."
            else:
                persona, description = "☕ The Regulars", "Not flashy, but they keep the lights on. They're the reliable backbone of the business. Give them a nod of appreciation."
        if any(p['persona'] == persona for p in persona_list):
             persona, description = f"Segment {cluster_id}", "A distinct customer segment."
        persona_list.append({"cluster_id": int(cluster_id), "persona": persona, "description": description, "avg_recency": float(row['Recency']), "avg_frequency": float(row['Frequency']), "avg_monetary": float(row['MonetaryValue'])})
    return persona_list

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
    global DEFAULT_RFM_DF
    config_str = request.form.get('config')
    if not config_str: return jsonify({"error": "Configuration data was missing."}), 400
    config = json.loads(config_str)
    use_default, cluster_count = config.get('use_default', True), int(config.get('cluster_count', 4))
    rfm_df = None
    if use_default:
        if DEFAULT_RFM_DF is None:
            DEFAULT_RFM_DF = prepare_default_data()
        rfm_df = DEFAULT_RFM_DF.copy()
    else:
        if 'file' not in request.files: return jsonify({"error": "No file part"}), 400
        file, mappings = request.files['file'], config.get('mappings', {})
        try:
            if file.filename.endswith('.csv'): df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
            elif file.filename.endswith('.xlsx'): df = pd.read_excel(io.BytesIO(file.read()))
        except Exception as e: return jsonify({"error": f"Error reading file: {e}"}), 500
        customer_id_col, invoice_id_col, invoice_date_col, quantity_col, price_col = (mappings.get('customer_id'), mappings.get('invoice_id'), mappings.get('invoice_date'), mappings.get('quantity'), mappings.get('price'))
        df.dropna(subset=[customer_id_col], inplace=True)
        df = df[df[quantity_col] > 0]
        df[customer_id_col] = df[customer_id_col].astype(str)
        df['TotalPrice'] = df[quantity_col] * df[price_col]
        df[invoice_date_col] = pd.to_datetime(df[invoice_date_col])
        snapshot_date = df[invoice_date_col].max() + dt.timedelta(days=1)
        rfm_df = df.groupby([customer_id_col]).agg({'InvoiceDate': lambda date: (snapshot_date - date.max()).days, invoice_id_col: 'nunique', 'TotalPrice': 'sum'})
        rfm_df.rename(columns={'InvoiceDate': 'Recency', invoice_id_col: 'Frequency', 'TotalPrice': 'MonetaryValue'}, inplace=True)
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_df)
    kmeans = KMeans(n_clusters=cluster_count, init='k-means++', random_state=42, n_init=10)
    kmeans.fit(rfm_scaled)
    rfm_df['Cluster'] = kmeans.labels_
    plot_data_json = json.loads(rfm_df.to_json(orient='table', index=True))
    persona_data = assign_persona(rfm_df)
    final_response = {"plotData": plot_data_json, "personaData": persona_data}
    return jsonify(final_response)

if __name__ == '__main__':
    app.run(debug=True)