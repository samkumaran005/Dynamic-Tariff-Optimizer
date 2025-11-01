# ================== app.py ==================
from flask import Flask, render_template, request, jsonify
import json
from optimizer import EnergyOptimizer
from datetime import datetime

app = Flask(__name__)
optimizer = EnergyOptimizer()

@app.route('/')
def index():
    tariffs = optimizer.load_tariffs()
    return render_template('index.html', tariffs=tariffs)

@app.route('/appliances')
def appliances():
    appliances_list = optimizer.load_appliances()
    return render_template('appliances.html', appliances=appliances_list)

@app.route('/scheduler')
def scheduler():
    appliances_list = optimizer.load_appliances()
    tariffs = optimizer.load_tariffs()
    return render_template('scheduler.html', appliances=appliances_list, tariffs=tariffs)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/add_appliance', methods=['POST'])
def add_appliance():
    data = request.json
    result = optimizer.add_appliance(data)
    return jsonify(result)

@app.route('/api/delete_appliance/<int:appliance_id>', methods=['DELETE'])
def delete_appliance(appliance_id):
    result = optimizer.delete_appliance(appliance_id)
    return jsonify(result)

@app.route('/api/optimize', methods=['POST'])
def optimize_schedule():
    data = request.json
    appliance_ids = data.get('appliances', [])
    constraints = data.get('constraints', {})
    
    recommendations = optimizer.optimize_schedule(appliance_ids, constraints)
    return jsonify(recommendations)

@app.route('/api/calculate_savings', methods=['POST'])
def calculate_savings():
    data = request.json
    savings = optimizer.calculate_savings(data)
    return jsonify(savings)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
