"""
Integration tests for conversation flow
"""

import pytest

from ia_conversacional_integrada import IAConversacionalIntegrada


class TestConversationFlow:
    @pytest.fixture
    def ia(self):
        return IAConversacionalIntegrada()

    def test_simple_greeting_flow(self, ia):
        result = ia.procesar_mensaje_usuario("Hola", "+59891234567", "test_session_1")
        assert result is not None
        assert "mensaje" in result

    def test_quote_request_flow(self, ia):
        result1 = ia.procesar_mensaje_usuario("Hola", "+59891234567", "test_session_2")
        result2 = ia.procesar_mensaje_usuario(
            "Quiero cotizar isodec", "+59891234567", "test_session_2"
        )
        assert result1 is not None
        assert result2 is not None

    def test_multi_turn_conversation(self, ia):
        session_id = "test_session_3"
        result1 = ia.procesar_mensaje_usuario("Hola", "+59891234567", session_id)
        result2 = ia.procesar_mensaje_usuario(
            "Información sobre isodec", "+59891234567", session_id
        )
        result3 = ia.procesar_mensaje_usuario(
            "Quiero cotizar para 50 metros", "+59891234567", session_id
        )
        assert result1 is not None
        assert result2 is not None
        assert result3 is not None
