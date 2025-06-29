import re
import logging
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class SectionRAGRetriever:
    
    def __init__(self):
        """Initialize the retriever with a sentence transformer model."""
        logger.info(" Initializing Section RAG Retriever...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Loaded SentenceTransformer: all-MiniLM-L6-v2")

        self.sections: List[Dict[str, Any]] = []
        self.section_embeddings: np.ndarray = np.array([])

    def process_document(self, content: str) -> None:
        """
        Split the document into two-level numbered subsections
        """
        self.sections = self.chunk_sections(content)

        texts = [sec['content'] for sec in self.sections]
        self.section_embeddings = self.model.encode(texts)

        logger.info(f" Document processed: {len(self.sections)} sections extracted.")

    def retrieve_relevant_sections(self, fee_type: str, vessel_info: Dict[str, Any]) -> str:
        """
        Return the full content of the most relevant two-level section for a given fee type.
        """
        query = self._create_search_query(fee_type)
        q_emb = self.model.encode([query])

        sims = np.dot(q_emb, self.section_embeddings.T)[0]
        best_idx = int(np.argmax(sims))
        best_sec = self.sections[best_idx]

        logger.info(f" Best match for '{fee_type}' -> Section {best_sec['section_number']} ({sims[best_idx]:.3f})")
        return best_sec['content']

    def chunk_sections(self, content: str) -> List[Dict[str, Any]]:
        """
        From a Markdown string, pull out every '## n.n TITLE' block 
        (including anything until the next '## n.n' or end of doc), and return the desired structure:
        """
        sections: List[Dict[str, Any]] = []

        # Find only the top-level subsections (##) with a numeric n.n and ALL-CAPS title
        header_rx = re.compile(r'(?m)^##\s*(\d+\.\d+)\s+(.+)$')

        # Locate all matches
        matches = list(header_rx.finditer(content))
        for idx, m in enumerate(matches):
            start = m.start()
            end = matches[idx+1].start() if idx + 1 < len(matches) else len(content)

            number = m.group(1)
            title  = m.group(2).strip()
            block  = content[start:end].strip()

            sections.append({
                'section_number': number,
                'title': f"{number} {title}",
                'content': block
            })

        return sections

    def _create_search_query(self, fee_type: str) -> str:
        """
        Build a simple keyword-based query for a fee type. Helps locate the correct sections
        """
        keywords = {
            'light_dues': ['light dues'],
            'port_dues': ['port fees on vessels'],
            'vts_charges': ['vts charges'],
            'pilotage': ['pilotage'],
            'towage': ['tug', 'towage'],
            'berthing_services': ['berthing services'],
            'running_of_vessel_lines_dues': ['running of vessel lines','mooring boat']
        }
        terms = keywords.get(fee_type, [fee_type.replace('_', ' ')])
        return ' '.join(terms)

