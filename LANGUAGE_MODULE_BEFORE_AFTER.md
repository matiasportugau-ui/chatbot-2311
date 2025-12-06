# Central Language Module - Before & After Comparison

## 🔄 Migration Examples

### Example 1: AI Conversational Responses

#### ❌ BEFORE (Current - Hardcoded)
```python
# ia_conversacional_integrada.py
def _manejar_saludo(self, contexto: ContextoConversacion) -> RespuestaIA:
    saludos = [
        "¡Hola! Soy tu asistente de cotizaciones de BMC Uruguay. ¿En qué puedo ayudarte?",
        "¡Buenos días! Estoy aquí para ayudarte con tus consultas de aislamiento térmico.",
        "¡Hola! ¿Te interesa cotizar algún producto de aislamiento térmico?"
    ]
    mensaje = random.choice(saludos)
    return self._crear_respuesta(mensaje, "informativa", 0.9, ["patrones_respuesta"])
```

**Problems:**
- Hardcoded Spanish text
- Cannot change language
- Difficult to update messages
- No translation workflow

#### ✅ AFTER (With Language Module)
```python
# ia_conversacional_integrada.py
from language_module import get_language_manager

class IAConversacionalIntegrada:
    def __init__(self):
        # ... existing code ...
        self.lang_manager = None  # Will be set based on user locale
    
    def _detect_locale(self, mensaje: str, contexto: ContextoConversacion) -> str:
        """Detect locale from message or context"""
        # Try context first (from session)
        if hasattr(contexto, 'locale') and contexto.locale:
            return contexto.locale
        
        # Detect from message
        lang = get_language_manager()
        return lang.detect_locale(mensaje)
    
    def _manejar_saludo(self, contexto: ContextoConversacion) -> RespuestaIA:
        # Detect or get locale
        locale = self._detect_locale("", contexto)
        lang = get_language_manager(locale)
        
        # Get greetings from translation file
        greetings = lang.t('greetings', namespace='ai-responses')
        # If it's a list, pick random
        if isinstance(greetings, list):
            mensaje = random.choice(greetings)
        else:
            mensaje = greetings
        
        return self._crear_respuesta(mensaje, "informativa", 0.9, ["patrones_respuesta"])
```

**Benefits:**
- ✅ Language detection
- ✅ Easy to add new languages
- ✅ Centralized translations
- ✅ Can update without code changes

---

### Example 2: Quote Validation Messages

#### ❌ BEFORE (Current - Hardcoded)
```python
# utils_cotizaciones.py
def formatear_mensaje_faltantes(faltantes: list[str]) -> str:
    if not faltantes:
        return ""
    
    mensajes_campo = {
        "nombre": "tu nombre",
        "apellido": "tu apellido",
        "telefono": "tu número de teléfono",
        "producto": "qué producto te interesa (Isodec, Poliestireno o Lana de Roca)",
        # ... more hardcoded messages
    }
    
    if len(faltantes) == 1:
        campo = faltantes[0]
        descripcion = mensajes_campo.get(campo, campo)
        
        if campo == "producto":
            return (f"Para poder cotizar necesito que me indiques {descripcion}. "
                   "¿Cuál te interesa?")
        # ... more hardcoded logic
```

**Problems:**
- All messages hardcoded in Spanish
- Complex conditional logic
- Difficult to maintain
- No language support

#### ✅ AFTER (With Language Module)
```python
# utils_cotizaciones.py
from language_module import t

def formatear_mensaje_faltantes(faltantes: list[str], locale: str = 'es') -> str:
    if not faltantes:
        return ""
    
    # Handle grouped fields
    if "largo" in faltantes and "ancho" in faltantes:
        faltantes = [f for f in faltantes if f not in ["largo", "ancho"]]
        faltantes.append("dimensiones")
    
    if "nombre" in faltantes and "apellido" in faltantes:
        faltantes = [f for f in faltantes if f not in ["nombre", "apellido"]]
        faltantes.insert(0, "nombre_completo")
    
    # Single missing field
    if len(faltantes) == 1:
        campo = faltantes[0]
        return t(f'quotes.missing{campo.capitalize()}', namespace='quotes', locale=locale)
    
    # Multiple missing fields
    campos_texto = ", ".join([
        t(f'quotes.fieldNames.{campo}', namespace='quotes', locale=locale)
        for campo in faltantes[:-1]
    ]) + " y " + t(f'quotes.fieldNames.{faltantes[-1]}', namespace='quotes', locale=locale)
    
    return t('quotes.missingData', namespace='quotes', locale=locale, data=campos_texto)
```

