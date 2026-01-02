"""
Unit tests for entity extraction functionality
"""

import pytest

from ia_conversacional_integrada import IAConversacionalIntegrada


class TestEntityExtraction:
    @pytest.fixture
    def ia(self):
        return IAConversacionalIntegrada()

    def test_product_extraction(self, ia):
        entities = ia._extraer_entidades("Quiero isodec")
        assert "productos" in entities
        assert len(entities.get("productos", [])) > 0

    def test_dimension_extraction(self, ia):
        entities = ia._extraer_entidades("10 metros x 5 metros")
        assert "dimensiones" in entities

    def test_multiple_entities(self, ia):
        message = "Quiero cotizar isodec 100mm para 50 metros cuadrados"
        entities = ia._extraer_entidades(message)
        assert len(entities.keys()) > 0
