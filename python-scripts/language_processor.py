#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Centralized Language Processing Module
Optimized for multilingual support, intent classification, and entity extraction
"""

import re
import json
import hashlib
import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import unicodedata


class Language(Enum):
    """Supported languages"""
    SPANISH = "es"
    ENGLISH = "en"
    PORTUGUESE = "pt"
    UNKNOWN = "unknown"


class Intent(Enum):
    """Intent types"""
    SALUDO = "saludo"
    DESPEDIDA = "despedida"
    COTIZACION = "cotizacion"
    INFORMACION = "informacion"
    PREGUNTA = "pregunta"
    PRODUCTO = "producto"
    INSTALACION = "instalacion"
    SERVICIO = "servicio"
    OBJECION = "objecion"
    GENERAL = "general"
    ERROR = "error"


@dataclass
class ProcessedMessage:
    """Result of language processing"""
    original: str
    normalized: str
    language: Language
    intent: Intent
    entities: Dict[str, Any]
    confidence: float
    timestamp: datetime.datetime
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class Entity:
    """Extracted entity"""
    type: str
    value: Any
    confidence: float
    start_pos: int
    end_pos: int


class TextNormalizer:
    """Normalize text for processing"""
    
    def __init__(self):
        self.abbreviations = {
            'm2': 'metros cuadrados',
            'm²': 'metros cuadrados',
            'ml': 'metros lineales',
            'mm': 'milimetros',
            'cm': 'centimetros',
            'm': 'metros',
            'q': 'que',
            'x': 'por',
            'xq': 'porque',
            'pq': 'porque',
            'tb': 'tambien',
            'tmb': 'tambien',
            'd': 'de',
            'k': 'que',
        }
    
    def normalize(self, text: str, language: Language = Language.SPANISH) -> str:
        """Normalize text"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove accents (for better matching)
        text = self._remove_accents(text)
        
        # Expand abbreviations
        text = self._expand_abbreviations(text)
        
        # Normalize numbers
        text = self._normalize_numbers(text)
        
        # Remove special characters (keep alphanumeric, spaces, and basic punctuation)
        text = re.sub(r'[^\w\s\.\,\-\+]', ' ', text)
        
        return text.strip()
    
    def _remove_accents(self, text: str) -> str:
        """Remove accents from text"""
        nfkd = unicodedata.normalize('NFKD', text)
        return ''.join([c for c in nfkd if not unicodedata.combining(c)])
    
    def _expand_abbreviations(self, text: str) -> str:
        """Expand common abbreviations"""
        words = text.split()
        expanded = []
        for word in words:
            if word in self.abbreviations:
                expanded.append(self.abbreviations[word])
            else:
                expanded.append(word)
        return ' '.join(expanded)
    
    def _normalize_numbers(self, text: str) -> str:
        """Normalize number formats"""
        # Convert "10x5" to "10 x 5"
        text = re.sub(r'(\d+)\s*[x×]\s*(\d+)', r'\1 x \2', text)
        # Convert "10m x 5m" to "10 metros x 5 metros"
        text = re.sub(r'(\d+)\s*m\s*[x×]\s*(\d+)\s*m', r'\1 metros x \2 metros', text)
        return text


