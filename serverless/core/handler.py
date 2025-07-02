"""Platform-agnostic request handler"""

from typing import Dict, Any, Optional, List, Union
from .romanizer_service import RomanizerService


class UromanHandler:
    """Handles romanization requests in a platform-agnostic way"""
    
    def __init__(self, romanizer_service: Optional[RomanizerService] = None):
        self.service = romanizer_service or RomanizerService()
    
    def handle_single(self, text: str, lang_code: Optional[str] = None) -> Dict[str, Any]:
        """Handle single text romanization"""
        if not text:
            return {
                "error": "No text provided",
                "code": "MISSING_TEXT"
            }
        
        try:
            romanized = self.service.romanize(text, lang_code)
            return {
                "original": text,
                "romanized": romanized,
                "lang_code": lang_code
            }
        except Exception as e:
            return {
                "error": str(e),
                "code": "ROMANIZATION_ERROR"
            }
    
    def handle_batch(self, texts: List[str], lang_code: Optional[str] = None) -> Dict[str, Any]:
        """Handle batch romanization"""
        if not texts:
            return {
                "error": "No texts provided",
                "code": "MISSING_TEXTS"
            }
        
        try:
            romanized_texts = self.service.romanize_batch(texts, lang_code)
            return {
                "originals": texts,
                "romanized": romanized_texts,
                "lang_code": lang_code,
                "count": len(texts)
            }
        except Exception as e:
            return {
                "error": str(e),
                "code": "BATCH_ERROR"
            }
    
    def handle_request(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic request - routes to single or batch"""
        # Check for batch request
        if "texts" in body:
            return self.handle_batch(
                texts=body.get("texts", []),
                lang_code=body.get("lang_code")
            )
        # Single text request
        else:
            return self.handle_single(
                text=body.get("text", ""),
                lang_code=body.get("lang_code")
            )
    
    def handle_info(self) -> Dict[str, Any]:
        """Handle info/health check request"""
        return self.service.get_info()
