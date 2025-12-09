# 📤 Instrucciones para Subir .env.unified a GitHub

Tu archivo `.env.unified` está listo con **51 variables** extraídas de tu workspace.

## 🚀 Opción 1: Subida Automática (Recomendado)

### Requisitos:

```bash
# Instalar GitHub CLI si no lo tienes
brew install gh  # macOS
# o ver: https://cli.github.com/

# Autenticarse
gh auth login
```

### Subir:

```bash
python upload_secrets_to_github.py --env-file .env.unified
```

El script:
- ✅ Lee todas las variables de `.env.unified`
- ✅ Las sube a GitHub Repository Secrets
- ✅ Las hace disponibles automáticamente en Codespaces

## 📋 Opción 2: Subida Manual

1. **Ir a GitHub:**
   ```
   https://github.com/matiasportugau-ui/chatbot-2311/settings/secrets/codespaces
   ```

2. **Para cada variable en `.env.unified`:**
   - Click "New repository secret"
   - Name: `OPENAI_API_KEY` (ejemplo)
   - Value: `sk-...` (del archivo .env.unified)
   - Click "Add secret"

3. **Repetir para todas las variables**

### Ver todas las variables a subir:

```bash
# Ver solo los nombres (sin valores)
grep "^[A-Z]" .env.unified | cut -d'=' -f1

# Ver con valores (¡CUIDADO! No compartir)
cat .env.unified
```

## ✅ Verificación

Después de subir, verifica:

1. **En GitHub:**
   - Settings → Secrets and variables → Codespaces
   - Deberías ver todas las variables listadas

2. **En Codespaces:**
   ```bash
   # Las variables estarán disponibles automáticamente
   echo $OPENAI_API_KEY
   
   # O cargar desde .env
   bash .devcontainer/load-secrets.sh
   ```

## 🔐 Seguridad

- ✅ `.env.unified` está en `.gitignore` (no se subirá a Git)
- ✅ Los secrets en GitHub están encriptados
- ✅ Solo tú y colaboradores autorizados pueden verlos
- ❌ **NUNCA** compartas el contenido de `.env.unified` públicamente

## 📝 Variables Encontradas

Tu `.env.unified` contiene:
- Variables de AI (OpenAI, Groq, Gemini, Grok)
- Configuración de bases de datos (MongoDB)
- Credenciales de WhatsApp
- Configuración de MercadoLibre
- Y más...

**Total: 51 variables** listas para subir.

---

**¿Listo para subir?** Ejecuta:

```bash
python upload_secrets_to_github.py --env-file .env.unified
```