class LanguageDetector:
    """Detect language of text"""
    
    def __init__(self):
        # Language-specific patterns
        self.patterns = {
            Language.SPANISH: {
                'common_words': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'una', 'está', 'como', 'más', 'pero', 'sus', 'le', 'ha', 'me', 'si', 'sin', 'sobre', 'este', 'entre', 'cuando', 'todo', 'esta', 'ser', 'son', 'dos', 'también', 'fue', 'había', 'era', 'muy', 'años', 'hasta', 'desde', 'está', 'mi', 'porque', 'qué', 'sólo', 'han', 'yo', 'hay', 'vez', 'puede', 'todos', 'así', 'nos', 'ni', 'parte', 'tiene', 'él', 'uno', 'donde', 'bien', 'tiempo', 'mismo', 'ese', 'ahora', 'cada', 'e', 'vida', 'otro', 'después', 'te', 'otros', 'aunque', 'esas', 'esos', 'estas', 'estos', 'estas', 'estos', 'estas', 'estos'],
                'common_endings': ['ción', 'sión', 'dad', 'tad', 'ncia', 'ncia', 'mente', 'mente'],
                'articles': ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas'],
            },
            Language.ENGLISH: {
                'common_words': ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'],
                'common_endings': ['ing', 'ed', 'tion', 'sion', 'ly', 'er', 'est'],
                'articles': ['the', 'a', 'an'],
            },
            Language.PORTUGUESE: {
                'common_words': ['o', 'de', 'a', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'suas', 'numa', 'pelos', 'pelas', 'havia', 'seja', 'qual', 'será', 'nós', 'tenho', 'lhe', 'deles', 'essas', 'esses', 'esses', 'essas', 'esses', 'essas', 'esses'],
                'common_endings': ['ção', 'são', 'ção', 'são', 'dade', 'dade', 'mente', 'mente'],
                'articles': ['o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas'],
            }
        }
    
    def detect(self, text: str) -> Language:
        """Detect language of text"""
        if not text or len(text.strip()) < 3:
            return Language.UNKNOWN
        
        text_lower = text.lower()
        scores = defaultdict(float)
        
        # Pre-tokenize text to ensure word-level matching and avoid substring matches
        # (e.g., avoid counting "the" in "lathe" or "la" in "hola")
        words = set(re.findall(r"\b\w+\b", text_lower, flags=re.UNICODE))
        
        # Score based on common words (word-level matches only)
        for lang, patterns in self.patterns.items():
            for word in patterns['common_words']:
                if word in words:
                    scores[lang] += 1
        
        # Score based on common endings (intentionally using substring matching
        # since we're checking for word suffixes like "ción", "ing", etc.)
        for lang, patterns in self.patterns.items():
            for ending in patterns['common_endings']:
                if ending in text_lower:
                    scores[lang] += 0.5
        
        # Score based on articles
        for lang, patterns in self.patterns.items():
            for article in patterns['articles']:
                if f' {article} ' in f' {text_lower} ':
                    scores[lang] += 0.3
        
        # Return language with highest score
        if scores:
            detected = max(scores.items(), key=lambda x: x[1])[0]
            # Only return if confidence is reasonable
            if scores[detected] > 1.0:
                return detected
        
        # Default to Spanish for Uruguay market
        return Language.SPANISH