**Translation File:**
```json
{
  "missingProduct": "Para poder cotizar necesito que me indiques qué producto te interesa (Isodec, Poliestireno o Lana de Roca). ¿Cuál te interesa?",
  "missingDimensions": "Para poder cotizar necesito las dimensiones (largo x ancho en metros, por ejemplo: 10m x 5m). ¿Cuáles son las dimensiones?",
  "missingName": "Para poder cotizar necesito tu nombre completo (nombre y apellido). ¿Cómo te llamas?",
  "missingData": "Para poder cotizar necesito los siguientes datos: {data}. ¿Podrías indicarme esa información?",
  "fieldNames": {
    "producto": "el producto",
    "dimensiones": "las dimensiones",
    "nombre_completo": "tu nombre completo"
  }
}
```

**Benefits:**
- ✅ Cleaner code
- ✅ Easy to add new languages
- ✅ Centralized message management
- ✅ Consistent messaging

---

### Example 3: Product Information

#### ❌ BEFORE (Current - Hardcoded)
```python
# ia_conversacional_integrada.py
def _obtener_informacion_producto(self, producto: str) -> str:
    if producto == "isodec":
        return ("🏠 **ISODEC - Panel Aislante Térmico**\n\n"
               "**Características principales:**\n"
               "✅ Núcleo de EPS (Poliestireno Expandido)\n"
               "✅ Excelente aislamiento térmico\n"
               "✅ Fácil instalación\n"
               "✅ Durabilidad superior\n\n"
               "**Opciones disponibles:**\n"
               "📏 Espesores: 50mm, 75mm, 100mm, 125mm, 150mm\n"
               "🎨 Colores: Blanco, Gris, Personalizado\n"
               "🔧 Terminaciones: Gotero, Hormigón, Aluminio\n\n"
               "💰 **Precio base:** $150/m² (100mm, Blanco)\n\n"
               "¿Te interesa cotizar Isodec?")
    # ... more hardcoded product info
```

**Problems:**
- Long hardcoded strings
- Difficult to update
- No language support
- Mixed formatting and content

#### ✅ AFTER (With Language Module)
```python
# ia_conversacional_integrada.py
def _obtener_informacion_producto(self, producto: str, locale: str = 'es') -> str:
    lang = get_language_manager(locale)
    
    # Get product info from translation file
    product_key = producto.replace('_', '').lower()
    if product_key == 'lanaroca':
        product_key = 'lanaRoca'
    
    # Build message from translation file
    product_info = lang.t(f'{product_key}.description', namespace='products')
    features = lang.t(f'{product_key}.features', namespace='products')
    base_price = self.sistema_cotizaciones.obtener_precio_producto(producto)
    
    message = f"🏠 **{lang.t(f'{product_key}.name', namespace='products')}**\n\n"
    message += f"**{lang.t('features', namespace='products')}:**\n"
    
    # Features is a list in JSON
    if isinstance(features, list):
        for feature in features:
            message += f"✅ {feature}\n"
    
    message += f"\n💰 **{lang.t('basePrice', namespace='products')}:** "
    message += lang.format_currency(base_price) + "\n\n"
    message += lang.t(f'{product_key}.interested', namespace='products')
    
    return message
```

**Translation File:**
```json
{
  "features": "Características principales",
  "isodec": {
    "name": "ISODEC - Panel Aislante Térmico",
    "description": "Panel aislante térmico con núcleo EPS",
    "features": [
      "Núcleo de EPS (Poliestireno Expandido)",
      "Excelente aislamiento térmico",
      "Fácil instalación",
      "Durabilidad superior"
    ],
    "thicknessOptions": "Espesores: 50mm, 75mm, 100mm, 125mm, 150mm",
    "colorOptions": "Colores: Blanco, Gris, Personalizado",
    "finishOptions": "Terminaciones: Gotero, Hormigón, Aluminio",
    "basePrice": "Precio base",
    "interested": "¿Te interesa cotizar Isodec?"
  }
}
```

