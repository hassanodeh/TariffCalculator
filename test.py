"""
Port Tariff Calculator - Test Suite
===================================

Comprehensive test suite that validates the system functionality and accuracy.
This is the ONLY file that performs accuracy checking against ground truth values.
"""

import os
import sys
import json
import logging
from typing import Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.pdf_parser import PDFParser
from src.calculation_engine import CalculationEngine, VesselData

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ground truth values for SUDESTADA vessel
GROUND_TRUTH = {
    "light_dues": 60062.04,
    "port_dues": 199549.22,
    "vts_dues": 33315.75,
    "pilotage_dues": 47189.94,
    "towage_dues": 147074.38,
    "vessel_lines_dues": 19639.50
}

TOTAL_GROUND_TRUTH = sum(GROUND_TRUTH.values())

def check_prerequisites() -> bool:
    """Check if all prerequisites are met"""
    print("Checking prerequisites...")
    
    # Check if PDF file exists
    pdf_path = "data/port_tariff_document.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        print("Please ensure the tariff PDF document is in the data/ directory")
        return False
    
    print(f"✅ PDF file found: {pdf_path}")
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key: export GEMINI_API_KEY=your_key_here")
        return False
    
    print("✅ API key found")
    
    # Check dependencies
    try:
        import fitz
        import google.generativeai
        print("✅ All dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False
    
    return True

def test_pdf_parsing(api_key: str) -> Dict[str, Any]:
    """Test PDF parsing functionality"""
    print("\n" + "="*50)
    print("TESTING PDF PARSING")
    print("="*50)
    
    pdf_path = "data/port_tariff_document.pdf"
    parser = PDFParser(api_key)
    
    print("Parsing PDF document...")
    results = parser.parse_pdf(pdf_path)
    
    if "error" in results:
        print(f"❌ PDF parsing failed: {results['error']}")
        return results
    
    print(f"✅ PDF parsing successful")
    print(f"   Numbers found: {results['total_numbers_found']}")
    print(f"   Tariff types with methodologies: {len(results['methodologies'])}")
    
    # Check if methodologies were extracted for each tariff type
    expected_tariffs = ["light_dues", "port_dues", "vts_dues", "pilotage_dues", "towage_dues", "vessel_lines_dues"]
    
    for tariff in expected_tariffs:
        if tariff in results['methodologies']:
            methodology = results['methodologies'][tariff]
            rates_count = len(methodology.get('rates', []))
            print(f"   {tariff}: {rates_count} rates found")
        else:
            print(f"   {tariff}: No methodology found")
    
    return results

def test_calculation_engine(api_key: str, methodologies: Dict[str, Any]) -> Dict[str, Any]:
    """Test calculation engine functionality"""
    print("\n" + "="*50)
    print("TESTING CALCULATION ENGINE")
    print("="*50)
    
    # Define test vessel (SUDESTADA)
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
    
    print(f"Calculating tariffs for vessel: {vessel.name}")
    
    engine = CalculationEngine(api_key)
    results = engine.calculate_all_tariffs(vessel, methodologies)
    
    print(f"✅ Calculation completed")
    print(f"   Total amount: ZAR {results['total_amount']:,.2f}")
    print(f"   Successful calculations: {results['calculation_summary']['successful_calculations']}/6")
    
    return results

def calculate_accuracy(calculated: float, expected: float) -> float:
    """Calculate accuracy percentage between calculated and expected values"""
    if expected == 0:
        return 100.0 if calculated == 0 else 0.0
    
    accuracy = (1 - abs(calculated - expected) / expected) * 100
    return max(0.0, accuracy)

def test_accuracy(calculation_results: Dict[str, Any]) -> Dict[str, Any]:
    """Test accuracy against ground truth values"""
    print("\n" + "="*50)
    print("TESTING ACCURACY AGAINST GROUND TRUTH")
    print("="*50)
    
    accuracy_results = {}
    total_calculated = calculation_results['total_amount']
    
    print(f"Ground Truth Total: ZAR {TOTAL_GROUND_TRUTH:,.2f}")
    print(f"Calculated Total:   ZAR {total_calculated:,.2f}")
    print(f"Difference:         ZAR {abs(total_calculated - TOTAL_GROUND_TRUTH):,.2f}")
    
    overall_accuracy = calculate_accuracy(total_calculated, TOTAL_GROUND_TRUTH)
    print(f"Overall Accuracy:   {overall_accuracy:.1f}%")
    
    print("\nIndividual Tariff Accuracy:")
    print("-" * 60)
    
    individual_accuracies = []
    
    for tariff_type, expected_amount in GROUND_TRUTH.items():
        calculated_amount = calculation_results['individual_tariffs'][tariff_type]['amount']
        accuracy = calculate_accuracy(calculated_amount, expected_amount)
        individual_accuracies.append(accuracy)
        
        status = "✅" if accuracy >= 95 else "⚠️" if accuracy >= 80 else "❌"
        
        print(f"{status} {tariff_type.replace('_', ' ').title():<20}")
        print(f"   Expected:   ZAR {expected_amount:>10,.2f}")
        print(f"   Calculated: ZAR {calculated_amount:>10,.2f}")
        print(f"   Accuracy:   {accuracy:>10.1f}%")
        print()
        
        accuracy_results[tariff_type] = {
            "expected": expected_amount,
            "calculated": calculated_amount,
            "accuracy": accuracy
        }
    
    # Summary statistics
    high_accuracy_count = len([a for a in individual_accuracies if a >= 95])
    medium_accuracy_count = len([a for a in individual_accuracies if 80 <= a < 95])
    low_accuracy_count = len([a for a in individual_accuracies if a < 80])
    
    print("Accuracy Summary:")
    print(f"  High accuracy (≥95%):     {high_accuracy_count}/6 tariffs")
    print(f"  Medium accuracy (80-95%): {medium_accuracy_count}/6 tariffs")
    print(f"  Low accuracy (<80%):      {low_accuracy_count}/6 tariffs")
    
    accuracy_results['summary'] = {
        "overall_accuracy": overall_accuracy,
        "high_accuracy_count": high_accuracy_count,
        "medium_accuracy_count": medium_accuracy_count,
        "low_accuracy_count": low_accuracy_count,
        "average_individual_accuracy": sum(individual_accuracies) / len(individual_accuracies)
    }
    
    return accuracy_results

def run_full_test_suite():
    """Run the complete test suite"""
    print("PORT TARIFF CALCULATOR - TEST SUITE")
    print("="*60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        return False
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    
    try:
        # Test PDF parsing
        pdf_results = test_pdf_parsing(api_key)
        if "error" in pdf_results:
            print("\n❌ PDF parsing failed. Cannot continue with tests.")
            return False
        
        # Test calculation engine
        calculation_results = test_calculation_engine(api_key, pdf_results['methodologies'])
        
        # Test accuracy
        accuracy_results = test_accuracy(calculation_results)
        
        # Save test results
        test_results = {
            "pdf_extraction": pdf_results,
            "calculations": calculation_results,
            "accuracy": accuracy_results,
            "ground_truth": GROUND_TRUTH
        }
        
        with open("test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)
        
        print(f"\n✅ Test results saved to test_results.json")
        
        # Final assessment
        overall_accuracy = accuracy_results['summary']['overall_accuracy']
        high_accuracy_count = accuracy_results['summary']['high_accuracy_count']
        
        print("\n" + "="*60)
        print("FINAL TEST ASSESSMENT")
        print("="*60)
        
        if overall_accuracy >= 95 and high_accuracy_count >= 4:
            print("🎉 EXCELLENT: System performing at production level")
        elif overall_accuracy >= 80 and high_accuracy_count >= 3:
            print("✅ GOOD: System performing well with room for improvement")
        elif overall_accuracy >= 60:
            print("⚠️ FAIR: System functional but needs significant improvement")
        else:
            print("❌ POOR: System needs major improvements")
        
        print(f"Overall Accuracy: {overall_accuracy:.1f}%")
        print(f"High Accuracy Tariffs: {high_accuracy_count}/6")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        logger.exception("Test suite error")
        return False

def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Port Tariff Calculator Test Suite")
        print("Usage: python test.py")
        print("\nThis test validates the system against ground truth values:")
        for tariff, amount in GROUND_TRUTH.items():
            print(f"  {tariff.replace('_', ' ').title()}: ZAR {amount:,.2f}")
        print(f"  Total: ZAR {TOTAL_GROUND_TRUTH:,.2f}")
        return
    
    success = run_full_test_suite()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