class IntentClassifier:
    """Classify user intent"""
    
    def __init__(self):
        # Intent patterns by language
        self.patterns = {
            Language.SPANISH: {
                Intent.SALUDO: ['hola', 'buenos', 'buenas', 'saludos', 'hi', 'hello', 'buen dia', 'buen dia', 'buenas tardes', 'buenas noches'],
                Intent.DESPEDIDA: ['gracias', 'chau', 'adios', 'hasta luego', 'hasta pronto', 'nos vemos', 'bye', 'bye bye', 'hasta la vista'],
                Intent.COTIZACION: ['cotizar', 'precio', 'costo', 'cuanto', 'presupuesto', 'cotizacion', 'cotización', 'presupuesto', 'precio', 'costo', 'cuanto cuesta', 'cuanto sale', 'precio de', 'costo de'],
                Intent.INFORMACION: ['informacion', 'información', 'caracteristicas', 'características', 'especificaciones', 'que es', 'qué es', 'como funciona', 'cómo funciona', 'diferencia', 'ventajas', 'beneficios', 'aplicaciones'],
                Intent.PREGUNTA: ['como', 'cómo', 'cuando', 'cuándo', 'donde', 'dónde', 'por que', 'por qué', 'que', 'qué', 'cual', 'cuál', 'cuanto tiempo', 'cuánto tiempo', 'garantia', 'garantía', 'instalacion', 'instalación', 'flete', 'entrega'],
                Intent.PRODUCTO: ['isodec', 'isoroof', 'isopanel', 'isowall', 'poliestireno', 'lana de roca', 'lana_roca', 'chapa', 'calameria', 'calamería', 'producto', 'productos'],
                Intent.INSTALACION: ['instalar', 'instalacion', 'instalación', 'montaje', 'colocacion', 'colocación', 'armar', 'montar'],
                Intent.SERVICIO: ['servicio', 'garantia', 'garantía', 'soporte', 'atencion', 'atención', 'servicio tecnico', 'servicio técnico'],
                Intent.OBJECION: ['caro', 'costoso', 'no estoy seguro', 'dudar', 'muy caro', 'es caro', 'precio alto', 'no puedo pagar', 'no tengo dinero'],
            },
            Language.ENGLISH: {
                Intent.SALUDO: ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
                Intent.DESPEDIDA: ['thanks', 'thank you', 'bye', 'goodbye', 'see you', 'later'],
                Intent.COTIZACION: ['quote', 'price', 'cost', 'how much', 'estimate', 'quotation', 'pricing'],
                Intent.INFORMACION: ['information', 'info', 'what is', 'how does', 'features', 'specifications', 'characteristics'],
                Intent.PREGUNTA: ['how', 'when', 'where', 'why', 'what', 'which', 'how long', 'warranty', 'installation', 'delivery'],
                Intent.PRODUCTO: ['product', 'products', 'isodec', 'isoroof', 'isopanel', 'isowall'],
                Intent.INSTALACION: ['install', 'installation', 'mount', 'setup'],
                Intent.SERVICIO: ['service', 'warranty', 'support', 'customer service'],
                Intent.OBJECION: ['expensive', 'costly', 'too expensive', 'not sure', 'doubt'],
            },
            Language.PORTUGUESE: {
                Intent.SALUDO: ['ola', 'olá', 'oi', 'bom dia', 'boa tarde', 'boa noite'],
                Intent.DESPEDIDA: ['obrigado', 'obrigada', 'tchau', 'ate logo', 'até logo', 'ate mais', 'até mais'],
                Intent.COTIZACION: ['cotizar', 'preco', 'preço', 'custo', 'quanto', 'orçamento', 'cotação'],
                Intent.INFORMACION: ['informacao', 'informação', 'caracteristicas', 'características', 'especificacoes', 'especificações', 'o que e', 'o que é', 'como funciona'],
                Intent.PREGUNTA: ['como', 'quando', 'onde', 'por que', 'por quê', 'o que', 'qual', 'quanto tempo', 'garantia', 'instalacao', 'instalação', 'entrega'],
                Intent.PRODUCTO: ['produto', 'produtos', 'isodec', 'isoroof', 'isopanel', 'isowall'],
                Intent.INSTALACION: ['instalar', 'instalacao', 'instalação', 'montagem', 'colocacao', 'colocação'],
                Intent.SERVICIO: ['servico', 'serviço', 'garantia', 'suporte', 'atendimento'],
                Intent.OBJECION: ['caro', 'custoso', 'muito caro', 'nao tenho certeza', 'não tenho certeza', 'duvida', 'dúvida'],
            }
        }
    
    def classify(self, text: str, language: Language = Language.SPANISH, context: Optional[Dict[str, Any]] = None) -> Tuple[Intent, float]:
        """Classify intent with confidence score"""
        if not text:
            return Intent.GENERAL, 0.0
        
        text_lower = text.lower()
        scores = defaultdict(float)
        
        # Get patterns for detected language
        lang_patterns = self.patterns.get(language, self.patterns[Language.SPANISH])
        
        # Score each intent
        for intent, keywords in lang_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Longer keywords get higher weight
                    weight = len(keyword) / 10.0
                    scores[intent] += weight
        
        # Boost score based on context
        if context:
            previous_intent = context.get('previous_intent')
            if previous_intent:
                # Continuation of previous intent gets boost
                for intent in scores:
                    if intent.value == previous_intent:
                        scores[intent] *= 1.2
        
        # Return intent with highest score
        if scores:
            best_intent = max(scores.items(), key=lambda x: x[1])[0]
            # Calculate confidence (normalize to 0-1)
            max_score = max(scores.values())
            confidence = min(1.0, max_score / 10.0)  # Normalize
            
            # Only return if confidence is reasonable
            if confidence > 0.3:
                return best_intent, confidence
        
        return Intent.GENERAL, 0.5


