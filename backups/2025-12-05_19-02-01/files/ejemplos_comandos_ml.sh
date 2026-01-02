#!/bin/bash
# Ejemplos de comandos para extraer datos de Mercado Libre

echo "📋 EJEMPLOS DE COMANDOS PARA MERCADO LIBRE"
echo "=========================================="
echo ""

echo "1️⃣  Extraer desde archivo JSON:"
echo "python3 extraer_datos_entrenamiento.py --mercado-libre-archivo preguntas_ml.json --salida ml_entrenamiento.json"
echo ""

echo "2️⃣  Extraer desde archivo CSV:"
echo "python3 extraer_datos_entrenamiento.py --mercado-libre-archivo preguntas_ml.csv --salida ml_entrenamiento.json"
echo ""

echo "3️⃣  Extraer desde API (requiere token):"
echo "python3 extraer_datos_entrenamiento.py --mercado-libre-api --access-token TU_TOKEN --seller-id TU_SELLER_ID --limite 100 --salida ml_api.json"
echo ""

echo "4️⃣  Combinar WhatsApp + Mercado Libre:"
echo "python3 extraer_datos_entrenamiento.py --whatsapp-mongodb --mercado-libre-archivo preguntas_ml.json --salida datos_combinados.json"
echo ""

echo "5️⃣  Exportar a CSV:"
echo "python3 extraer_datos_entrenamiento.py --mercado-libre-archivo preguntas_ml.json --salida ml_entrenamiento.csv --formato csv"
echo ""

