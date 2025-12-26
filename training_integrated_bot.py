#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Training Integration Module
Integrates the training/evaluation system with the existing chatbot
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from training_evaluation_system import (
    TrainingEvaluationSystem,
    BotMode,
    CorrectionTrigger,
    format_correction_response
)
from benchmark_system import BenchmarkSystem, format_benchmark_report

try:
    from ia_conversacional_integrada import IAConversacionalIntegrada
    MAIN_BOT_AVAILABLE = True
except Exception as e:
    MAIN_BOT_AVAILABLE = False
    print(f"Warning: Main bot not available ({e}), using mock")


class TrainingIntegratedBot:
    """Bot with integrated training capabilities"""
    
    def __init__(self):
        """Initialize the training-integrated bot"""
        # Initialize training system
        self.training_system = TrainingEvaluationSystem()
        self.benchmark_system = BenchmarkSystem()
        
        # Initialize main bot
        if MAIN_BOT_AVAILABLE:
            self.main_bot = IAConversacionalIntegrada()
        else:
            self.main_bot = None
        
        # Conversation context
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
        self.pending_approval: Dict[str, str] = {}  # session_id -> correction_id
    
    def process_message(
        self,
        session_id: str,
        user_id: str,
        message: str
    ) -> str:
        """
        Process a message with training awareness
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            message: User message
            
        Returns:
            Bot response
        """
        # Store message in history
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].append({
            "role": "user",
            "content": message
        })
        
        # Check for mode switch commands
        message_upper = message.upper().strip()
        
        if message_upper in ["MODO ENTRENAMIENTO", "TRAINING MODE", "ENTRENAMIENTO"]:
            result = self.training_system.set_session_mode(session_id, user_id, BotMode.TRAINING)
            response = result["message"]
            if "instructions" in result:
                response += "\n\n" + result["instructions"]
            self.conversation_history[session_id].append({
                "role": "assistant",
                "content": response
            })
            return response
        
        elif message_upper in ["MODO PRODUCCIÓN", "PRODUCTION MODE", "PRODUCCION"]:
            result = self.training_system.set_session_mode(session_id, user_id, BotMode.PRODUCTION)
            self.conversation_history[session_id].append({
                "role": "assistant",
                "content": result["message"]
            })
            return result["message"]
        
        elif message_upper in ["SALIR ENTRENAMIENTO", "FIN ENTRENAMIENTO", "FIN"]:
            result = self.training_system.end_training_session(session_id)
            if result["success"] and "statistics" in result:
                stats = result["statistics"]
                stats_msg = f"""
{result['message']}

📊 **Estadísticas de la Sesión:**
- Duración: {stats.get('duration_minutes', 0)} minutos
- Correcciones realizadas: {stats.get('corrections_made', 0)}
- Respuestas aprobadas: {stats.get('responses_approved', 0)}
- Respuestas rechazadas: {stats.get('responses_rejected', 0)}
- Tasa de aprobación: {stats.get('approval_rate', 0):.1f}%
"""
                self.conversation_history[session_id].append({
                    "role": "assistant",
                    "content": stats_msg
                })
                return stats_msg
            return result.get("message", "Sesión finalizada")
        
        elif message_upper in ["ESTADÍSTICAS", "ESTADISTICAS", "STATS", "📊"]:
            result = self.training_system.get_session_statistics(session_id)
            if result["success"]:
                stats_msg = f"""
📊 **Estadísticas de la Sesión Actual:**
- Modo: {result['mode']}
- Duración: {result['duration_minutes']} minutos
- Correcciones realizadas: {result['corrections_made']}
- Respuestas aprobadas: {result['responses_approved']}
- Respuestas rechazadas: {result['responses_rejected']}
- Tasa de aprobación: {result['approval_rate']:.1f}%
"""
                self.conversation_history[session_id].append({
                    "role": "assistant",
                    "content": stats_msg
                })
                return stats_msg
            return result["message"]
        
        # Check if waiting for approval/rejection
        if session_id in self.pending_approval:
            if message_upper in ["APROBAR", "APPROVE", "✅", "OK", "SI", "SÍ"]:
                correction_id = self.pending_approval[session_id]
                result = self.training_system.approve_reformulation(correction_id, user_id)
                del self.pending_approval[session_id]
                
                self.conversation_history[session_id].append({
                    "role": "assistant",
                    "content": result["message"]
                })
                return result["message"]
            
            elif message_upper.startswith("RECHAZAR") or message_upper.startswith("❌"):
                correction_id = self.pending_approval[session_id]
                reason = message[message.find(" "):].strip() if " " in message else "Sin razón especificada"
                result = self.training_system.reject_reformulation(correction_id, user_id, reason)
                del self.pending_approval[session_id]
                
                response = result["message"]
                if "next_action" in result:
                    response += "\n\n" + result["next_action"]
                
                self.conversation_history[session_id].append({
                    "role": "assistant",
                    "content": response
                })
                return response
        
        # Check for correction
        is_correction, correction_text = self.training_system.detect_correction(message, session_id)
        
        if is_correction and correction_text:
            # Get previous bot response
            bot_responses = [
                msg["content"] for msg in self.conversation_history[session_id]
                if msg["role"] == "assistant"
            ]
            
            if not bot_responses:
                response = "No hay respuesta previa para corregir. Por favor, primero haz una pregunta."
                self.conversation_history[session_id].append({
                    "role": "assistant",
                    "content": response
                })
                return response
            
            previous_response = bot_responses[-1]
            
            # Get previous user query (2 messages back)
            user_queries = [
                msg["content"] for msg in self.conversation_history[session_id]
                if msg["role"] == "user"
            ]
            previous_query = user_queries[-2] if len(user_queries) >= 2 else user_queries[-1]
            
            # Create correction request
            correction = self.training_system.create_correction_request(
                session_id=session_id,
                user_id=user_id,
                original_query=previous_query,
                original_response=previous_response,
                correction_text=correction_text
            )
            
            # Generate reformulated response
            reformulated = self.training_system.generate_reformulated_response(
                correction,
                self._generate_bot_response
            )
            
            # Store for approval
            self.pending_approval[session_id] = correction.id
            
            # Format and return
            response = format_correction_response(reformulated)
            self.conversation_history[session_id].append({
                "role": "assistant",
                "content": response
            })
            return response
        
        # Normal message processing
        response = self._generate_bot_response(message, session_id)
        
        self.conversation_history[session_id].append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def _generate_bot_response(self, message: str, session_id: str = None) -> str:
        """
        Generate bot response using main bot or mock
        
        Args:
            message: User message
            session_id: Optional session ID for context
            
        Returns:
            Bot response
        """
        if self.main_bot and MAIN_BOT_AVAILABLE:
            try:
                # Use the actual bot's response generation
                # This would integrate with IAConversacionalIntegrada
                response = self.main_bot.procesar_mensaje(message, session_id or "default")
                if isinstance(response, dict) and "mensaje" in response:
                    return response["mensaje"]
                return str(response)
            except Exception as e:
                print(f"Error generating response: {e}")
                return self._mock_response(message)
        else:
            return self._mock_response(message)
    
    def _mock_response(self, message: str) -> str:
        """Generate a mock response for testing"""
        message_lower = message.lower()
        
        if "cotizacion" in message_lower or "cotización" in message_lower:
            return """
Para generar una cotización necesito los siguientes datos:
- Producto (Isodec, Poliestireno o Lana de Roca)
- Espesor deseado
- Dimensiones (largo x ancho)
- Tus datos de contacto

¿Podrías proporcionarme esta información?
"""
        elif "producto" in message_lower or "aislante" in message_lower:
            return """
Tenemos disponibles tres tipos principales de aislantes térmicos:

1. **Isodec**: Panel aislante con núcleo de EPS, ideal para techos y paredes
2. **Poliestireno Expandido**: Versátil y económico, excelente aislación térmica
3. **Lana de Roca**: Aislación térmica y acústica, resistente al fuego

¿Sobre cuál te gustaría saber más?
"""
        elif "precio" in message_lower:
            return """
Los precios varían según el producto, espesor y cantidad. Para darte un presupuesto 
exacto, necesito:
- Tipo de producto
- Espesor
- Metros cuadrados

¿Podrías darme estos datos para cotizar?
"""
        else:
            return """
Gracias por tu consulta. Estoy aquí para ayudarte con información sobre nuestros 
productos de aislamiento térmico y generar cotizaciones. ¿En qué puedo asistirte?
"""
    
    def run_benchmark(
        self,
        suite_name: str = "default",
        mode: str = "after_training"
    ) -> str:
        """
        Run benchmark and return formatted results
        
        Args:
            suite_name: Test suite name
            mode: 'before_training' or 'after_training'
            
        Returns:
            Formatted benchmark results
        """
        result = self.benchmark_system.run_benchmark(
            suite_name=suite_name,
            bot_response_func=lambda msg: self._generate_bot_response(msg),
            mode=mode
        )
        
        if not result["success"]:
            return result["message"]
        
        summary = result["summary"]
        
        output = f"""
📊 **Resultados del Benchmark**
Suite: {suite_name}
Modo: {mode}

---
🎯 **Resumen:**
- Tests ejecutados: {summary['total_tests']}
- Tests aprobados: {summary['tests_passed']} ({summary['pass_rate']:.1f}%)
- Score promedio: {summary['average_score']:.1f}/100
- Score mediano: {summary['median_score']:.1f}/100
- Desviación estándar: {summary['std_dev']:.1f}
- Rango: {summary['min_score']:.1f} - {summary['max_score']:.1f}
"""
        
        return output
    
    def generate_benchmark_report(self, period_days: int = 7) -> str:
        """Generate and return formatted benchmark report"""
        report = self.benchmark_system.generate_report(period_days=period_days)
        return format_benchmark_report(report)


