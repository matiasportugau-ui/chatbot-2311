# Central Language Module - Quick Start Guide

## 🚀 Quick Setup

### 1. Install Dependencies

No external dependencies required! The module uses only Python standard library.

### 2. Create Translation Files Structure

```
locales/
├── es/
│   ├── common.json
│   ├── quotes.json
│   ├── products.json
│   └── ai-responses.json
├── en/
│   └── [same structure]
└── pt/
    └── [same structure]
```

### 3. Basic Usage

```python
from language_module import LanguageManager, t

# Initialize with Spanish
lang = LanguageManager('es')

# Simple translation
message = lang.t('welcome', name='Juan')
# Returns: "¡Hola Juan! Bienvenido al sistema de cotizaciones BMC Uruguay."

# Translation with namespace
quote_label = lang.t('productLabel', namespace='quotes')
# Returns: "Producto"

# Using convenience function
from language_module import t
message = t('welcome', name='Juan', locale='es')
```

---

## 📝 Common Patterns

### Pattern 1: Simple Translation

```python
lang = LanguageManager('es')
greeting = lang.t('greeting')
```

### Pattern 2: Translation with Variables

```python
lang = LanguageManager('es')
welcome = lang.t('welcome', name='Juan', company='BMC')
```

Translation file:
```json
{
  "welcome": "¡Hola {name}! Bienvenido a {company}."
}
```

### Pattern 3: Nested Keys

```python
lang = LanguageManager('es')
product_name = lang.t('isodec.name', namespace='products')
```

Translation file:
```json
{
  "isodec": {
    "name": "ISODEC",
    "description": "Panel aislante térmico"
  }
}
```

### Pattern 4: Pluralization

```python
lang = LanguageManager('es')
items = lang.pluralize('items', count=5)
```

Translation file:
```json
{
  "items": {
    "one": "1 artículo",
    "other": "{count} artículos"
  }
}
```

### Pattern 5: Number/Currency Formatting

```python
lang = LanguageManager('es')
formatted = lang.format_currency(1234.56)
# Returns: "$1.234,56 UYU"
```

---

## 🔄 Integration Examples

### Example 1: Update `ia_conversacional_integrada.py`

**Before:**
```python
mensaje = "¡Hola! Soy tu asistente de cotizaciones de BMC Uruguay."
```

**After:**
```python
from language_module import get_language_manager

# Detect locale from user input or session
lang = get_language_manager(locale='es')
mensaje = lang.t('greetings', namespace='ai-responses')
```

### Example 2: Update `utils_cotizaciones.py`

**Before:**
```python
return "Para poder cotizar necesito tu nombre completo."
```

**After:**
```python
from language_module import t

def formatear_mensaje_faltantes(faltantes, locale='es'):
    return t('quotes.missingName', namespace='quotes', locale=locale)
```

### Example 3: API Response Translation

```python
from language_module import LanguageManager

def handle_api_request(request_data):
    # Detect or get locale from request
    locale = request_data.get('locale', 'es')
    lang = LanguageManager(locale)
    
    response = {
        'message': lang.t('quotes.welcomeMessage'),
        'status': lang.t('success', namespace='common')
    }
    return response
```

---

## 🎯 Migration Checklist

### Step 1: Identify Strings to Translate

```bash
# Search for hardcoded Spanish strings
grep -r "¡Hola\|Bienvenido\|Cotización" --include="*.py"
```

### Step 2: Create Translation Keys

Choose a naming convention:
- `namespace.key` (e.g., `quotes.welcomeMessage`)
- `namespace.category.key` (e.g., `quotes.messages.welcome`)

### Step 3: Extract Strings

1. Create translation files
2. Move strings to JSON files
3. Replace hardcoded strings with `lang.t()` calls

### Step 4: Test

```python
# Test all locales
for locale in ['es', 'en', 'pt']:
    lang = LanguageManager(locale)
    print(f"{locale}: {lang.t('welcome', name='Test')}")
```

---

## 🔧 Advanced Usage

### Custom Locale Detection

```python
def detect_user_locale(user_input, session_data):
    # Try session first
    if 'locale' in session_data:
        return session_data['locale']
    
    # Detect from input
    lang = LanguageManager()
    return lang.detect_locale(user_input)
```

### Caching Strategy

The module includes built-in caching:
- Translation files are cached in memory
- LRU cache for frequently accessed translations
- Cache clears when locale changes

### Error Handling

```python
try:
    lang = LanguageManager('es')
    message = lang.t('nonexistent.key')
except FileNotFoundError:
    # Handle missing translation files
    pass
```

---

## 📊 Performance Tips

1. **Reuse LanguageManager instances** - Don't create new instances for each request
2. **Use namespaces** - Organize translations to load only what you need
3. **Cache at application level** - Keep a global instance per locale
4. **Lazy load** - Only load translations when needed

---

## 🐛 Troubleshooting

### Issue: "Translation directory not found"

**Solution:** Create the `locales` directory structure:
```bash
mkdir -p locales/{es,en,pt}
touch locales/es/common.json
```

### Issue: "Translation missing for key"

**Solution:** Add the key to the appropriate translation file or check the namespace.

### Issue: "Missing variable in translation"

**Solution:** Ensure all variables in the translation string are provided:
```python
# Translation: "Hello {name}, welcome to {company}"
lang.t('welcome', name='Juan', company='BMC')  # ✅ Correct
lang.t('welcome', name='Juan')  # ❌ Missing 'company'
```

---

## 📚 Next Steps

1. Review `CENTRAL_LANGUAGE_MODULE_ANALYSIS.md` for detailed analysis
2. Set up translation workflow
3. Migrate existing strings
4. Add new languages as needed
5. Train team on usage

---

**Need Help?** Check the main analysis document or review the code examples in `language_module.py`.
