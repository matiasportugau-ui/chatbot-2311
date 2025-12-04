"""
Unit tests for intent detection functionality
"""

import pytest

from ia_conversacional_integrada import IAConversacionalIntegrada


class TestIntentDetection:
    @pytest.fixture
    def ia(self):
        return IAConversacionalIntegrada()

    def test_greeting_intent(self, ia):
        intent, confidence = ia._analizar_intencion("Hola")
        assert intent == "saludo"
        assert confidence > 0.5
