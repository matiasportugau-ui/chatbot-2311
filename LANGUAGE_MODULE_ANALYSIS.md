# Central Language Module - Analysis & Optimization Guide

## Current Status

### Architecture Overview
The language processing is currently **distributed** across multiple files without a centralized module:

#### Python Files:
- `ia_conversacional_integrada.py` - Intent analysis, entity extraction (Spanish-focused)
- `chat_interactivo.py` - Pattern matching, message processing
- `base_conocimiento_dinamica.py` - Keyword extraction, text analysis

#### TypeScript Files:
- `quote-engine.ts` - Intent classification, keyword matching
- `quote-parser.ts` - OpenAI-based parsing with fallback

### Current Capabilities

✅ **What Works:**
1. **Basic Intent Detection** - Recognizes: saludo, cotizacion, informacion, pregunta
2. **Entity Extraction** - Products, dimensions, thickness, colors
3. **Keyword Matching** - Spanish keyword-based classification
4. **OpenAI Integration** - Advanced parsing via GPT-4
5. **Fallback Parsing** - Basic regex-based parsing when OpenAI fails

### Current Limitations

❌ **Critical Issues:**

1. **No Language Detection**
   - Assumes Spanish only
   - No automatic language detection
   - Cannot handle mixed-language input

2. **Duplicated Logic**
   - Intent detection duplicated in Python and TypeScript
   - Keyword lists maintained in multiple places
   - Inconsistent patterns across files

3. **No Normalization**
   - No text normalization (accents, case, typos)
   - No synonym handling
   - No abbreviation expansion

4. **Limited Multilingual Support**
   - Hardcoded Spanish keywords
   - No translation capabilities
   - No locale-specific formatting

5. **Performance Issues**
   - Multiple regex passes on same text
   - No caching of parsed results
   - OpenAI calls for every message (expensive)

6. **No Context Awareness**
   - Doesn't maintain conversation context
   - No memory of previous intents
   - Can't handle follow-up questions

7. **Error Handling**
   - Basic fallback only
   - No graceful degradation
   - Limited error recovery

### Code Duplication Examples

**Intent Detection (duplicated in 3+ places):**
```python
# ia_conversacional_integrada.py
patrones_intencion = {
    "saludo": ["hola", "buenos", "buenas", "hi", "hello"],
    "cotizacion": ["cotizar", "precio", "costo", "cuanto", "presupuesto"],
    # ...
}

# quote-engine.ts
const palabrasCotizacion = [
  'cotizar', 'precio', 'costo', 'cuanto', 'presupuesto', 'cotización',
  # ...
]
```

**Product Detection (duplicated):**
```python
# chat_interactivo.py
if "isodec" in mensaje_lower:
    producto = "isodec"
elif "poliestireno" in mensaje_lower:
    producto = "poliestireno"
# ...

# quote-parser.ts
if (text.includes('isodec')) tipo = 'Isodec'
else if (text.includes('isoroof')) tipo = 'Isoroof'
# ...
```

## Optimization Recommendations

### 1. Create Centralized Language Module

**Structure:**
```
language_processor/
├── __init__.py
├── language_detector.py      # Detect language (es, en, pt)
├── text_normalizer.py       # Normalize text (accents, case, typos)
├── intent_classifier.py      # Unified intent classification
├── entity_extractor.py      # Extract entities (products, dimensions)
├── context_manager.py       # Manage conversation context
├── cache_manager.py         # Cache parsed results
└── multilingual_support.py  # Translation & locale support
```

### 2. Performance Optimizations

**Caching Strategy:**
- Cache parsed intents (TTL: 5 minutes)
- Cache entity extractions
- Cache OpenAI responses (similar queries)

**Batch Processing:**
- Process multiple messages in batch
- Reduce OpenAI API calls

**Lazy Loading:**
- Load language models only when needed
- Use lightweight models for simple tasks

### 3. Best Practices Comparison

