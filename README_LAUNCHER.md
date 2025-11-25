# 🚀 Launcher One-Click – BMC Chatbot

Este launcher permite instalar, configurar e iniciar el chatbot completo con **un solo click** en Windows.

## 📦 Archivos incluidos

- `INICIAR_CHATBOT.bat` – Script principal (ejecútalo)
- `instalar_dependencias_automatico.py` – Instala todas las dependencias
- `configurar_entorno.py` – Configura el archivo `.env`
- `gestionar_servicios.py` – Verifica/activa servicios opcionales (MongoDB)
- `verificar_sistema_completo.py` – Reporte completo de estado

## ✅ Qué hace automáticamente

1. **Verifica Python 3.11+**  
   - Si no está instalado, descarga el instalador oficial y guía el proceso

2. **Instala dependencias**  
   - Usa `pip install -r requirements.txt`
   - Actualiza `pip` antes de instalar

3. **Configura `.env`**  
   - Solicita (una sola vez) tu `OPENAI_API_KEY`
   - Configura valores por defecto (`OPENAI_MODEL`, `MONGODB_URI`)

4. **Gestiona servicios opcionales**  
   - Detecta Docker
   - Crea/inicia el contenedor `bmc-mongodb` (mongo:7.0) si está disponible

5. **Verifica el sistema**  
   - Versiones de Python
   - Dependencias críticas y opcionales
   - Archivos de conocimiento
   - Estado de MongoDB

6. **Inicia el chatbot** (`chat_interactivo.py`)

## 🖱️ Cómo usarlo

1. Haz doble clic en `INICIAR_CHATBOT.bat`
2. Sigue las instrucciones en pantalla:
   - Instala Python si se abre el instalador
   - Ingresa tu `OPENAI_API_KEY` cuando se solicite
3. El script configurará todo y abrirá el chatbot

## ℹ️ Requisitos previos

- Windows 10 u 11
- Conexión a internet (para instalar dependencias o Python si falta)
- Docker Desktop (opcional, solo si quieres MongoDB local)

## 🛠️ Reintentos / Troubleshooting

- Si algo falla, revisa el mensaje mostrado y vuelve a ejecutar `INICIAR_CHATBOT.bat`
- Para reinstalar dependencias manualmente:
  ```bash
  python instalar_dependencias_automatico.py
  ```
- Para reconfigurar tu `.env`:
  ```bash
  python configurar_entorno.py
  ```

## 🔐 Seguridad

Tu `OPENAI_API_KEY` se guarda en `.env` (lista en `.gitignore`), por lo que **no se subirá a Git**.

---

¿Necesitas personalizar el flujo (por ejemplo, iniciar API server o el dashboard)?  
Amplía `INICIAR_CHATBOT.bat` y los scripts auxiliares según tus necesidades. ¡El sistema está diseñado para escalar! 💡

