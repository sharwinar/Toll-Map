from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import pandas as pd
import random

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load data
toll_data = pd.read_csv('Toll_data.csv')  # Toll data CSV

# Clean lat/long columns
toll_data['Toll_Lat'] = toll_data['Toll_Lat'].astype(str).str.replace(r'\s+', '', regex=True)
toll_data['Toll_Long'] = toll_data['Toll_Long'].astype(str).str.replace(r'\s+', '', regex=True)

# Convert lat/long columns to floats
def safe_float(value):
    try:
        return float(value)
    except ValueError:
        return None

toll_data['Toll_Lat'] = toll_data['Toll_Lat'].apply(safe_float)
toll_data['Toll_Long'] = toll_data['Toll_Long'].apply(safe_float)

@app.route('/')
def index():
    return render_template('Untitled-1.html')

@app.route('/markers')
def get_markers():
    zone = request.args.get('zone')  # Selected zone
    region = request.args.get('region')  # Selected region
    markers = []

    # Filter toll data
    filtered_toll_data = toll_data
    if zone:
        filtered_toll_data = filtered_toll_data[filtered_toll_data['Zone'] == zone]
    if region:
        filtered_toll_data = filtered_toll_data[filtered_toll_data['Region'] == region]

    # Add Toll markers
    for _, row in filtered_toll_data.iterrows():
        if pd.notna(row['Toll_Lat']) and pd.notna(row['Toll_Long']):
            # Find the TSL marker linked to this Toll marker
            markers.append({
                'location': row['Plaza Name'],
                'Code': row['Plaza_Code'],
                'latitude': row['Toll_Lat'],
                'longitude': row['Toll_Long'],
                'type': 'Toll',
                'zone': row['Zone'],
                'region': row['Region'],
                'tagged': row['Tagged']
            })

    return jsonify(markers)


@app.route('/zones', methods=['GET'])
def get_zones():
    zones = toll_data['Zone'].unique().tolist()
    return jsonify(zones)

@app.route('/regions', methods=['GET'])
def get_regions():
    zone = request.args.get('zone')
    if zone:
        regions = toll_data[toll_data['Zone'] == zone]['Region'].unique().tolist()
    else:
        regions = toll_data['Region'].unique().tolist()
    return jsonify(regions)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
