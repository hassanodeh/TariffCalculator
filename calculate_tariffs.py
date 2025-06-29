#!/usr/bin/env python3
"""
Port Tariff Calculator
CLI testing with the given example
"""
import os
import sys
import json
import argparse
from typing import Dict, Any
from src.parser import parse_pdf
from src.section_rag_calculator import SectionRAGCalculator

def calculate_tariffs(vessel_info: Dict[str, Any], port: str = "Durban") -> Dict[str, Any]:
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')
    
    # Initialize components
    print(f" Port Tariff Calculator:")
    print(f"   Calculating tariffs for {vessel_info.get('name', 'Unknown')} at {port}")
    MD_PATH = 'src\port_tariff.md'
    # Parse tariff document
    if not os.path.exists(MD_PATH):
        print("\n Parsing tariff document...")
        parse_pdf()
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        document_content = f.read()
    
    # Initialize calculator
    calculator = SectionRAGCalculator(GEMINI_API_KEY)
    calculator.process_document(document_content) 
    
    
    # Calculate tariffs
    print(f"\n Calculating tariffs...")
    results = calculator.calculate_tariffs(vessel_info)
    
    return results

def format_output(results: Dict[str, Any], vessel_info: Dict[str, Any]) -> str:
    # Results format display
    
    output = []
    output.append("=" * 80)
    output.append(" PORT TARIFF CALCULATION RESULTS")
    output.append("=" * 80)
    output.append(f"Vessel: {vessel_info.get('name', 'Unknown')}")
    output.append(f"Port: {vessel_info.get('port', 'Unknown')}")
    output.append(f"Gross Tonnage: {vessel_info.get('gross_tonnage', 0):,} GT")
    output.append("-" * 80)
    
    # Individual tariffs
    fee_names = {
        'light_dues': 'Light Dues',
        'port_dues': 'Port Dues',
        'vts_charges': 'VTS Charges',
        'pilotage': 'Pilotage',
        'towage': 'Towage',
        'berthing_services': 'Berthing Services',
        'running_of_vessel_lines_dues': 'Running of Vessel Lines Dues'
    }
    
    total_amount = 0
    for fee_type, display_name in fee_names.items():
        if fee_type in results:
            amount = results[fee_type].get('amount', 0)
            total_amount += amount
            output.append(f"{display_name:<30} | R {amount:>12,.2f}")
    
    output.append("-" * 80)
    output.append(f"{'TOTAL TARIFFS':<30} | R {total_amount:>12,.2f}")
    output.append("=" * 80)
    
    # Summary
    summary = results.get('summary', {})
    success_rate = summary.get('success_rate', 0)
    successful = summary.get('successful_calculations', 0)
    total_calcs = summary.get('total_calculations', 0)
    
    output.append(f" Success Rate: {success_rate:.1f}% ({successful}/{total_calcs})")
    output.append(f" Total Amount: R{total_amount:,.2f}")
    output.append("=" * 80)
    
    return "\n".join(output)

def main():
    """Main function for command line usage"""
    
    parser = argparse.ArgumentParser(description='Calculate port tariffs for vessels')
    parser.add_argument('--vessel-file', type=str, help='JSON file containing vessel information')
    parser.add_argument('--port', type=str, default='Durban', 
                       choices=['Durban', 'Saldanha', "Richard's Bay"],
                       help='Port name (default: Durban)')
    parser.add_argument('--output', type=str, help='Output file for results (optional)')
    
    args = parser.parse_args()
    
    # Default vessel info if no file provided
    if args.vessel_file:
        try:
            with open(args.vessel_file, 'r') as f:
                vessel_info = json.load(f)
        except FileNotFoundError:
            print(f" Error: Vessel file '{args.vessel_file}' not found")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in vessel file '{args.vessel_file}'")
            sys.exit(1)
    else:
        # Use default test vessel
        vessel_info = {
            "name": "SUDESTADA",
            "gross_tonnage": 51300,
            "dead_weight_tonnage": 93274,
            "total_length": 229.2,
            "operations": 2,
            "vessel_type": "Bulk Carrier",
            "flag": "Malta",
            "port":"Durban",
            "Days Alongside": "3.39 days"
        }
        print("ℹ️  Using default test vessel (SUDESTADA). Use --vessel-file to specify custom vessel.")
    
    try:
        # Calculate tariffs
        results = calculate_tariffs(vessel_info, args.port)
        
        # Format and display results
        output_text = format_output(results, vessel_info)
        print(f"\n{output_text}")
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_text)
            print(f"\n Results saved to: {args.output}")
        
        # Also save JSON results
        json_output = {
            'vessel_info': vessel_info,
            'tariff_results': results,
            'total_amount': sum(results[fee].get('amount', 0) for fee in results if fee != 'summary')
        }
        
        json_filename = f"tariff_results_{vessel_info.get('name', 'vessel').replace(' ', '_').lower()}.json"
        with open(json_filename, 'w') as f:
            json.dump(json_output, f, indent=2)
        print(f" JSON results saved to: {json_filename}")
        
    except Exception as e:
        print(f" Error calculating tariffs: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

