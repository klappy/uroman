#!/usr/bin/env python3
"""
Integration tests for uroman package
Tests various scripts, languages, and edge cases
"""

import json
import os
import pytest
import sys
import tempfile
from pathlib import Path
import uroman as ur


class TestUromanIntegration:
    """Integration tests for the Uroman romanizer"""
    
    @classmethod
    def setup_class(cls):
        """Initialize uroman instance once for all tests"""
        cls.uroman = ur.Uroman()
    
    def test_basic_romanization_strings(self):
        """Test basic romanization across different scripts"""
        test_cases = [
            # (input, expected_output, language_code)
            ("Игорь Стравинский", "Igor Stravinsky", None),  # Russian
            ("Νεπάλ", "Nepal", "ell"),  # Greek
            ("नेपाल", "nepaal", "hin"),  # Hindi
            ("نیپال", "nipal", "urd"),  # Urdu
            ("三万一", "31000", None),  # Chinese numbers
            ("ایران", "iran", "fas"),  # Persian - corrected
            ("مصر", "msr", "ara"),  # Arabic
            ("ประเทศไทย", "prathetthai", "tha"),  # Thai
            ("日本", "riben", None),  # Japanese (Kanji as Chinese)
            ("한국", "hangug", "kor"),  # Korean
        ]
        
        for input_text, expected, lcode in test_cases:
            result = self.uroman.romanize_string(input_text, lcode=lcode)
            assert result == expected, f"Failed for {input_text}: expected {expected}, got {result}"
    
    def test_mixed_scripts(self):
        """Test romanization of text with mixed scripts"""
        mixed_text = "Hello мир 世界 नमस्ते"
        result = self.uroman.romanize_string(mixed_text)
        assert "Hello" in result
        assert "mir" in result
        assert "shijie" in result
        assert "namaste" in result
    
    def test_numbers_in_various_scripts(self):
        """Test number conversion from various scripts"""
        test_cases = [
            ("၁၂၃", "123"),  # Myanmar
            ("١٢٣", "123"),  # Arabic-Indic
            ("૧૨૩", "123"),  # Gujarati
            ("๑๒๓", "123"),  # Thai
            ("໑໒໓", "123"),  # Lao
        ]
        
        for input_num, expected in test_cases:
            result = self.uroman.romanize_string(input_num)
            assert result == expected, f"Failed for {input_num}: expected {expected}, got {result}"
    
    def test_edge_format_output(self):
        """Test edge format output with offset information"""
        text = "Привет"
        result = self.uroman.romanize_string(text, rom_format=ur.RomFormat.EDGES)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check that edges have proper structure
        for edge in result:
            assert hasattr(edge, 'start')
            assert hasattr(edge, 'end')
            edge_str = str(edge)
            assert len(edge_str) > 0
    
    def test_lattice_format_output(self):
        """Test lattice format output"""
        text = "مرحبا"
        result = self.uroman.romanize_string(text, rom_format=ur.RomFormat.LATTICE)
        
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_file_romanization(self):
        """Test file-based romanization"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as input_file:
            input_file.write("Здравствуйте\n")
            input_file.write("こんにちは\n")
            input_file.write("مرحبا\n")
            input_filename = input_file.name
        
        with tempfile.NamedTemporaryFile(mode='r', encoding='utf-8', delete=False) as output_file:
            output_filename = output_file.name
        
        try:
            self.uroman.romanize_file(
                input_filename=input_filename,
                output_filename=output_filename
            )
            
            with open(output_filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            assert len(lines) == 3
            assert "Zdravstvuite" in lines[0]
            assert "konnichiha" in lines[1]
            assert "mrhba" in lines[2]
        finally:
            os.unlink(input_filename)
            os.unlink(output_filename)
    
    def test_special_characters_and_punctuation(self):
        """Test handling of special characters and punctuation"""
        test_cases = [
            ("Hello, world!", "Hello, world!"),
            ("«Привет»", "«Privet»"),
            ("¿Cómo estás?", "Como estas?"),  # Inverted question mark is removed
            ("100%", "100%"),
            ("€100", "€100"),
        ]
        
        for input_text, expected in test_cases:
            result = self.uroman.romanize_string(input_text)
            assert result == expected, f"Failed for {input_text}: expected {expected}, got {result}"
    
    def test_empty_and_edge_cases(self):
        """Test edge cases like empty strings"""
        assert self.uroman.romanize_string("") == ""
        assert self.uroman.romanize_string(" ") == " "
        assert self.uroman.romanize_string("\n") == "\n"
    
    def test_unicode_escape_decoding(self):
        """Test Unicode escape sequence handling"""
        escaped = r"\u03C0\u03B9"
        decoded = ur.Uroman.decode_unicode_escapes(escaped)
        result = self.uroman.romanize_string(decoded)
        assert result == "pi"
    
    def test_language_specific_romanization(self):
        """Test language-specific romanization rules"""
        text_ukr = "Київ"
        text_rus = "Киев"
        
        result_ukr = self.uroman.romanize_string(text_ukr, lcode='ukr')
        result_rus = self.uroman.romanize_string(text_rus, lcode='rus')
        
        assert len(result_ukr) > 0
        assert len(result_rus) > 0
    
    def test_caching_performance(self):
        """Test that caching improves performance for repeated strings"""
        import time
        
        self.uroman.reset_cache()
        
        test_string = "Это тестовая строка для проверки кэширования"
        
        # First call (not cached)
        start = time.time()
        result1 = self.uroman.romanize_string(test_string)
        time1 = time.time() - start
        
        # Second call (should be cached)
        start = time.time()
        result2 = self.uroman.romanize_string(test_string)
        time2 = time.time() - start
        
        assert result1 == result2
        # Cache should make it faster
        assert time2 < time1 * 0.5 or time2 < 0.001
    
    def test_braille_romanization(self):
        """Test Braille script romanization"""
        braille_hello = "⠓⠑⠇⠇⠕"
        result = self.uroman.romanize_string(braille_hello)
        assert result == "hello"
    
    def test_json_output_format(self):
        """Test JSON output for edge format"""
        text = "Тест"
        result = self.uroman.romanize_string(text, rom_format=ur.RomFormat.EDGES)
        
        # The edges have a json() method that returns a list
        json_data = []
        for edge in result:
            if hasattr(edge, 'json'):
                # The json() method returns a JSON array [start, end, text, annotation]
                json_str = edge.json()
                parsed = json.loads(json_str)
                assert isinstance(parsed, list)
                assert len(parsed) >= 3
                json_data.append(parsed)
        
        assert len(json_data) > 0


class TestUromanCLI:
    """Test command-line interface"""
    
    def test_cli_basic(self):
        """Test basic CLI functionality"""
        import subprocess
        
        result = subprocess.run(
            ["python3", "-m", "uroman", "Привет"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Privet" in result.stdout
    
    def test_cli_with_language_code(self):
        """Test CLI with language code"""
        import subprocess
        
        result = subprocess.run(
            ["python3", "-m", "uroman", "Київ", "-l", "ukr"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert len(result.stdout.strip()) > 0
    
    def test_cli_help(self):
        """Test CLI help"""
        import subprocess
        
        result = subprocess.run(
            ["python3", "-m", "uroman", "-h"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
        assert "--lcode" in result.stdout or "-l" in result.stdout


class TestUromanServerlessReady:
    """Test that uroman is ready for serverless deployment"""
    
    def test_import_time(self):
        """Test that uroman can be imported reasonably quickly"""
        import time
        import importlib
        
        # Clear any cached imports
        if 'uroman' in sys.modules:
            del sys.modules['uroman']
        
        start = time.time()
        importlib.import_module('uroman')
        import_time = time.time() - start
        
        # Should import in under 5 seconds
        assert import_time < 5.0, f"Import took {import_time} seconds"
    
    def test_initialization_time(self):
        """Test that Uroman instance can be created reasonably quickly"""
        import time
        
        start = time.time()
        uroman_instance = ur.Uroman()
        init_time = time.time() - start
        
        # Should initialize in under 10 seconds
        assert init_time < 10.0, f"Initialization took {init_time} seconds"
    
    def test_memory_usage(self):
        """Test that uroman doesn't use excessive memory"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Get memory before creating instance
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create instance and romanize some text
        uroman_instance = ur.Uroman()
        for _ in range(100):
            uroman_instance.romanize_string("Тестовая строка для проверки памяти")
        
        # Get memory after
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_increase = mem_after - mem_before
        
        # Should not increase memory by more than 500MB
        assert mem_increase < 500, f"Memory increased by {mem_increase} MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
