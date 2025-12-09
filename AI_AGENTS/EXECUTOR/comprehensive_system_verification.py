#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive System Verification and Troubleshooting Agent
===========================================================

This agent performs step-by-step verification of all system components,
identifies issues, and attempts to fix them automatically.

Features:
- Complete system health check
- AI integration verification (OpenAI, Groq, Gemini, Grok)
- Bot response fluency testing
- Automated troubleshooting
- Extensive reporting
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

# Add project root to path
_current_dir = Path(__file__).parent
_project_root = _current_dir.parent.parent
sys.path.insert(0, str(_project_root))

try:
    from model_integrator import get_model_integrator
    MODEL_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_INTEGRATOR_AVAILABLE = False

try:
    from ejecutor_completo import (
        print_success, print_warning, print_error,
        print_info, print_header
    )
except ImportError:
    def print_success(text): print(f"✅ {text}")
    def print_warning(text): print(f"⚠️  {text}")
    def print_error(text): print(f"❌ {text}")
    def print_info(text): print(f"ℹ️  {text}")
    def print_header(text): print(f"\n{'='*80}\n{text}\n{'='*80}\n")


class VerificationStatus(Enum):
    """Verification status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


@dataclass
class VerificationResult:
    """Result of a verification step"""
    name: str
    status: VerificationStatus
    message: str
    details: Dict
    fix_applied: bool = False
    fix_message: str = ""


class ComprehensiveSystemVerifier:
    """Comprehensive system verification and troubleshooting"""
    
    def __init__(self):
        self.results: List[VerificationResult] = []
        self.model_integrator = None
        self.fixes_applied = []
        
        if MODEL_INTEGRATOR_AVAILABLE:
            try:
                self.model_integrator = get_model_integrator()
            except Exception as e:
                print_warning(f"Model integrator not available: {e}")
    
    def verify_environment_variables(self) -> VerificationResult:
        """Verify environment variables are set"""
        print_info("Verificando variables de entorno...")
        
        required_vars = {
            'OPENAI_API_KEY': 'OpenAI',
            'GROQ_API_KEY': 'Groq',
            'GEMINI_API_KEY': 'Gemini',
            'XAI_API_KEY': 'Grok/xAI'
        }
        
        found = []
        missing = []
        
        for var, name in required_vars.items():
            value = os.getenv(var) or os.getenv(var.replace('_API_KEY', '_KEY'))
            if value and value.strip() and value != f"TU_{name.upper()}_KEY":
                found.append(name)
            else:
                missing.append(name)
        
        if found:
            status = VerificationStatus.PASS if len(found) >= 1 else VerificationStatus.WARNING
            message = f"Variables encontradas: {', '.join(found)}"
            if missing:
                message += f" | Faltantes: {', '.join(missing)}"
        else:
            status = VerificationStatus.FAIL
            message = "No se encontraron variables de entorno configuradas"
        
        return VerificationResult(
            name="Environment Variables",
            status=status,
            message=message,
            details={'found': found, 'missing': missing}
        )
    
    def verify_model_integrator(self) -> VerificationResult:
        """Verify model integrator is working"""
        print_info("Verificando Model Integrator...")
        
        if not MODEL_INTEGRATOR_AVAILABLE:
            return VerificationResult(
                name="Model Integrator",
                status=VerificationStatus.FAIL,
                message="Model integrator no está disponible",
                details={}
            )
        
        if not self.model_integrator:
            return VerificationResult(
                name="Model Integrator",
                status=VerificationStatus.FAIL,
                message="Model integrator no inicializado",
                details={}
            )
        
        try:
            available_models = self.model_integrator.list_available_models()
            enabled_models = [m for m in available_models if m.get('enabled', False)]
            
            if enabled_models:
                providers = [m['provider'] for m in enabled_models]
                return VerificationResult(
                    name="Model Integrator",
                    status=VerificationStatus.PASS,
                    message=f"Modelos disponibles: {', '.join(providers)}",
                    details={'models': enabled_models}
                )
            else:
                return VerificationResult(
                    name="Model Integrator",
                    status=VerificationStatus.WARNING,
                    message="Model integrator disponible pero sin modelos habilitados",
                    details={'available': available_models}
                )
        except Exception as e:
            return VerificationResult(
                name="Model Integrator",
                status=VerificationStatus.FAIL,
                message=f"Error verificando model integrator: {e}",
                details={'error': str(e)}
            )
    
    def test_ai_providers(self) -> List[VerificationResult]:
        """Test each AI provider individually"""
        print_info("Probando proveedores de IA...")
        
        results = []
        providers = ['openai', 'groq', 'gemini', 'grok']
        
        for provider in providers:
            print_info(f"  Probando {provider}...")
            result = self._test_provider(provider)
            results.append(result)
            time.sleep(0.5)  # Rate limiting
        
        return results
    
    def _test_provider(self, provider: str) -> VerificationResult:
        """Test a specific provider"""
        if not self.model_integrator:
            return VerificationResult(
                name=f"Provider {provider}",
                status=VerificationStatus.SKIP,
                message="Model integrator no disponible",
                details={}
            )
        
        try:
            # Try to generate a simple response
            test_prompt = "Responde solo 'OK' si puedes leer esto."
            
            response = self.model_integrator.generate(
                prompt=test_prompt,
                provider=provider,
                max_tokens=10,
                temperature=0.1
            )
            
            if response and 'content' in response:
                content = response['content'].strip().upper()
                if 'OK' in content or len(content) > 0:
                    return VerificationResult(
                        name=f"Provider {provider}",
                        status=VerificationStatus.PASS,
                        message=f"{provider} responde correctamente",
                        details={'response': content[:50]}
                    )
                else:
                    return VerificationResult(
                        name=f"Provider {provider}",
                        status=VerificationStatus.WARNING,
                        message=f"{provider} responde pero con formato inesperado",
                        details={'response': content}
                    )
            else:
                return VerificationResult(
                    name=f"Provider {provider}",
                    status=VerificationStatus.FAIL,
                    message=f"{provider} no generó respuesta válida",
                    details={'response': response}
                )
        except Exception as e:
            error_msg = str(e)
            # Check if it's an API key issue
            if 'api key' in error_msg.lower() or '401' in error_msg or 'unauthorized' in error_msg.lower():
                return VerificationResult(
                    name=f"Provider {provider}",
                    status=VerificationStatus.FAIL,
                    message=f"{provider}: API key inválida o no configurada",
                    details={'error': error_msg}
                )
            else:
                return VerificationResult(
                    name=f"Provider {provider}",
                    status=VerificationStatus.FAIL,
                    message=f"{provider}: Error - {error_msg[:100]}",
                    details={'error': error_msg}
                )
    
    def verify_bot_integration(self) -> VerificationResult:
        """Verify bot is properly integrated with AI"""
        print_info("Verificando integración del bot...")
        
        try:
            from ia_conversacional_integrada import IAConversacionalIntegrada
            
            bot = IAConversacionalIntegrada()
            
            # Check if AI is enabled
            if not bot.use_ai:
                return VerificationResult(
                    name="Bot Integration",
                    status=VerificationStatus.FAIL,
                    message="Bot no tiene IA habilitada",
                    details={'use_ai': False}
                )
            
            # Check model integrator
            has_integrator = bot.model_integrator is not None
            has_openai_fallback = bot.openai_client is not None
            
            if has_integrator or has_openai_fallback:
                return VerificationResult(
                    name="Bot Integration",
                    status=VerificationStatus.PASS,
                    message="Bot integrado correctamente con IA",
                    details={
                        'has_integrator': has_integrator,
                        'has_openai_fallback': has_openai_fallback
                    }
                )
            else:
                return VerificationResult(
                    name="Bot Integration",
                    status=VerificationStatus.FAIL,
                    message="Bot no tiene integración de IA configurada",
                    details={}
                )
        except Exception as e:
            return VerificationResult(
                name="Bot Integration",
                status=VerificationStatus.FAIL,
                message=f"Error verificando bot: {e}",
                details={'error': str(e)}
            )
    
    def test_bot_response_fluency(self) -> VerificationResult:
        """Test bot response fluency"""
        print_info("Probando fluidez de respuestas del bot...")
        
        try:
            from ia_conversacional_integrada import IAConversacionalIntegrada
            
            bot = IAConversacionalIntegrada()
            
            if not bot.use_ai:
                return VerificationResult(
                    name="Bot Fluency",
                    status=VerificationStatus.SKIP,
                    message="Bot no tiene IA habilitada, no se puede probar fluidez",
                    details={}
                )
            
            # Test with a simple question
            test_message = "Hola, ¿qué productos tienen disponibles?"
            
            try:
                response = bot.procesar_mensaje(
                    mensaje=test_message,
                    cliente_id="test_verification",
                    sesion_id="test_session"
                )
                
                if response and hasattr(response, 'mensaje'):
                    message = response.mensaje
                    if message and len(message) > 10:
                        return VerificationResult(
                            name="Bot Fluency",
                            status=VerificationStatus.PASS,
                            message="Bot responde fluidamente",
                            details={
                                'response_length': len(message),
                                'preview': message[:100]
                            }
                        )
                    else:
                        return VerificationResult(
                            name="Bot Fluency",
                            status=VerificationStatus.WARNING,
                            message="Bot responde pero con mensaje muy corto",
                            details={'response': message}
                        )
                else:
                    return VerificationResult(
                        name="Bot Fluency",
                        status=VerificationStatus.FAIL,
                        message="Bot no generó respuesta válida",
                        details={'response': response}
                    )
            except Exception as e:
                return VerificationResult(
                    name="Bot Fluency",
                    status=VerificationStatus.FAIL,
                    message=f"Error probando bot: {e}",
                    details={'error': str(e)}
                )
        except Exception as e:
            return VerificationResult(
                name="Bot Fluency",
                status=VerificationStatus.FAIL,
                message=f"Error inicializando bot: {e}",
                details={'error': str(e)}
            )
    
    def verify_dependencies(self) -> VerificationResult:
        """Verify Python dependencies"""
        print_info("Verificando dependencias Python...")
        
        required = [
            'openai', 'groq', 'google.genai', 'pymongo',
            'fastapi', 'uvicorn', 'python-dotenv'
        ]
        
        found = []
        missing = []
        
        for dep in required:
            try:
                if dep == 'google.genai':
                    __import__('google.genai')
                elif dep == 'google.generativeai':
                    __import__('google.generativeai')
                else:
                    __import__(dep)
                found.append(dep)
            except ImportError:
                missing.append(dep)
        
        if not missing:
            status = VerificationStatus.PASS
            message = f"Todas las dependencias instaladas ({len(found)})"
        elif len(found) > len(missing):
            status = VerificationStatus.WARNING
            message = f"{len(found)}/{len(required)} dependencias instaladas"
        else:
            status = VerificationStatus.FAIL
            message = f"Faltan {len(missing)} dependencias críticas"
        
        return VerificationResult(
            name="Dependencies",
            status=status,
            message=message,
            details={'found': found, 'missing': missing}
        )
    
    def verify_files(self) -> VerificationResult:
        """Verify required files exist"""
        print_info("Verificando archivos del sistema...")
        
        required_files = [
            'ia_conversacional_integrada.py',
            'model_integrator.py',
            'sistema_cotizaciones.py',
            'base_conocimiento_dinamica.py',
            'ejecutor_completo.py'
        ]
        
        found = []
        missing = []
        
        for file in required_files:
            if Path(file).exists():
                found.append(file)
            else:
                missing.append(file)
        
        if not missing:
            status = VerificationStatus.PASS
            message = f"Todos los archivos presentes ({len(found)})"
        else:
            status = VerificationStatus.FAIL
            message = f"Faltan {len(missing)} archivos"
        
        return VerificationResult(
            name="Required Files",
            status=status,
            message=message,
            details={'found': found, 'missing': missing}
        )
    
    def attempt_fixes(self, result: VerificationResult) -> bool:
        """Attempt to automatically fix issues"""
        if result.status == VerificationStatus.PASS:
            return False
        
        fix_applied = False
        fix_message = ""
        
        # Fix environment variables
        if result.name == "Environment Variables" and result.status == VerificationStatus.FAIL:
            # Try to load from .env files
            try:
                from dotenv import load_dotenv
                if Path('.env.local').exists():
                    load_dotenv('.env.local', override=True)
                    fix_message = "Variables cargadas desde .env.local"
                    fix_applied = True
                elif Path('.env').exists():
                    load_dotenv('.env', override=True)
                    fix_message = "Variables cargadas desde .env"
                    fix_applied = True
            except:
                pass
        
        # Fix dependencies
        if result.name == "Dependencies" and result.missing:
            missing = result.details.get('missing', [])
            if missing:
                try:
                    print_info(f"Intentando instalar dependencias faltantes...")
                    # This would require user confirmation, so we just note it
                    fix_message = f"Dependencias a instalar: {', '.join(missing)}"
                except:
                    pass
        
        if fix_applied:
            result.fix_applied = True
            result.fix_message = fix_message
            self.fixes_applied.append({
                'check': result.name,
                'fix': fix_message,
                'timestamp': datetime.now().isoformat()
            })
        
        return fix_applied
    
    def run_full_verification(self) -> Dict:
        """Run complete verification"""
        print_header("VERIFICACIÓN COMPLETA DEL SISTEMA")
        
        # Step 1: Environment
        result = self.verify_environment_variables()
        self.results.append(result)
        if result.status != VerificationStatus.PASS:
            self.attempt_fixes(result)
        
        # Step 2: Dependencies
        result = self.verify_dependencies()
        self.results.append(result)
        
        # Step 3: Files
        result = self.verify_files()
        self.results.append(result)
        
        # Step 4: Model Integrator
        result = self.verify_model_integrator()
        self.results.append(result)
        
        # Step 5: Test AI Providers
        provider_results = self.test_ai_providers()
        self.results.extend(provider_results)
        
        # Step 6: Bot Integration
        result = self.verify_bot_integration()
        self.results.append(result)
        
        # Step 7: Bot Fluency
        result = self.test_bot_response_fluency()
        self.results.append(result)
        
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """Generate comprehensive report"""
        passed = sum(1 for r in self.results if r.status == VerificationStatus.PASS)
        failed = sum(1 for r in self.results if r.status == VerificationStatus.FAIL)
        warnings = sum(1 for r in self.results if r.status == VerificationStatus.WARNING)
        skipped = sum(1 for r in self.results if r.status == VerificationStatus.SKIP)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_checks': len(self.results),
                'passed': passed,
                'failed': failed,
                'warnings': warnings,
                'skipped': skipped,
                'success_rate': f"{(passed / len(self.results) * 100):.1f}%" if self.results else "0%"
            },
            'results': [
                {
                    'name': r.name,
                    'status': r.status.value,
                    'message': r.message,
                    'details': r.details,
                    'fix_applied': r.fix_applied,
                    'fix_message': r.fix_message
                }
                for r in self.results
            ],
            'fixes_applied': self.fixes_applied,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on results"""
        recommendations = []
        
        failed_checks = [r for r in self.results if r.status == VerificationStatus.FAIL]
        warning_checks = [r for r in self.results if r.status == VerificationStatus.WARNING]
        
        # Check for API key issues
        api_key_issues = [r for r in failed_checks if 'api key' in r.message.lower()]
        if api_key_issues:
            recommendations.append(
                "Configurar API keys válidas en .env o .env.local para los proveedores de IA"
            )
        
        # Check for dependency issues
        dep_issues = [r for r in failed_checks if r.name == "Dependencies"]
        if dep_issues:
            recommendations.append(
                "Instalar dependencias faltantes: pip install -r requirements.txt"
            )
        
        # Check for bot integration issues
        bot_issues = [r for r in failed_checks if 'bot' in r.name.lower()]
        if bot_issues:
            recommendations.append(
                "Verificar que el bot esté correctamente inicializado con model_integrator"
            )
        
        # Check for provider-specific issues
        provider_issues = [r for r in failed_checks if 'Provider' in r.name]
        if len(provider_issues) > 0:
            recommendations.append(
                "Al menos un proveedor de IA debe estar funcionando para el bot"
            )
        
        if not recommendations:
            recommendations.append("Sistema en buen estado. Continuar monitoreo.")
        
        return recommendations
    
    def print_report(self, report: Dict):
        """Print report to console"""
        print_header("REPORTE DE VERIFICACIÓN")
        
        summary = report['summary']
        print(f"\nResumen:")
        print(f"  Total de verificaciones: {summary['total_checks']}")
        print_success(f"  ✅ Pasadas: {summary['passed']}")
        if summary['failed'] > 0:
            print_error(f"  ❌ Fallidas: {summary['failed']}")
        if summary['warnings'] > 0:
            print_warning(f"  ⚠️  Advertencias: {summary['warnings']}")
        print(f"  Tasa de éxito: {summary['success_rate']}")
        
        print(f"\nDetalles:")
        for result in report['results']:
            status_icon = {
                'pass': '✅',
                'fail': '❌',
                'warning': '⚠️',
                'skip': '⏭️'
            }.get(result['status'], '❓')
            
            print(f"\n  {status_icon} {result['name']}")
            print(f"     {result['message']}")
            if result['fix_applied']:
                print_success(f"     🔧 Fix aplicado: {result['fix_message']}")
        
        if report['fixes_applied']:
            print(f"\n🔧 Fixes Aplicados:")
            for fix in report['fixes_applied']:
                print(f"  • {fix['check']}: {fix['fix']}")
        
        if report['recommendations']:
            print(f"\n💡 Recomendaciones:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
    
    def save_report(self, report: Dict, filename: Optional[str] = None) -> Path:
        """Save report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_verification_report_{timestamp}.json"
        
        filepath = Path(filename)
        filepath.write_text(json.dumps(report, indent=2, default=str), encoding='utf-8')
        return filepath


def main():
    """Main entry point"""
    verifier = ComprehensiveSystemVerifier()
    
    print_header("AGENTE DE VERIFICACIÓN Y SOLUCIÓN AUTOMÁTICA")
    print_info("Este agente verificará todos los componentes del sistema")
    print_info("e intentará solucionar problemas automáticamente\n")
    
    # Run verification
    report = verifier.run_full_verification()
    
    # Print report
    verifier.print_report(report)
    
    # Save report
    report_path = verifier.save_report(report)
    print()
    print_success(f"Reporte guardado en: {report_path}")
    
    # Return exit code based on results
    if report['summary']['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

