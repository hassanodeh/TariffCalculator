"""
Port Tariff Calculator - Main Module
====================================

Simple command-line interface for calculating port tariffs from PDF documents.
"""

import sys
import json
import logging
from src.pdf_parser import PDFParser
from src.calculation_engine import CalculationEngine, VesselData

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function to run the port tariff calculator"""
    if len(sys.argv) < 3:
        print("Usage: python main.py <pdf_path> <api_key>")
        print("Example: python main.py tariff_document.pdf your_gemini_api_key")
        return
    
    pdf_path = sys.argv[1]
    api_key = sys.argv[2]
    
    logger.info("Starting Port Tariff Calculator")
    
    # Step 1: Parse PDF to extract methodologies
    logger.info("Step 1: Parsing PDF document...")
    parser = PDFParser(api_key)
    pdf_results = parser.parse_pdf(pdf_path)
    
    if "error" in pdf_results:
        logger.error(f"PDF parsing failed: {pdf_results['error']}")
        return
    
    logger.info(f"Found {pdf_results['total_numbers_found']} numbers in PDF")
    logger.info(f"Extracted methodologies for {len(pdf_results['methodologies'])} tariff types")
    
    # Step 2: Define vessel data (example vessel)
    vessel = VesselData(
        name="SUDESTADA",
        gt=51300,
        dwt=93274,
        loa=229.2,
        beam=38,
        vessel_type="Bulk Carrier",
        cargo_quantity=40000,
        days_alongside=3.39,
        operations=2,
        port="Durban"
    )
    
    # Step 3: Calculate tariffs
    logger.info("Step 2: Calculating tariffs...")
    engine = CalculationEngine(api_key)
    calculation_results = engine.calculate_all_tariffs(vessel, pdf_results['methodologies'])
    
    # Step 4: Display results
    logger.info("Step 3: Results")
    print("\n" + "="*60)
    print("PORT TARIFF CALCULATION RESULTS")
    print("="*60)
    print(f"Vessel: {calculation_results['vessel_name']}")
    print(f"Total Amount: ZAR {calculation_results['total_amount']:,.2f}")
    print("\nIndividual Tariffs:")
    print("-" * 40)
    
    for tariff_type, details in calculation_results['individual_tariffs'].items():
        tariff_name = tariff_type.replace('_', ' ').title()
        amount = details['amount']
        confidence = details['confidence']
        method = details['calculation_method']
        
        print(f"{tariff_name}: ZAR {amount:,.2f}")
        print(f"  Method: {method}")
        print(f"  Confidence: {confidence:.1%}")
        print()
    
    # Summary statistics
    summary = calculation_results['calculation_summary']
    print(f"Summary: {summary['successful_calculations']}/{summary['total_tariffs']} tariffs calculated")
    print(f"Average Confidence: {summary['average_confidence']:.1%}")
    
    # Save results to file
    output_file = "calculation_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "pdf_extraction": pdf_results,
            "calculations": calculation_results
        }, f, indent=2)
    
    logger.info(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()