# CLI Interface for testing
def main():
    """Main CLI interface for testing"""
    print("=" * 60)
    print("🤖 ChatBot BMC con Sistema de Entrenamiento")
    print("=" * 60)
    print("\nComandos disponibles:")
    print("- 'MODO ENTRENAMIENTO' - Activar modo de entrenamiento")
    print("- 'MODO PRODUCCIÓN' - Activar modo de producción")
    print("- 'ESTADÍSTICAS' - Ver estadísticas de la sesión")
    print("- 'SALIR ENTRENAMIENTO' - Finalizar sesión de entrenamiento")
    print("- 'BENCHMARK' - Ejecutar benchmark")
    print("- 'REPORTE' - Generar reporte de benchmark")
    print("- 'SALIR' - Salir del programa")
    print("\nEn modo entrenamiento:")
    print(f"- Usa {CorrectionTrigger.CORRECTION_EMOJI.value} o '{CorrectionTrigger.CORRECTION_PREFIX.value}' para correcciones")
    print("=" * 60)
    
    bot = TrainingIntegratedBot()
    session_id = "cli_session_001"
    user_id = "admin"
    
    while True:
        try:
            user_input = input("\n👤 Tú: ").strip()
            
            if not user_input:
                continue
            
            if user_input.upper() == "SALIR":
                print("\n👋 ¡Hasta luego!")
                break
            
            if user_input.upper() == "BENCHMARK":
                print("\n🔄 Ejecutando benchmark...")
                result = bot.run_benchmark()
                print(f"\n🤖 Bot:\n{result}")
                continue
            
            if user_input.upper() == "REPORTE":
                print("\n🔄 Generando reporte...")
                result = bot.generate_benchmark_report()
                print(f"\n🤖 Bot:\n{result}")
                continue
            
            response = bot.process_message(session_id, user_id, user_input)
            print(f"\n🤖 Bot:\n{response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
