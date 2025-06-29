#!/usr/bin/env python3
"""
Port Tariff Calculator API
Flask API endpoint for calculating vessel tariffs
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import sys
import os
import re
import google.generativeai as genai

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.section_rag_calculator import SectionRAGCalculator

app = Flask(__name__)
CORS(app)

# Global calculator instance\ # ensure only one initialization
calculator = None

def initialize_calculator():
    """
    Initialize the SectionRAGCalculator with pre-processed Markdown
    """
    global calculator
    if calculator is None:
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')
        genai.configure(api_key=GEMINI_API_KEY)

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        MD_PATH = os.path.join(project_root, 'src', 'port_tariff.md')
        if not os.path.exists(MD_PATH):
            raise FileNotFoundError(f"Markdown file not found at {MD_PATH}. Run parser first.")
        with open(MD_PATH, 'r', encoding='utf-8') as f:
            document_content = f.read()
        calculator = SectionRAGCalculator(GEMINI_API_KEY)
        calculator.process_document(document_content)
    return calculator

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Port Tariff Calculator API', 'version': '1.0.0'})

@app.route('/calculate-tariffs', methods=['POST'])
def calculate_tariffs_api():
    try:
        calc = initialize_calculator()
        data = request.get_json() or {}
        query = data.get('query', '')
        port = data.get('port', '')
        vessel_info = data.get('vessel_info')

        # If vessel_info not provided, use Gemini-2.5-flash to extract all fields
        if not vessel_info:
            GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')
            genai.configure(api_key=GEMINI_API_KEY)
            prompt = (
                "Extract vessel details as JSON with keys name, vessel_type, gross_tonnage, "
                "dead_weight_tonnage, net_tonnage, total_length, operations, flag, port from: "
                f"{query}"
            )
            response = genai.generate(
                model='gemini-2.5-flash',
                prompt=prompt
            )
            try:
                vessel_info = json.loads(response.text)
            except Exception:
                return jsonify({'status': 'error', 'error': 'Failed to parse vessel info from Gemini response'}), 400
            vessel_info.setdefault('port', port or vessel_info.get('port', 'Durban'))

        # Validate required fields
        missing = [f for f in ('name', 'gross_tonnage', 'port') if f not in vessel_info]
        if missing:
            return jsonify({'status': 'error', 'error': f'Missing fields: {missing}'}), 400

        # Defaults for optional fields
        defaults = {
            'dead_weight_tonnage': 0,
            'net_tonnage': 0,
            'total_length': 0,
            'operations': 2,
            'flag': 'Unknown'
        }
        for k, v in defaults.items():
            vessel_info.setdefault(k, v)

        # Calculate tariffs
        results = calc.calculate_tariffs(vessel_info)

        # Build response
        fee_map = {
            'light_dues': 'Light Dues',
            'port_dues': 'Port Dues',
            'vts_charges': 'VTS Charges',
            'pilotage': 'Pilotage',
            'towage': 'Towage',
            'berthing_services': 'Berthing Services',
            'running_of_vessel_lines_dues': 'Running of Vessel Lines Dues'
        }
        tariffs = {}
        total = 0
        for key, label in fee_map.items():
            amt = results.get(key, {}).get('amount', 0)
            tariffs[label] = {'amount': amt, 'currency': 'ZAR', 'formatted': f"R {amt:,.2f}"}
            total += amt
        summary = results.get('summary', {})

        return jsonify({
            'status': 'success',
            'vessel_info': {k: vessel_info[k] for k in ('name','gross_tonnage','port')},
            'tariffs': tariffs,
            'total': {'amount': total, 'currency': 'ZAR', 'formatted': f"R {total:,.2f}"},
            'summary': summary,
            'query': query
        })

    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/ports', methods=['GET'])
def get_supported_ports():
    return jsonify({'supported_ports': ['Durban', 'Saldanha', "Richard's Bay"], 'default': 'Durban'})

@app.route('/example', methods=['GET'])
def example_request():
    example = {
        'query': "Calculate the different tariffs payable by the following vessel berthing at the port of Durban: SUDESTADA, Bulk Carrier, 51,300 GT",
        'vessel_info': None,
        'port': None
    }
    return jsonify({'example_request': example, 'endpoint': '/calculate-tariffs', 'method': 'POST'})

if __name__ == '__main__':
    print("🚀 Starting API...")
    app.run(host='0.0.0.0', port=5000)