**Benefits:**
- ✅ Structured content
- ✅ Easy to update product info
- ✅ Multi-language support
- ✅ Separation of content and code

---

### Example 4: Frontend Component

#### ❌ BEFORE (Current - Hardcoded)
```tsx
// src/components/dashboard/settings.tsx
<div className="space-y-2">
  <label className="text-sm font-medium">Language</label>
  <select className="w-full p-2 border rounded-lg">
    <option value="es">Español</option>
    <option value="en">English</option>
    <option value="pt">Português</option>
  </select>
</div>
```

**Problems:**
- Language selector doesn't work
- Labels hardcoded in English
- No actual language switching

#### ✅ AFTER (With next-intl)
```tsx
// src/components/dashboard/settings.tsx
'use client'

import {useTranslations, useLocale} from 'next-intl'
import {useRouter, usePathname} from 'next/navigation'

export function LanguageSelector() {
  const t = useTranslations('settings')
  const locale = useLocale()
  const router = useRouter()
  const pathname = usePathname()
  
  const handleLanguageChange = (newLocale: string) => {
    // Update URL with new locale
    const segments = pathname.split('/')
    segments[1] = newLocale
    router.push(segments.join('/'))
  }
  
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">{t('language')}</label>
      <select 
        value={locale}
        onChange={(e) => handleLanguageChange(e.target.value)}
        className="w-full p-2 border rounded-lg"
      >
        <option value="es">{t('spanish')}</option>
        <option value="en">{t('english')}</option>
        <option value="pt">{t('portuguese')}</option>
      </select>
    </div>
  )
}
```

**Translation File:**
```json
{
  "language": "Idioma",
  "spanish": "Español",
  "english": "Inglés",
  "portuguese": "Portugués"
}
```

**Benefits:**
- ✅ Functional language switcher
- ✅ Translated labels
- ✅ Persistent language preference
- ✅ Better UX

---

### Example 5: API Response

#### ❌ BEFORE (Current - Hardcoded)
```typescript
// src/app/api/chat/route.ts
return NextResponse.json({ 
  success: false,
  error: error instanceof Error ? error.message : 'Unknown error',
  data: {
    tipo: 'error',
    mensaje: 'Lo siento, hubo un problema procesando tu mensaje. Por favor, intenta de nuevo.'
  }
}, { status: 500 })
```

**Problems:**
- Hardcoded Spanish error message
- No locale detection
- Inconsistent with user's language

#### ✅ AFTER (With Language Module)
```typescript
// src/app/api/chat/route.ts
import {getLanguageManager} from '@/lib/language-manager'

export async function POST(request: NextRequest) {
  try {
    const { message, sessionId, userPhone, locale = 'es' } = await request.json()
    
    // ... processing ...
    
  } catch (error) {
    // Get language manager for user's locale
    const lang = getLanguageManager(locale)
    
    return NextResponse.json({ 
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      data: {
        tipo: 'error',
        mensaje: lang.t('error', namespace='common')
      }
    }, { status: 500 })
  }
}
```

**Benefits:**
- ✅ Locale-aware error messages
- ✅ Consistent language experience
- ✅ Better user experience

---

## 📊 Impact Summary

| Aspect | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Languages Supported** | 1 (Spanish) | 3+ (ES, EN, PT) | +200% |
| **Time to Add Language** | Days/weeks | Hours | 90% faster |
| **Time to Update Text** | Code changes | JSON edit | 95% faster |
| **Code Maintainability** | Low | High | Significant |
| **Translation Coverage** | 0% | 100% | Complete |
| **User Experience** | Single language | Multi-language | Much better |

---

## 🎯 Migration Priority

### High Priority (Week 1-2)
1. ✅ Common UI elements
2. ✅ Error messages
3. ✅ API responses

### Medium Priority (Week 3-4)
1. ✅ Quote-related messages
2. ✅ Product information
3. ✅ Validation messages

### Low Priority (Week 5-6)
1. ✅ AI response templates
2. ✅ Help text
3. ✅ Tooltips and hints

---

## ✅ Checklist

- [ ] Review all examples above
- [ ] Understand the migration pattern
- [ ] Set up translation files
- [ ] Update high-priority files first
- [ ] Test with multiple languages
- [ ] Verify all translations work
- [ ] Update documentation
- [ ] Train team on new system

---

**Ready to migrate?** Start with the high-priority items and work your way down!
