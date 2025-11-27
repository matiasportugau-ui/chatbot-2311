#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Central Language Module for BMC Uruguay System
Handles translations and language management across the Python backend
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from functools import lru_cache
import re


class LanguageManager:
    """
    Central language manager for handling translations
    
    Features:
    - Multi-language support (ES, EN, PT)
    - Namespace organization
    - Variable interpolation
    - Pluralization support
    - Caching for performance
    - Fallback to default language
    """
    
    def __init__(self, locale: str = 'es', locales_dir: Optional[str] = None):
        """
        Initialize language manager
        
        Args:
            locale: Default locale code (es, en, pt)
            locales_dir: Directory containing translation files (defaults to ./locales)
        """
        self.locale = locale
        self.default_locale = 'es'
        
        # Determine locales directory
        if locales_dir:
            self.locales_dir = Path(locales_dir)
        else:
            # Default to locales directory in project root
            current_file = Path(__file__).parent
            self.locales_dir = current_file / 'locales'
        
        # Cache for loaded translations
        self._translation_cache: Dict[str, Dict[str, Any]] = {}
        
        # Load translations for current locale
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Load all translation files for current locale"""
        locale_dir = self.locales_dir / self.locale
        
        if not locale_dir.exists():
            # Fallback to default locale if current locale doesn't exist
            if self.locale != self.default_locale:
                locale_dir = self.locales_dir / self.default_locale
                self.locale = self.default_locale
        
        if not locale_dir.exists():
            raise FileNotFoundError(
                f"Translation directory not found: {locale_dir}. "
                f"Please create translation files in {self.locales_dir}"
            )
        
        # Load all JSON files in locale directory
        for json_file in locale_dir.glob('*.json'):
            namespace = json_file.stem  # filename without extension
            cache_key = f"{self.locale}:{namespace}"
            
            if cache_key not in self._translation_cache:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        self._translation_cache[cache_key] = json.load(f)
                except Exception as e:
                    print(f"Warning: Could not load {json_file}: {e}")
                    self._translation_cache[cache_key] = {}
    
    @lru_cache(maxsize=1000)
    def _get_translation(self, locale: str, namespace: str, key: str) -> Optional[str]:
        """Get translation with caching"""
        cache_key = f"{locale}:{namespace}"
        translations = self._translation_cache.get(cache_key, {})
        
        # Navigate nested keys (e.g., "quotes.welcome.message")
        keys = key.split('.')
        value = translations
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
        
        return value if isinstance(value, str) else None
    
    def t(self, key: str, namespace: str = 'common', **kwargs) -> str:
        """
        Get translation for a key
        
        Args:
            key: Translation key (supports dot notation for nested keys)
            namespace: Namespace/file name (default: 'common')
            **kwargs: Variables for interpolation
        
        Returns:
            Translated string with variables interpolated
        
        Example:
            >>> lang = LanguageManager('es')
            >>> lang.t('welcome', name='Juan')
            '¡Hola Juan! Bienvenido al sistema BMC.'
        """
        # Try current locale first
        translation = self._get_translation(self.locale, namespace, key)
        
        # Fallback to default locale if not found
        if not translation and self.locale != self.default_locale:
            translation = self._get_translation(self.default_locale, namespace, key)
        
        # Fallback to key if still not found
        if not translation:
            print(f"Warning: Translation missing for key '{key}' in namespace '{namespace}' (locale: {self.locale})")
            return key
        
        # Interpolate variables
        if kwargs:
            try:
                return translation.format(**kwargs)
            except KeyError as e:
                print(f"Warning: Missing variable {e} in translation key '{key}'")
                return translation
        
        return translation
    
    def set_locale(self, locale: str) -> None:
        """
        Change the current locale
        
        Args:
            locale: New locale code (es, en, pt)
        """
        if locale != self.locale:
            self.locale = locale
            self._translation_cache.clear()  # Clear cache
            self._get_translation.cache_clear()  # Clear LRU cache
            self._load_translations()
    
    def get_available_locales(self) -> List[str]:
        """Get list of available locales"""
        if not self.locales_dir.exists():
            return [self.default_locale]
        
        locales = []
        for item in self.locales_dir.iterdir():
            if item.is_dir() and (item / 'common.json').exists():
                locales.append(item.name)
        
        return sorted(locales) if locales else [self.default_locale]
    
    def detect_locale(self, text: str) -> str:
        """
        Detect language from text (simple heuristic-based detection)
        
        Args:
            text: Input text to analyze
        
        Returns:
            Detected locale code
        
        Note: This is a simple implementation. For production, consider using
        a proper language detection library like langdetect or polyglot.
        """
        text_lower = text.lower()
        
        # Spanish indicators
        spanish_words = ['hola', 'gracias', 'cotización', 'producto', 'precio', 'necesito']
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        
        # Portuguese indicators
        portuguese_words = ['olá', 'obrigado', 'cotação', 'produto', 'preço', 'preciso']
        portuguese_count = sum(1 for word in portuguese_words if word in text_lower)
        
        # English indicators
        english_words = ['hello', 'thanks', 'quote', 'product', 'price', 'need']
        english_count = sum(1 for word in english_words if word in text_lower)
        
        # Determine locale
        if spanish_count > portuguese_count and spanish_count > english_count:
            return 'es'
        elif portuguese_count > english_count:
            return 'pt'
        elif english_count > 0:
            return 'en'
        else:
            return self.default_locale
    
    def pluralize(self, key: str, count: int, namespace: str = 'common') -> str:
        """
        Get pluralized translation
        
        Args:
            key: Translation key (base key, plural forms should be key.one, key.other)
            count: Number for pluralization
            namespace: Namespace name
        
        Returns:
            Pluralized translation
        
        Example:
            Translation file:
            {
              "items": {
                "one": "1 artículo",
                "other": "{count} artículos"
              }
            }
            
            >>> lang.pluralize('items', 1)  # Returns "1 artículo"
            >>> lang.pluralize('items', 5)  # Returns "5 artículos"
        """
        # Determine plural form (simplified: Spanish/Portuguese use count != 1)
        if self.locale in ['es', 'pt']:
            plural_key = f"{key}.one" if count == 1 else f"{key}.other"
        else:  # English
            plural_key = f"{key}.one" if count == 1 else f"{key}.other"
        
        return self.t(plural_key, namespace, count=count)
    
    def format_number(self, number: float, decimals: int = 2) -> str:
        """Format number according to locale"""
        if self.locale == 'es':
            # Spanish: 1.234,56
            return f"{number:,.{decimals}f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif self.locale == 'pt':
            # Portuguese: 1.234,56
            return f"{number:,.{decimals}f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        else:  # English
            # English: 1,234.56
            return f"{number:,.{decimals}f}"
    
    def format_currency(self, amount: float, currency: str = 'UYU') -> str:
        """Format currency according to locale"""
        formatted = self.format_number(amount, decimals=2)
        
        if self.locale == 'es':
            return f"${formatted} {currency}"
        elif self.locale == 'pt':
            return f"R$ {formatted}" if currency == 'UYU' else f"{currency} {formatted}"
        else:  # English
            return f"{currency} {formatted}"


# Global instance (singleton pattern)
_global_language_manager: Optional[LanguageManager] = None


def get_language_manager(locale: str = 'es') -> LanguageManager:
    """
    Get or create global language manager instance
    
    Args:
        locale: Locale code
    
    Returns:
        LanguageManager instance
    """
    global _global_language_manager
    
    if _global_language_manager is None:
        _global_language_manager = LanguageManager(locale)
    elif _global_language_manager.locale != locale:
        _global_language_manager.set_locale(locale)
    
    return _global_language_manager


def t(key: str, namespace: str = 'common', locale: str = 'es', **kwargs) -> str:
    """
    Convenience function for translations
    
    Args:
        key: Translation key
        namespace: Namespace name
        locale: Locale code
        **kwargs: Variables for interpolation
    
    Returns:
        Translated string
    
    Example:
        >>> from language_module import t
        >>> t('welcome', name='Juan', locale='es')
        '¡Hola Juan! Bienvenido al sistema BMC.'
    """
    lang_manager = get_language_manager(locale)
    return lang_manager.t(key, namespace, **kwargs)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("Central Language Module - Test & Demo")
    print("=" * 60)
    
    # Initialize with Spanish
    lang_es = LanguageManager('es')
    print(f"\n📍 Current locale: {lang_es.locale}")
    print(f"📚 Available locales: {lang_es.get_available_locales()}")
    
    # Test translations (will show warnings if files don't exist)
    print("\n🔤 Testing translations:")
    print(f"  Welcome: {lang_es.t('welcome', name='Juan')}")
    print(f"  Quote label: {lang_es.t('quotes.productLabel')}")
    
    # Switch to English
    print("\n🔄 Switching to English...")
    lang_en = LanguageManager('en')
    print(f"📍 Current locale: {lang_en.locale}")
    print(f"  Welcome: {lang_en.t('welcome', name='John')}")
    
    # Test language detection
    print("\n🔍 Testing language detection:")
    test_texts = [
        "Hola, necesito información sobre Isodec",
        "Hello, I need information about Isodec",
        "Olá, preciso de informações sobre Isodec"
    ]
    
    for text in test_texts:
        detected = lang_es.detect_locale(text)
        print(f"  '{text[:30]}...' -> {detected}")
    
    # Test number formatting
    print("\n💰 Testing number formatting:")
    test_number = 1234.56
    for locale in ['es', 'en', 'pt']:
        lang = LanguageManager(locale)
        print(f"  {locale.upper()}: {lang.format_currency(test_number)}")
    
    print("\n✅ Demo completed!")
    print("\n📝 Note: Create translation files in ./locales/{locale}/common.json")
    print("   to see actual translations instead of keys.")
