#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark System for Training & Evaluation
Evaluates the effectiveness of training corrections and knowledge improvements
"""

import json
import datetime
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict
import hashlib


@dataclass
class BenchmarkMetric:
    """A single benchmark metric"""
    name: str
    category: str  # quality, accuracy, efficiency, user_satisfaction
    value: float
    unit: str
    timestamp: datetime.datetime
    context: Dict[str, Any]


@dataclass
class BenchmarkTest:
    """A benchmark test scenario"""
    id: str
    name: str
    description: str
    input_query: str
    expected_output: str
    category: str
    difficulty: int  # 1-5
    tags: List[str]


@dataclass
class BenchmarkResult:
    """Result of a benchmark test"""
    test_id: str
    timestamp: datetime.datetime
    mode: str  # before_training, after_training
    actual_output: str
    score: float  # 0-100
    metrics: Dict[str, float]
    passed: bool
    notes: str


@dataclass
class BenchmarkReport:
    """Comprehensive benchmark report"""
    id: str
    timestamp: datetime.datetime
    period_start: datetime.datetime
    period_end: datetime.datetime
    total_tests: int
    tests_passed: int
    average_score: float
    improvement_rate: float
    category_scores: Dict[str, float]
    recommendations: List[str]


class BenchmarkSystem:
    """System for benchmarking and evaluating bot performance"""
    
    def __init__(self, benchmark_path: str = "data/benchmarks"):
        """
        Initialize benchmark system
        
        Args:
            benchmark_path: Path to store benchmark data
        """
        self.benchmark_path = Path(benchmark_path)
        self.benchmark_path.mkdir(parents=True, exist_ok=True)
        
        # Test suites
        self.test_suites: Dict[str, List[BenchmarkTest]] = {}
        self.test_results: List[BenchmarkResult] = []
        
        # Metrics tracking
        self.metrics_history: List[BenchmarkMetric] = []
        
        # Load existing benchmarks
        self._load_benchmark_data()
        self._create_default_test_suite()
    
    def _load_benchmark_data(self):
        """Load existing benchmark data"""
        tests_file = self.benchmark_path / "test_suites.json"
        results_file = self.benchmark_path / "test_results.json"
        
        if tests_file.exists():
            with open(tests_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Load test suites
        
        if results_file.exists():
            with open(results_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Load results
    
    def _save_benchmark_data(self):
        """Save benchmark data"""
        tests_file = self.benchmark_path / "test_suites.json"
        results_file = self.benchmark_path / "test_results.json"
        
        # Save test suites
        with open(tests_file, 'w', encoding='utf-8') as f:
            data = {
                suite_name: [asdict(test) for test in tests]
                for suite_name, tests in self.test_suites.items()
            }
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        # Save results
        with open(results_file, 'w', encoding='utf-8') as f:
            data = {
                'results': [asdict(r) for r in self.test_results[-1000:]]  # Keep last 1000
            }
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def _create_default_test_suite(self):
        """Create default test suite for BMC chatbot"""
        default_tests = [
            BenchmarkTest(
                id="test_001",
                name="Cotización básica Isodec",
                description="Cliente solicita cotización básica para Isodec",
                input_query="Hola, necesito una cotización para panel Isodec de 100mm, 10m x 5m",
                expected_output="precio, espesor correcto, dimensiones correctas, datos faltantes solicitados",
                category="cotizacion",
                difficulty=2,
                tags=["isodec", "cotizacion", "basico"]
            ),
            BenchmarkTest(
                id="test_002",
                name="Consulta de productos",
                description="Cliente pregunta sobre tipos de productos disponibles",
                input_query="¿Qué tipos de aislantes térmicos tienen disponibles?",
                expected_output="menciona Isodec, Poliestireno, Lana de Roca, características breves",
                category="informacion",
                difficulty=1,
                tags=["productos", "informacion"]
            ),
            BenchmarkTest(
                id="test_003",
                name="Objeción de precio",
                description="Cliente encuentra el precio elevado",
                input_query="El precio me parece muy alto, ¿tienen algo más económico?",
                expected_output="justificación de valor, alternativas, beneficios",
                category="objeciones",
                difficulty=3,
                tags=["precio", "objeciones", "negociacion"]
            ),
            BenchmarkTest(
                id="test_004",
                name="Especificaciones técnicas",
                description="Cliente pregunta detalles técnicos específicos",
                input_query="¿Cuál es la conductividad térmica del Isodec de 100mm?",
                expected_output="datos técnicos correctos, explicación clara",
                category="tecnico",
                difficulty=4,
                tags=["tecnico", "especificaciones"]
            ),
            BenchmarkTest(
                id="test_005",
                name="Datos incompletos",
                description="Cliente da información parcial para cotización",
                input_query="Quiero Isodec",
                expected_output="solicita espesor, dimensiones, datos del cliente",
                category="validacion",
                difficulty=2,
                tags=["validacion", "datos_faltantes"]
            ),
        ]
        
        self.test_suites["default"] = default_tests
        self._save_benchmark_data()
    
    def add_test(self, suite_name: str, test: BenchmarkTest):
        """Add a test to a suite"""
        if suite_name not in self.test_suites:
            self.test_suites[suite_name] = []
        
        self.test_suites[suite_name].append(test)
        self._save_benchmark_data()
    
    def run_benchmark(
        self,
        suite_name: str,
        bot_response_func: callable,
        mode: str = "after_training"
    ) -> Dict[str, Any]:
        """
        Run a benchmark test suite
        
        Args:
            suite_name: Name of test suite to run
            bot_response_func: Function to get bot response
            mode: 'before_training' or 'after_training'
            
        Returns:
            Summary of benchmark results
        """
        if suite_name not in self.test_suites:
            return {
                "success": False,
                "message": f"Test suite '{suite_name}' not found"
            }
        
        tests = self.test_suites[suite_name]
        results = []
        
        for test in tests:
            # Get bot response
            actual_output = bot_response_func(test.input_query)
            
            # Score the response
            score, metrics = self._score_response(test, actual_output)
            
            # Create result
            result = BenchmarkResult(
                test_id=test.id,
                timestamp=datetime.datetime.now(),
                mode=mode,
                actual_output=actual_output,
                score=score,
                metrics=metrics,
                passed=score >= 70,  # 70% threshold
                notes=""
            )
            
            results.append(result)
            self.test_results.append(result)
        
        self._save_benchmark_data()
        
        # Calculate summary
        summary = self._calculate_summary(results)
        
        return {
            "success": True,
            "suite_name": suite_name,
            "mode": mode,
            "summary": summary,
            "results": [asdict(r) for r in results]
        }
    
    def _score_response(
        self,
        test: BenchmarkTest,
        actual_output: str
    ) -> Tuple[float, Dict[str, float]]:
        """
        Score a response against expected output
        
        Args:
            test: BenchmarkTest object
            actual_output: Actual bot response
            
        Returns:
            Tuple of (overall_score, detailed_metrics)
        """
        metrics = {}
        
        # 1. Keyword presence (40% of score)
        expected_keywords = test.expected_output.lower().split(", ")
        keyword_score = sum(
            1 for keyword in expected_keywords
            if keyword in actual_output.lower()
        ) / len(expected_keywords) * 100
        metrics["keyword_presence"] = keyword_score
        
        # 2. Length appropriateness (20% of score)
        output_length = len(actual_output)
        if output_length < 50:
            length_score = 50  # Too short
        elif output_length > 500:
            length_score = 70  # Maybe too long
        else:
            length_score = 100  # Good length
        metrics["length_appropriateness"] = length_score
        
        # 3. Completeness (40% of score)
        # Check if response addresses the category appropriately
        completeness_score = self._evaluate_completeness(test, actual_output)
        metrics["completeness"] = completeness_score
        
        # Calculate overall score
        overall_score = (
            keyword_score * 0.4 +
            length_score * 0.2 +
            completeness_score * 0.4
        )
        
        return overall_score, metrics
    
    def _evaluate_completeness(self, test: BenchmarkTest, output: str) -> float:
        """Evaluate if response is complete for the test category"""
        output_lower = output.lower()
        
        # Category-specific checks
        if test.category == "cotizacion":
            checks = [
                "precio" in output_lower or "costo" in output_lower or "$" in output,
                any(dim in output_lower for dim in ["metros", "m²", "dimensiones"]),
                any(prod in output_lower for prod in ["isodec", "poliestireno", "lana"])
            ]
            return (sum(checks) / len(checks)) * 100
        
        elif test.category == "informacion":
            checks = [
                len(output) > 100,  # Substantial response
                any(prod in output_lower for prod in ["isodec", "poliestireno", "lana"]),
                "características" in output_lower or "propiedades" in output_lower
            ]
            return (sum(checks) / len(checks)) * 100
        
        elif test.category == "validacion":
            checks = [
                "necesito" in output_lower or "requiero" in output_lower,
                any(data in output_lower for data in ["espesor", "dimensiones", "nombre", "teléfono"]),
                "?" in output  # Asks questions
            ]
            return (sum(checks) / len(checks)) * 100
        
        else:
            # Generic completeness
            return 75.0 if len(output) > 50 else 50.0
    
    def _calculate_summary(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        if not results:
            return {}
        
        scores = [r.score for r in results]
        passed = [r for r in results if r.passed]
        
        return {
            "total_tests": len(results),
            "tests_passed": len(passed),
            "pass_rate": (len(passed) / len(results)) * 100,
            "average_score": statistics.mean(scores),
            "median_score": statistics.median(scores),
            "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
            "min_score": min(scores),
            "max_score": max(scores)
        }
    
    def compare_performance(
        self,
        before_results: List[BenchmarkResult],
        after_results: List[BenchmarkResult]
    ) -> Dict[str, Any]:
        """
        Compare performance before and after training
        
        Args:
            before_results: Results before training
            after_results: Results after training
            
        Returns:
            Comparison analysis
        """
        before_summary = self._calculate_summary(before_results)
        after_summary = self._calculate_summary(after_results)
        
        improvement = {
            "average_score": after_summary["average_score"] - before_summary["average_score"],
            "pass_rate": after_summary["pass_rate"] - before_summary["pass_rate"],
            "tests_improved": 0,
            "tests_degraded": 0,
            "tests_unchanged": 0
        }
        
        # Compare individual tests
        before_by_id = {r.test_id: r for r in before_results}
        after_by_id = {r.test_id: r for r in after_results}
        
        for test_id in before_by_id.keys():
            if test_id in after_by_id:
                before_score = before_by_id[test_id].score
                after_score = after_by_id[test_id].score
                
                if after_score > before_score + 5:  # 5 point threshold
                    improvement["tests_improved"] += 1
                elif after_score < before_score - 5:
                    improvement["tests_degraded"] += 1
                else:
                    improvement["tests_unchanged"] += 1
        
        return {
            "before_training": before_summary,
            "after_training": after_summary,
            "improvement": improvement,
            "overall_assessment": self._assess_improvement(improvement)
        }
    
    def _assess_improvement(self, improvement: Dict[str, Any]) -> str:
        """Assess overall improvement"""
        avg_improvement = improvement["average_score"]
        
        if avg_improvement >= 15:
            return "Mejora Excelente - El entrenamiento ha tenido un impacto significativo"
        elif avg_improvement >= 10:
            return "Mejora Notable - El entrenamiento ha sido efectivo"
        elif avg_improvement >= 5:
            return "Mejora Moderada - Se observan mejoras en el desempeño"
        elif avg_improvement >= 0:
            return "Mejora Ligera - El entrenamiento tuvo impacto limitado"
        else:
            return "Degradación - El desempeño empeoró, revisar cambios"
    
    def generate_report(
        self,
        period_days: int = 7,
        include_recommendations: bool = True
    ) -> BenchmarkReport:
        """
        Generate comprehensive benchmark report
        
        Args:
            period_days: Number of days to include in report
            include_recommendations: Include improvement recommendations
            
        Returns:
            BenchmarkReport object
        """
        period_start = datetime.datetime.now() - datetime.timedelta(days=period_days)
        period_end = datetime.datetime.now()
        
        # Filter results to period
        period_results = [
            r for r in self.test_results
            if period_start <= r.timestamp <= period_end
        ]
        
        if not period_results:
            # Return empty report
            return BenchmarkReport(
                id=hashlib.md5(f"{period_end}".encode()).hexdigest()[:12],
                timestamp=datetime.datetime.now(),
                period_start=period_start,
                period_end=period_end,
                total_tests=0,
                tests_passed=0,
                average_score=0.0,
                improvement_rate=0.0,
                category_scores={},
                recommendations=[]
            )
        
        # Calculate statistics
        summary = self._calculate_summary(period_results)
        
        # Calculate category scores
        category_scores = self._calculate_category_scores(period_results)
        
        # Calculate improvement rate
        improvement_rate = self._calculate_improvement_rate(period_results)
        
        # Generate recommendations
        recommendations = []
        if include_recommendations:
            recommendations = self._generate_recommendations(
                period_results,
                category_scores
            )
        
        report = BenchmarkReport(
            id=hashlib.md5(f"{period_end}".encode()).hexdigest()[:12],
            timestamp=datetime.datetime.now(),
            period_start=period_start,
            period_end=period_end,
            total_tests=summary["total_tests"],
            tests_passed=summary["tests_passed"],
            average_score=summary["average_score"],
            improvement_rate=improvement_rate,
            category_scores=category_scores,
            recommendations=recommendations
        )
        
        # Save report
        report_file = self.benchmark_path / f"report_{report.id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False, default=str)
        
        return report
    
    def _calculate_category_scores(
        self,
        results: List[BenchmarkResult]
    ) -> Dict[str, float]:
        """Calculate average scores by category"""
        category_scores = defaultdict(list)
        
        # Need to map results back to tests
        test_by_id = {}
        for suite in self.test_suites.values():
            for test in suite:
                test_by_id[test.id] = test
        
        for result in results:
            if result.test_id in test_by_id:
                category = test_by_id[result.test_id].category
                category_scores[category].append(result.score)
        
        return {
            category: statistics.mean(scores)
            for category, scores in category_scores.items()
        }
    
    def _calculate_improvement_rate(
        self,
        results: List[BenchmarkResult]
    ) -> float:
        """Calculate improvement rate over time"""
        if len(results) < 2:
            return 0.0
        
        # Sort by timestamp
        sorted_results = sorted(results, key=lambda r: r.timestamp)
        
        # Compare first half to second half
        mid_point = len(sorted_results) // 2
        first_half = sorted_results[:mid_point]
        second_half = sorted_results[mid_point:]
        
        first_avg = statistics.mean([r.score for r in first_half])
        second_avg = statistics.mean([r.score for r in second_half])
        
        return second_avg - first_avg
    
    def _generate_recommendations(
        self,
        results: List[BenchmarkResult],
        category_scores: Dict[str, float]
    ) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Identify weak categories
        for category, score in category_scores.items():
            if score < 70:
                recommendations.append(
                    f"🎯 Categoría '{category}' necesita mejora (score: {score:.1f}). "
                    f"Considera agregar más ejemplos de entrenamiento para esta categoría."
                )
        
        # Check for consistency
        scores = [r.score for r in results]
        if len(scores) > 1:
            std_dev = statistics.stdev(scores)
            if std_dev > 20:
                recommendations.append(
                    f"⚠️ Alta variabilidad en resultados (std dev: {std_dev:.1f}). "
                    "El bot responde de manera inconsistente, considera estandarizar respuestas."
                )
        
        # Check for failed tests
        failed = [r for r in results if not r.passed]
        if len(failed) > len(results) * 0.3:  # More than 30% failed
            recommendations.append(
                f"🚨 {len(failed)} de {len(results)} tests fallaron. "
                "Revisa los casos de falla y agrega correcciones específicas."
            )
        
        return recommendations
    
    def export_metrics(self, output_file: str):
        """Export metrics to file for external analysis"""
        output_path = Path(output_file)
        
        data = {
            "test_suites": {
                suite_name: [asdict(test) for test in tests]
                for suite_name, tests in self.test_suites.items()
            },
            "recent_results": [
                asdict(r) for r in self.test_results[-100:]
            ],
            "metrics_history": [
                asdict(m) for m in self.metrics_history[-1000:]
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def format_benchmark_report(report: BenchmarkReport) -> str:
    """Format benchmark report for display"""
    output = f"""
📊 **Reporte de Benchmark**
ID: {report.id}
Período: {report.period_start.strftime('%Y-%m-%d')} - {report.period_end.strftime('%Y-%m-%d')}

---
🎯 **Resumen General:**
- Tests ejecutados: {report.total_tests}
- Tests aprobados: {report.tests_passed} ({report.tests_passed/report.total_tests*100:.1f}%)
- Score promedio: {report.average_score:.1f}/100
- Tasa de mejora: {report.improvement_rate:+.1f} puntos

---
📈 **Scores por Categoría:**
"""
    
    for category, score in report.category_scores.items():
        emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
        output += f"{emoji} {category}: {score:.1f}/100\n"
    
    if report.recommendations:
        output += "\n---\n💡 **Recomendaciones:**\n"
        for i, rec in enumerate(report.recommendations, 1):
            output += f"\n{i}. {rec}"
    
    return output
