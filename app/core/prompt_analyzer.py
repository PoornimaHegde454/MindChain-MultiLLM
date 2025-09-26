"""
Prompt analysis engine for domain classification and complexity scoring
"""

import re
import logging
from typing import Dict, List, Optional
from app.core.enums import Domain, Complexity

logger = logging.getLogger(__name__)

class PromptAnalyzer:
    """Analyzes prompts to determine domain, complexity, and requirements"""
    
    def __init__(self):
        # Keywords for domain classification
        self.domain_keywords = {
            Domain.CODING: [
                "function", "class", "def", "import", "return", "python", "javascript",
                "code", "programming", "algorithm", "debug", "error", "syntax",
                "variable", "loop", "if", "else", "try", "except", "api", "database"
            ],
            Domain.CREATIVE: [
                "story", "poem", "creative", "write", "narrative", "character",
                "plot", "dialogue", "fiction", "imagine", "describe", "scene",
                "chapter", "book", "novel", "script", "screenplay"
            ],
            Domain.TECHNICAL: [
                "analyze", "explain", "technical", "architecture", "system",
                "performance", "optimization", "scalability", "security",
                "design", "pattern", "framework", "methodology", "best practice"
            ]
        }
        
        # Complexity indicators
        self.complexity_indicators = {
            Complexity.LOW: [
                "what is", "define", "explain", "simple", "basic", "quick",
                "short", "brief", "yes/no", "true/false"
            ],
            Complexity.HIGH: [
                "analyze", "compare", "evaluate", "complex", "detailed",
                "comprehensive", "thorough", "multiple", "advanced", "sophisticated"
            ]
        }
    
    async def analyze(self, message: str, context: Optional[str] = None) -> Dict:
        """
        Analyze a prompt to determine its characteristics
        
        Args:
            message: The user's prompt
            context: Optional context about the request
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Clean and prepare text
            text = self._clean_text(message)
            if context:
                text += " " + self._clean_text(context)
            
            # Determine domain
            domain = self._classify_domain(text)
            
            # Determine complexity
            complexity = self._assess_complexity(text)
            
            # Estimate response length
            estimated_length = self._estimate_response_length(text, domain, complexity)
            
            # Detect language
            language = self._detect_language(text)
            
            # Determine speed vs quality preference
            speed_priority = self._assess_speed_priority(text)
            
            return {
                "domain": domain.value,
                "complexity": complexity.value,
                "estimated_length": estimated_length,
                "language": language,
                "speed_priority": speed_priority,
                "word_count": len(text.split()),
                "character_count": len(text)
            }
            
        except Exception as e:
            logger.error(f"Prompt analysis error: {str(e)}")
            return {
                "domain": "general",
                "complexity": "medium",
                "estimated_length": "medium",
                "language": "en",
                "speed_priority": "balanced",
                "word_count": len(message.split()),
                "character_count": len(message)
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for analysis"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip().lower())
        return text
    
    def _classify_domain(self, text: str) -> Domain:
        """Classify the domain of the prompt"""
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            domain_scores[domain] = score
        
        # Return domain with highest score, default to general
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            if domain_scores[best_domain] > 0:
                return best_domain
        
        return Domain.GENERAL
    
    def _assess_complexity(self, text: str) -> Complexity:
        """Assess the complexity of the prompt"""
        low_score = sum(1 for indicator in self.complexity_indicators[Complexity.LOW] 
                       if indicator in text)
        high_score = sum(1 for indicator in self.complexity_indicators[Complexity.HIGH] 
                        if indicator in text)
        
        # Additional complexity factors
        word_count = len(text.split())
        question_count = text.count('?')
        instruction_count = len(re.findall(r'\b(create|build|implement|design|analyze)\b', text))
        
        # Calculate complexity score
        complexity_score = (
            high_score * 2 +  # High complexity indicators
            instruction_count +  # Instruction words
            min(question_count, 3) +  # Multiple questions
            (1 if word_count > 50 else 0)  # Long prompts
        ) - low_score  # Subtract low complexity indicators
        
        if complexity_score >= 3:
            return Complexity.HIGH
        elif complexity_score <= 0:
            return Complexity.LOW
        else:
            return Complexity.MEDIUM
    
    def _estimate_response_length(self, text: str, domain: Domain, complexity: Complexity) -> str:
        """Estimate the expected response length"""
        base_length = len(text.split())
        
        # Domain-based adjustments
        domain_multipliers = {
            Domain.CODING: 1.5,
            Domain.CREATIVE: 2.0,
            Domain.TECHNICAL: 1.8,
            Domain.GENERAL: 1.0
        }
        
        # Complexity-based adjustments
        complexity_multipliers = {
            Complexity.LOW: 0.5,
            Complexity.MEDIUM: 1.0,
            Complexity.HIGH: 2.0
        }
        
        estimated_words = int(
            base_length * 
            domain_multipliers.get(domain, 1.0) * 
            complexity_multipliers.get(complexity, 1.0)
        )
        
        if estimated_words < 50:
            return "short"
        elif estimated_words < 200:
            return "medium"
        else:
            return "long"
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection (basic implementation)"""
        # This is a basic implementation - in production, use a proper language detection library
        if any(char in text for char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'):
            return 'ru'
        elif any(char in text for char in 'àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ'):
            return 'fr'
        elif any(char in text for char in 'äöüß'):
            return 'de'
        else:
            return 'en'  # Default to English
    
    def _assess_speed_priority(self, text: str) -> str:
        """Assess if the user prioritizes speed over quality"""
        speed_indicators = ['quick', 'fast', 'urgent', 'asap', 'immediately', 'rush']
        quality_indicators = ['detailed', 'thorough', 'comprehensive', 'accurate', 'precise']
        
        speed_score = sum(1 for indicator in speed_indicators if indicator in text)
        quality_score = sum(1 for indicator in quality_indicators if indicator in text)
        
        if speed_score > quality_score:
            return "speed"
        elif quality_score > speed_score:
            return "quality"
        else:
            return "balanced"
