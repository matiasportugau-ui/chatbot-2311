# 🚀 START HERE - Simulador de Chatbot BMC

## ⚡ Inicio Rápido (3 pasos)

### 1️⃣ Instalar Dependencias

```bash
cd /Users/matias/Documents/GitHub/Dashboard-bmc/proyecto-cotizacion-whatsapp/05_dashboard_ui
./install_dependencies.sh
```

O manualmente:
```bash
pip install -r requirements.txt
```

### 2️⃣ Verificar Setup

```bash
python verify_setup.py
```

### 3️⃣ Iniciar y Probar

**Terminal 1 - API Server:**
```bash
python api_server.py
```

**Terminal 2 - Simulador:**
```bash
python simulate_chat_cli.py
```

O usa el script todo-en-uno:
```bash
./start_simulator.sh
```

## 💬 Tu Primera Conversación

Una vez que ambos terminales estén corriendo, en el simulador escribe:

```
Hola
Quiero cotizar Isodec
10 metros por 5 metros
100mm
Blanco
```

¡Y verás las respuestas del bot en tiempo real!

## 📚 Documentación Completa

- **`NEXT_STEPS.md`** - Guía detallada de próximos pasos
- **`README_SIMULATOR.md`** - Documentación completa del simulador
- **`QUICK_START_SIMULATOR.md`** - Inicio rápido

## 🎯 ¿Qué Puedes Hacer?

✅ Chatear con el bot usando lógica real  
✅ Probar diferentes conversaciones  
✅ Poblar knowledge base con escenarios  
✅ Iterar en prompts y mejorar respuestas  
✅ Exportar conversaciones para análisis  
✅ Ver estadísticas y métricas  

## 🆘 Problemas?

1. **Dependencias faltantes**: Ejecuta `./install_dependencies.sh`
2. **API no conecta**: Asegúrate de que `api_server.py` esté corriendo
3. **OpenAI errors**: El sistema usa pattern matching automáticamente
4. **MongoDB errors**: El sistema funciona sin MongoDB (sin persistencia)

## ✨ Comandos Útiles del CLI

Cuando uses `simulate_chat_cli.py`:

- `/help` - Ver comandos
- `/new` - Nueva sesión  
- `/history` - Ver historial
- `/export` - Exportar conversación
- `/stats` - Estadísticas KB
- `/exit` - Salir

---

**¡Listo para empezar!** 🎉

Ejecuta los 3 pasos de arriba y estarás chateando con el bot en minutos.

