"""
LegalGuardian AI — Interactive Q&A Model

Provides extractive question answering over contract text using
a pre-trained transformer model. Falls back to keyword search
if the transformer model is not available.
"""

import re
from typing import Dict, List, Optional


class QAModel:
    """
    Answers user questions about contract content.
    
    Primary: Transformer-based extractive QA (deepset/roberta-base-squad2)
    Fallback: Keyword-based search and extraction
    """
    
    def __init__(self, model_name: str = "deepset/roberta-base-squad2"):
        self.model_name = model_name
        self.pipeline = None
        self._model_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Attempt to load the QA model."""
        try:
            from transformers import pipeline
            self.pipeline = pipeline(
                "question-answering",
                model=self.model_name,
                tokenizer=self.model_name,
                device=-1  # CPU
            )
            self._model_loaded = True
            print(f"✅ Loaded QA model: {self.model_name}")
        except Exception as e:
            print(f"⚠️ Could not load QA model: {e}")
            print("   Falling back to keyword-based search")
            self._model_loaded = False
    
    def answer(self, question: str, context: str) -> Dict:
        """
        Answer a question about the contract.
        
        Args:
            question: User's question
            context: Contract text (or relevant section)
        
        Returns:
            Dict with 'answer', 'confidence', 'start', 'end', 'method'
        """
        if self._model_loaded:
            return self._answer_transformer(question, context)
        return self._answer_keyword(question, context)
    
    def _answer_transformer(self, question: str, context: str) -> Dict:
        """Use transformer-based QA model."""
        try:
            # Handle long contexts by chunking
            max_context_length = 4000  # Characters, not tokens
            
            if len(context) <= max_context_length:
                result = self.pipeline(question=question, context=context)
                return {
                    "answer": result["answer"],
                    "confidence": round(result["score"], 3),
                    "start": result["start"],
                    "end": result["end"],
                    "method": "transformer",
                    "context_snippet": self._get_surrounding_context(
                        context, result["start"], result["end"]
                    )
                }
            
            # Chunk the context for long documents
            chunks = self._chunk_context(context, max_context_length)
            best_result = None
            best_score = -1
            
            for chunk_start, chunk_text in chunks:
                try:
                    result = self.pipeline(question=question, context=chunk_text)
                    if result["score"] > best_score:
                        best_score = result["score"]
                        best_result = {
                            "answer": result["answer"],
                            "confidence": round(result["score"], 3),
                            "start": chunk_start + result["start"],
                            "end": chunk_start + result["end"],
                            "method": "transformer",
                            "context_snippet": self._get_surrounding_context(
                                chunk_text, result["start"], result["end"]
                            )
                        }
                except Exception:
                    continue
            
            if best_result:
                return best_result
            
            return self._answer_keyword(question, context)
            
        except Exception as e:
            print(f"⚠️ Transformer QA failed: {e}")
            return self._answer_keyword(question, context)
    
    def _answer_keyword(self, question: str, context: str) -> Dict:
        """Keyword-based fallback answer extraction."""
        question_lower = question.lower()
        
        # Extract key terms from the question
        # Remove common question words
        stop_words = {
            "what", "when", "where", "who", "how", "why", "does", "do",
            "is", "are", "was", "were", "will", "would", "can", "could",
            "should", "shall", "the", "a", "an", "in", "on", "at", "to",
            "for", "of", "with", "by", "if", "i", "my", "me", "this",
            "that", "it", "happen", "happens", "about", "tell"
        }
        
        keywords = [
            word.strip("?.,!") for word in question_lower.split()
            if word.strip("?.,!") not in stop_words and len(word.strip("?.,!")) > 2
        ]
        
        if not keywords:
            return {
                "answer": "I couldn't find a specific answer. Please try rephrasing your question.",
                "confidence": 0.0,
                "start": 0,
                "end": 0,
                "method": "keyword",
                "context_snippet": ""
            }
        
        # Score each sentence by keyword overlap
        sentences = re.split(r'(?<=[.!?])\s+', context)
        scored_sentences = []
        
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            score = sum(1 for kw in keywords if kw in sentence_lower)
            if score > 0:
                scored_sentences.append((score, i, sentence))
        
        if not scored_sentences:
            return {
                "answer": "I couldn't find relevant information about that in the contract. Please try a different question.",
                "confidence": 0.1,
                "start": 0,
                "end": 0,
                "method": "keyword",
                "context_snippet": ""
            }
        
        # Sort by score and return best match(es)
        scored_sentences.sort(reverse=True)
        
        # Take top 1-3 sentences
        top_sentences = scored_sentences[:3]
        # Sort by position for natural reading order
        top_sentences.sort(key=lambda x: x[1])
        
        answer = " ".join([s[2] for s in top_sentences])
        confidence = min(0.7, 0.2 + (top_sentences[0][0] / len(keywords)) * 0.5)
        
        return {
            "answer": answer.strip(),
            "confidence": round(confidence, 3),
            "start": 0,
            "end": 0,
            "method": "keyword",
            "context_snippet": answer.strip()
        }
    
    def _chunk_context(self, context: str, max_length: int) -> List[tuple]:
        """Split context into overlapping chunks."""
        chunks = []
        overlap = 500  # Character overlap between chunks
        start = 0
        
        while start < len(context):
            end = start + max_length
            chunk = context[start:end]
            chunks.append((start, chunk))
            start += max_length - overlap
        
        return chunks
    
    def _get_surrounding_context(self, text: str, start: int, end: int, 
                                  window: int = 200) -> str:
        """Get surrounding context around the answer span."""
        ctx_start = max(0, start - window)
        ctx_end = min(len(text), end + window)
        snippet = text[ctx_start:ctx_end]
        
        if ctx_start > 0:
            snippet = "..." + snippet
        if ctx_end < len(text):
            snippet = snippet + "..."
        
        return snippet


# Module-level instance
_qa_instance = None

def get_qa_model(model_name: str = "deepset/roberta-base-squad2") -> QAModel:
    """Get or create the QA model singleton."""
    global _qa_instance
    if _qa_instance is None:
        _qa_instance = QAModel(model_name)
    return _qa_instance