| Feature | Current | Recommended | Industry Standard |
|---------|---------|-------------|-------------------|
| **Language Detection** | ❌ None | ✅ Automatic (langdetect) | Google Cloud, AWS Comprehend |
| **Text Normalization** | ❌ None | ✅ Full normalization | spaCy, NLTK |
| **Intent Classification** | ⚠️ Keyword-based | ✅ ML-based (spaCy/NLU) | Rasa, Dialogflow |
| **Entity Extraction** | ⚠️ Regex-based | ✅ NER (Named Entity Recognition) | spaCy, Stanford NER |
| **Context Management** | ❌ None | ✅ Conversation state | Rasa, Bot Framework |
| **Multilingual** | ❌ Spanish only | ✅ Multi-language | i18n, react-intl |
| **Caching** | ❌ None | ✅ Redis/Memory cache | Redis, Memcached |
| **Error Handling** | ⚠️ Basic | ✅ Graceful degradation | Try-catch with fallbacks |

### 4. Implementation Priority

**Phase 1: Foundation (Week 1)**
1. Create centralized language module
2. Implement text normalization
3. Unify intent classification
4. Add basic caching

**Phase 2: Enhancement (Week 2)**
5. Add language detection
6. Improve entity extraction
7. Add context management
8. Implement error recovery

**Phase 3: Advanced (Week 3)**
9. Add multilingual support
10. Integrate ML-based classification
11. Add conversation memory
12. Performance optimization

## Proposed Architecture

```python
class LanguageProcessor:
    """Centralized language processing module"""
    
    def __init__(self):
        self.detector = LanguageDetector()
        self.normalizer = TextNormalizer()
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.context_manager = ContextManager()
        self.cache = CacheManager()
    
    def process_message(self, message: str, session_id: str) -> ProcessedMessage:
        """Main entry point for language processing"""
        # 1. Detect language
        language = self.detector.detect(message)
        
        # 2. Normalize text
        normalized = self.normalizer.normalize(message, language)
        
        # 3. Check cache
        cached = self.cache.get(normalized)
        if cached:
            return cached
        
        # 4. Get context
        context = self.context_manager.get_context(session_id)
        
        # 5. Classify intent
        intent = self.intent_classifier.classify(normalized, context, language)
        
        # 6. Extract entities
        entities = self.entity_extractor.extract(normalized, intent, language)
        
        # 7. Build result
        result = ProcessedMessage(
            original=message,
            normalized=normalized,
            language=language,
            intent=intent,
            entities=entities,
            confidence=calculate_confidence(intent, entities)
        )
        
        # 8. Cache result
        self.cache.set(normalized, result)
        
        # 9. Update context
        self.context_manager.update_context(session_id, result)
        
        return result
```

## Metrics & KPIs

**Performance Metrics:**
- Processing time: < 100ms (target: < 50ms)
- Cache hit rate: > 60%
- Intent accuracy: > 85%
- Entity extraction accuracy: > 80%

**Quality Metrics:**
- Language detection accuracy: > 95%
- Multilingual support: 3+ languages
- Error recovery rate: > 90%

## Migration Strategy

1. **Create new module** alongside existing code
2. **Gradual migration** - Route 10% of traffic to new module
3. **A/B testing** - Compare results
4. **Full migration** - Once validated
5. **Remove old code** - Clean up duplicated logic

## Dependencies

**Required:**
- `langdetect` - Language detection
- `spacy` - NLP processing
- `unidecode` - Text normalization
- `redis` - Caching (optional)

**Optional:**
- `googletrans` - Translation
- `nltk` - Advanced NLP
- `transformers` - ML models

## Next Steps

1. ✅ Review this analysis
2. ⏳ Create centralized language module
3. ⏳ Implement core features
4. ⏳ Add tests
5. ⏳ Integrate with existing code
6. ⏳ Monitor performance
7. ⏳ Iterate and improve
