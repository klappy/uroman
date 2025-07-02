"""Core romanization service - platform agnostic"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Union


class RomanizerService:
    """Platform-agnostic romanization service"""
    
    def __init__(self, uroman_path: Optional[Union[str, Path]] = None):
        self._uroman = None
        if uroman_path:
            self._uroman_path = Path(uroman_path) if isinstance(uroman_path, str) else uroman_path
        else:
            self._uroman_path = Path(__file__).parent.parent.parent / "uroman"
        
    def _initialize(self):
        """Lazy initialization of uroman"""
        if self._uroman is None:
            # Add uroman to path if needed
            uroman_parent = str(self._uroman_path.parent)
            if uroman_parent not in sys.path:
                sys.path.insert(0, uroman_parent)
            
            from uroman.uroman import Uroman
            self._uroman = Uroman()
            
    def romanize(self, text: str, lang_code: Optional[str] = None) -> str:
        """Romanize a single text"""
        self._initialize()
        return self._uroman.romanize_string(text, lang_code)
    
    def romanize_batch(self, texts: List[str], lang_code: Optional[str] = None) -> List[str]:
        """Romanize multiple texts"""
        self._initialize()
        return [self._uroman.romanize_string(text, lang_code) for text in texts]
    
    def get_info(self) -> Dict[str, Any]:
        """Get service information"""
        self._initialize()
        return {
            "service": "uroman",
            "version": getattr(self._uroman, '__version__', 'unknown'),
            "description": "Universal Romanizer - converts any script to Latin alphabet"
        }