class EntityExtractor:
    """Extract entities from text"""
    
    def __init__(self):
        # Product entities
        self.products = {
            'isodec': ['isodec', 'isodac', 'isodak'],
            'isoroof': ['isoroof', 'iso roof', 'iso-roof'],
            'isopanel': ['isopanel', 'iso panel', 'iso-panel'],
            'isowall': ['isowall', 'iso wall', 'iso-wall'],
            'poliestireno': ['poliestireno', 'eps', 'poliestireno expandido'],
            'lana_roca': ['lana de roca', 'lana roca', 'rockwool', 'lana mineral'],
            'chapa': ['chapa', 'chapa galvanizada', 'chapa prepintada'],
            'calameria': ['calameria', 'calamería', 'calameria estructural'],
        }
        
        # Color entities
        self.colors = {
            'blanco': ['blanco', 'white'],
            'gris': ['gris', 'gray', 'grey'],
            'rojo': ['rojo', 'red'],
            'personalizado': ['personalizado', 'custom', 'a medida'],
        }
        
        # Thickness entities
        self.thickness_pattern = re.compile(r'(\d+)\s*(?:mm|milimetros|milímetros)')
        
        # Dimension patterns
        self.dimension_patterns = [
            re.compile(r'(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)'),  # 10x5
            re.compile(r'(\d+(?:\.\d+)?)\s*metros?\s*[x×]\s*(\d+(?:\.\d+)?)\s*metros?'),  # 10 metros x 5 metros
            re.compile(r'(\d+(?:\.\d+)?)\s*m\s*[x×]\s*(\d+(?:\.\d+)?)\s*m'),  # 10m x 5m
            re.compile(r'(\d+(?:\.\d+)?)\s*m(?:2|²)'),  # 50m2, 50m²
            re.compile(r'(\d+(?:\.\d+)?)\s*metros?\s*cuadrados?'),  # 50 metros cuadrados
        ]
        
        # Phone pattern
        self.phone_pattern = re.compile(r'(\+?598\s?)?(\d{2,3}\s?\d{3}\s?\d{3})')
    
    def extract(self, text: str, intent: Intent, language: Language = Language.SPANISH) -> Dict[str, Any]:
        """Extract entities from text"""
        entities = {
            'products': [],
            'dimensions': {},
            'thickness': None,
            'color': None,
            'phone': None,
            'services': {
                'flete': False,
                'instalacion': False,
                'accesorios': False,
            }
        }
        
        text_lower = text.lower()
        
        # Extract products
        for product_id, keywords in self.products.items():
            for keyword in keywords:
                if keyword in text_lower:
                    entities['products'].append({
                        'id': product_id,
                        'name': keyword,
                        'confidence': 0.9
                    })
                    break
        
        # Extract dimensions
        for pattern in self.dimension_patterns:
            match = pattern.search(text)
            if match:
                if len(match.groups()) == 2:
                    entities['dimensions'] = {
                        'largo': float(match.group(1)),
                        'ancho': float(match.group(2)),
                        'confidence': 0.8
                    }
                elif 'm2' in match.group(0) or 'metros cuadrados' in match.group(0):
                    entities['dimensions'] = {
                        'area_m2': float(match.group(1)),
                        'confidence': 0.8
                    }
                break
        
        # Extract thickness
        thickness_match = self.thickness_pattern.search(text)
        if thickness_match:
            entities['thickness'] = {
                'value': thickness_match.group(1) + 'mm',
                'confidence': 0.9
            }
        
        # Extract color
        for color_id, keywords in self.colors.items():
            for keyword in keywords:
                if keyword in text_lower:
                    entities['color'] = {
                        'value': color_id,
                        'confidence': 0.8
                    }
                    break
        
        # Extract phone
        phone_match = self.phone_pattern.search(text)
        if phone_match:
            entities['phone'] = {
                'value': phone_match.group(0).replace(' ', ''),
                'confidence': 0.9
            }
        
        # Extract services
        if 'flete' in text_lower or 'transporte' in text_lower or 'delivery' in text_lower:
            entities['services']['flete'] = True
        if 'instalacion' in text_lower or 'instalación' in text_lower or 'instalacao' in text_lower or 'instalação' in text_lower or 'instalar' in text_lower or 'installation' in text_lower:
            entities['services']['instalacion'] = True
        if 'accesorios' in text_lower or 'accesorios' in text_lower or 'accessories' in text_lower:
            entities['services']['accesorios'] = True
        
        return entities


class CacheManager:
    """Simple in-memory cache for processed messages"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def _get_key(self, text: str) -> str:
        """Generate cache key"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get(self, text: str) -> Optional[ProcessedMessage]:
        """Get cached result"""
        key = self._get_key(text)
        if key in self.cache:
            entry = self.cache[key]
            # Check TTL
            age = (datetime.datetime.now() - entry['timestamp']).total_seconds()
            if age < self.ttl_seconds:
                return entry['result']
            else:
                # Expired, remove
                del self.cache[key]
        return None
    
    def set(self, text: str, result: ProcessedMessage):
        """Cache result"""
        key = self._get_key(text)
        # Evict if cache is full
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'result': result,
            'timestamp': datetime.datetime.now()
        }


