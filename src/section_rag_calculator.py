
import logging
import re
import google.generativeai as genai
from typing import Dict, Any, List
from .section_rag_retriever import SectionRAGRetriever

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SectionRAGCalculator:
    """Section-based RAG tariff calculator using individual fee-specific prompts. Calculating one fee at a time"""
    
    def __init__(self, gemini_api_key: str):
        """Initialize Section RAG calculator"""
        
        # Initialize Gemini
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Initialize Section RAG retriever
        self.rag_retriever = SectionRAGRetriever()
        
        logger.info("Section RAG Calculator initialized")
    
    def process_document(self, document_content: str):
        """Process document for section RAG"""
        
        logger.info(f" Processing document for Section RAG: {len(document_content):,} characters")
        
        # Process document into sections
        self.rag_retriever.process_document(document_content)
        
        logger.info("Document processed for Section RAG")
    
    def calculate_tariffs(self, vessel_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate all tariff fees using section-based RAG"""
        
        logger.info(f" Calculating tariffs with Section RAG for vessel: {vessel_info['name']}")
        
        # Define fee types to calculate
        fee_types = [
            'light_dues',
            'port_dues', 
            'vts_charges',
            'pilotage',
            'towage',
            'berthing_services',
            'running_of_vessel_lines_dues'
        ]
        
        results = {}
        total_amount = 0.0
        successful_calculations = 0
        
        for fee_type in fee_types:
            try:
                # Get most relevant section using semantic search
                relevant_content = self.rag_retriever.retrieve_relevant_sections(fee_type, vessel_info)
                
                # Calculate fee using the relevant section
                amount = self.calculate_fee(fee_type, vessel_info, relevant_content)
                
                results[fee_type] = {
                    'amount': amount,
                    'method': 'section_rag',
                    'content_length': len(relevant_content)
                }
                
                total_amount += amount
                successful_calculations += 1
                
                logger.info(f"{fee_type}: R{amount:,.2f} (Section RAG)")
                
            except Exception as e:
                logger.error(f"Failed to calculate {fee_type}: {str(e)}")
                results[fee_type] = {
                    'amount': 0.0,
                    'method': 'section_rag',
                    'error': str(e)
                }
        
        # Add summary for checking
        results['summary'] = {
            'total_amount': total_amount,
            'successful_calculations': successful_calculations,
            'total_calculations': len(fee_types),
            'success_rate': (successful_calculations / len(fee_types)) * 100,
            'method': 'section_rag'
        }
        
        logger.info(f"\\nSection RAG Summary:")
        logger.info(f"   Total Amount: R{total_amount:,.2f}")
        logger.info(f"   Successful: {successful_calculations}/{len(fee_types)}")

        
        return results
    
    def calculate_fee(self, fee_type: str, vessel_info: Dict[str, Any], relevant_content: str) -> float:
        """Calculate a single fee using the most relevant section"""
        
        # Create fee-specific query
        query = self.create_prompt(fee_type, vessel_info, relevant_content)
        
        # Get response from Gemini
        response = self.model.generate_content(query)
        response_text = response.text
        
        # Extract amount from response
        amount = self._extract_amount(response_text)
        
        if amount is None:
            logger.warning(f"Could not extract amount from response: {response_text[:200]}...")
            return 0.0
        
        return amount


    def create_prompt(self, fee_type: str, vessel_info: str, relevant_content: str) -> str:
        return f"""You are a precise Port Tariff expert. Your goal is to find the exact **{fee_type.replace('_', ' ')}** for vessels. 
            In order to find the exact fee, you need to understand in an extreme depth and apply the following correctly:
            -----------
            {relevant_content}
            -----------
            As formulas are not provided, you need to implement your understanding, the instructions and rates in determining how to exactly find **{fee_type.replace('_', ' ')}**.
            Given the following Vessel data, you need to precisely and accurately calculate **{fee_type.replace('_', ' ')}**:
            {vessel_info}

 
            Do not include VAT and produce the result in the format:
                 Final Amount: R [amount]"""

    
    
    def _extract_amount(self, response_text: str) -> float:
        """Extract final amount from Gemini response"""
        
        # Look for "Final Amount: R[amount]" pattern
        patterns = [
            r'Final Amount:\s*R\s*([\d,]+\.?\d*)',
            r'FINAL AMOUNT:\s*R\s*([\d,]+\.?\d*)',
            r'Total:\s*R\s*([\d,]+\.?\d*)',
            r'Amount:\s*R\s*([\d,]+\.?\d*)',
            r'R\s*([\d,]+\.?\d*)\s*(?:total|final)',
            r'(?:total|final).*?R\s*([\d,]+\.?\d*)',
            r'ZAR\s*([\d,]+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None