class ContextManager:
    """Manage conversation context"""
    
    def __init__(self):
        self.contexts = {}
        self.max_age_seconds = 3600  # 1 hour
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get context for session"""
        if session_id in self.contexts:
            context = self.contexts[session_id]
            # Check if expired
            age = (datetime.datetime.now() - context['last_update']).total_seconds()
            if age < self.max_age_seconds:
                return context['data']
            else:
                # Expired, remove
                del self.contexts[session_id]
        
        # Return empty context
        return {
            'previous_intent': None,
            'previous_entities': {},
            'conversation_history': [],
            'data_collected': {}
        }
    
    def update_context(self, session_id: str, result: ProcessedMessage):
        """Update context with new result"""
        context = self.get_context(session_id)
        context['previous_intent'] = result.intent.value
        context['previous_entities'] = result.entities
        context['conversation_history'].append({
            'timestamp': result.timestamp.isoformat(),
            'intent': result.intent.value,
            'entities': result.entities
        })
        # Keep only last 10 messages
        if len(context['conversation_history']) > 10:
            context['conversation_history'] = context['conversation_history'][-10:]
        
        self.contexts[session_id] = {
            'data': context,
            'last_update': datetime.datetime.now()
        }


class LanguageProcessor:
    """Centralized language processing module"""
    
    def __init__(self, enable_cache: bool = True, enable_context: bool = True):
        self.normalizer = TextNormalizer()
        self.detector = LanguageDetector()
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.cache = CacheManager() if enable_cache else None
        self.context_manager = ContextManager() if enable_context else None
    
    def process_message(self, message: str, session_id: Optional[str] = None) -> ProcessedMessage:
        """Main entry point for language processing"""
        if not message or not message.strip():
            return ProcessedMessage(
                original=message,
                normalized="",
                language=Language.UNKNOWN,
                intent=Intent.ERROR,
                entities={},
                confidence=0.0,
                timestamp=datetime.datetime.now(),
                session_id=session_id
            )
        
        # 1. Detect language
        language = self.detector.detect(message)
        
        # 2. Normalize text
        normalized = self.normalizer.normalize(message, language)
        
        # 3. Check cache
        cached = None
        if self.cache:
            cached = self.cache.get(normalized)
            if cached:
                # Update session_id if provided
                cached.session_id = session_id
                return cached
        
        # 4. Get context
        context = None
        if self.context_manager and session_id:
            context = self.context_manager.get_context(session_id)
        
        # 5. Classify intent
        intent, intent_confidence = self.intent_classifier.classify(normalized, language, context)
        
        # 6. Extract entities
        entities = self.entity_extractor.extract(message, intent, language)  # Use original for entity extraction
        
        # 7. Calculate overall confidence
        confidence = self._calculate_confidence(intent_confidence, entities)
        
        # 8. Build result
        result = ProcessedMessage(
            original=message,
            normalized=normalized,
            language=language,
            intent=intent,
            entities=entities,
            confidence=confidence,
            timestamp=datetime.datetime.now(),
            session_id=session_id,
            context=context
        )
        
        # 9. Cache result
        if self.cache:
            self.cache.set(normalized, result)
        
        # 10. Update context
        if self.context_manager and session_id:
            self.context_manager.update_context(session_id, result)
        
        return result
    
    def _calculate_confidence(self, intent_confidence: float, entities: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        # Base confidence from intent
        confidence = intent_confidence
        
        # Boost if entities found
        entity_count = 0
        if entities.get('products'):
            entity_count += len(entities['products'])
        if entities.get('dimensions'):
            entity_count += 1
        if entities.get('thickness'):
            entity_count += 1
        if entities.get('color'):
            entity_count += 1
        
        # Boost confidence based on entity count (max 0.2 boost)
        entity_boost = min(0.2, entity_count * 0.05)
        confidence = min(1.0, confidence + entity_boost)
        
        return confidence
    
    def export_stats(self) -> Dict[str, Any]:
        """Export processing statistics"""
        return {
            'cache_size': len(self.cache.cache) if self.cache else 0,
            'context_sessions': len(self.context_manager.contexts) if self.context_manager else 0,
            'timestamp': datetime.datetime.now().isoformat()
        }


# Global instance
_language_processor = None

def get_language_processor() -> LanguageProcessor:
    """Get or create global language processor instance"""
    global _language_processor
    if _language_processor is None:
        _language_processor = LanguageProcessor()
    return _language_processor


# Example usage
if __name__ == "__main__":
    processor = LanguageProcessor()
    
    # Test messages
    test_messages = [
        "Hola, necesito cotizar Isodec 100mm para 50m2",
        "Quiero información sobre poliestireno",
        "Cuanto cuesta instalar isoroof?",
        "Hello, I need a quote for Isodec",
        "Ola, preciso de um orcamento",
    ]
    
    print("=" * 70)
    print("Language Processor - Test Results")
    print("=" * 70)
    
    for message in test_messages:
        result = processor.process_message(message, session_id="test_session")
        print(f"\nOriginal: {result.original}")
        print(f"Normalized: {result.normalized}")
        print(f"Language: {result.language.value}")
        print(f"Intent: {result.intent.value}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Entities: {json.dumps(result.entities, indent=2, ensure_ascii=False)}")
        print("-" * 70)
    
    print(f"\nStats: {json.dumps(processor.export_stats(), indent=2)}")
