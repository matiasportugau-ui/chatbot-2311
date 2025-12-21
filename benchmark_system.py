#!/usr/bin/env python3
"""
Benchmark System
Evaluates bot performance and tracks learning metrics over time
"""

import json
import statistics
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class BenchmarkTestCase:
    """Test case for benchmarking"""
    test_id: str
    category: str  # "quotation", "product_info", "objection", "technical"
    input_message: str
    expected_keywords: list[str]  # Keywords that should appear in response
    expected_confidence: float  # Minimum expected confidence
    metadata: dict[str, Any]


@dataclass
class BenchmarkResult:
    """Result from a benchmark test"""
    test_id: str
    timestamp: str
    response: str
    confidence: float
    knowledge_source: str  # "dynamic" or "static"
    contains_expected_keywords: bool
    keyword_coverage: float  # Percentage of expected keywords found
    passed: bool
    score: float  # 0-100
    metadata: dict[str, Any]


class BenchmarkSystem:
    """System for evaluating bot performance and tracking learning"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent
        self.results_dir = self.project_root / "data" / "benchmarks"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.test_cases = self._load_test_cases()
        self.historical_results = self._load_historical_results()
        
        print(f"✅ Benchmark System initialized with {len(self.test_cases)} test cases")
    
    def _load_test_cases(self) -> list[BenchmarkTestCase]:
        """Load benchmark test cases"""
        # Pre-configured test scenarios
        test_cases = [
            BenchmarkTestCase(
                test_id="test_001_isodec_price",
                category="quotation",
                input_message="¿Cuál es el precio del Isodec de 100mm?",
                expected_keywords=["precio", "isodec", "100", "mm", "uyu", "$"],
                expected_confidence=0.7,
                metadata={"product": "isodec", "query_type": "price"}
            ),
            BenchmarkTestCase(
                test_id="test_002_isodec_specs",
                category="product_info",
                input_message="¿Qué características tiene el panel Isodec?",
                expected_keywords=["aislante", "térmico", "eps", "conductividad"],
                expected_confidence=0.7,
                metadata={"product": "isodec", "query_type": "technical"}
            ),
            BenchmarkTestCase(
                test_id="test_003_objection_price",
                category="objection",
                input_message="El Isodec me parece muy caro",
                expected_keywords=["valor", "largo plazo", "ahorro", "calidad", "beneficio"],
                expected_confidence=0.6,
                metadata={"objection_type": "price"}
            ),
            BenchmarkTestCase(
                test_id="test_004_installation",
                category="technical",
                input_message="¿Cómo se instala el panel Isodec?",
                expected_keywords=["instalación", "anclajes", "proceso", "colocación"],
                expected_confidence=0.6,
                metadata={"query_type": "installation"}
            ),
            BenchmarkTestCase(
                test_id="test_005_comparison",
                category="product_info",
                input_message="¿Cuál es la diferencia entre Isodec y otros paneles?",
                expected_keywords=["diferencia", "ventaja", "característic", "comparación"],
                expected_confidence=0.6,
                metadata={"query_type": "comparison"}
            )
        ]
        
        return test_cases
    
    def _load_historical_results(self) -> list[dict[str, Any]]:
        """Load historical benchmark results"""
        results_file = self.results_dir / "benchmark_history.json"
        if not results_file.exists():
            return []
        
        try:
            with open(results_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading historical results: {e}")
            return []
    
    def run_benchmark(self, bot_instance, test_cases: Optional[list[str]] = None) -> dict[str, Any]:
        """
        Run benchmark tests on a bot instance
        
        Args:
            bot_instance: Instance of IAConversacionalIntegrada
            test_cases: Optional list of test IDs to run (default: all)
        
        Returns:
            Dictionary with benchmark results and statistics
        """
        print("\n" + "="*60)
        print("🎯 RUNNING BENCHMARK TESTS")
        print("="*60)
        
        # Filter test cases if specified
        if test_cases:
            tests_to_run = [tc for tc in self.test_cases if tc.test_id in test_cases]
        else:
            tests_to_run = self.test_cases
        
        results = []
        
        for test_case in tests_to_run:
            print(f"\n▶️  Running: {test_case.test_id} ({test_case.category})")
            print(f"   Input: {test_case.input_message}")
            
            try:
                # Run the test
                response = bot_instance.procesar_mensaje_multimodal(
                    mensaje=test_case.input_message,
                    cliente_id="benchmark_test",
                    sesion_id=f"benchmark_{datetime.now().timestamp()}",
                    mensaje_tipo="text",
                    metadata=test_case.metadata
                )
                
                # Evaluate the response
                result = self._evaluate_response(test_case, response)
                results.append(result)
                
                # Print result
                status = "✅ PASS" if result.passed else "❌ FAIL"
                print(f"   {status} - Score: {result.score:.1f}/100 - Confidence: {result.confidence:.2f}")
                print(f"   Keywords: {result.keyword_coverage*100:.0f}% - Source: {result.knowledge_source}")
                
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                results.append(BenchmarkResult(
                    test_id=test_case.test_id,
                    timestamp=datetime.now().isoformat(),
                    response=f"Error: {str(e)}",
                    confidence=0.0,
                    knowledge_source="error",
                    contains_expected_keywords=False,
                    keyword_coverage=0.0,
                    passed=False,
                    score=0.0,
                    metadata={"error": str(e)}
                ))
        
        # Calculate statistics
        statistics_data = self._calculate_statistics(results)
        
        # Save results
        self._save_results(results, statistics_data)
        
        # Print summary
        self._print_summary(statistics_data)
        
        return {
            "results": [self._result_to_dict(r) for r in results],
            "statistics": statistics_data,
            "timestamp": datetime.now().isoformat()
        }
    
    def _evaluate_response(self, test_case: BenchmarkTestCase, response: Any) -> BenchmarkResult:
        """Evaluate a bot response against test case expectations"""
        response_text = response.mensaje.lower()
        confidence = getattr(response, "confianza", 0.5)
        
        # Check for expected keywords
        found_keywords = []
        for keyword in test_case.expected_keywords:
            if keyword.lower() in response_text:
                found_keywords.append(keyword)
        
        keyword_coverage = len(found_keywords) / len(test_case.expected_keywords) if test_case.expected_keywords else 1.0
        contains_expected = keyword_coverage >= 0.5  # At least 50% of keywords
        
        # Get knowledge source from personalizacion
        knowledge_source = response.personalizacion.get("knowledge_source", "unknown")
        
        # Calculate score (0-100)
        score = 0.0
        
        # Component 1: Keyword coverage (40 points)
        score += keyword_coverage * 40
        
        # Component 2: Confidence (30 points)
        score += confidence * 30
        
        # Component 3: Response quality (30 points)
        # Check if response is not too short or generic
        if len(response_text) > 50:
            score += 15
        if any(word in response_text for word in ["específicamente", "detalle", "información"]):
            score += 15
        
        # Determine pass/fail
        passed = (
            keyword_coverage >= 0.5 and
            confidence >= test_case.expected_confidence and
            score >= 60
        )
        
        return BenchmarkResult(
            test_id=test_case.test_id,
            timestamp=datetime.now().isoformat(),
            response=response.mensaje,
            confidence=confidence,
            knowledge_source=knowledge_source,
            contains_expected_keywords=contains_expected,
            keyword_coverage=keyword_coverage,
            passed=passed,
            score=score,
            metadata={
                "category": test_case.category,
                "found_keywords": found_keywords,
                "expected_keywords": test_case.expected_keywords
            }
        )
    
    def _calculate_statistics(self, results: list[BenchmarkResult]) -> dict[str, Any]:
        """Calculate statistics from benchmark results"""
        if not results:
            return {}
        
        scores = [r.score for r in results]
        confidences = [r.confidence for r in results]
        keyword_coverages = [r.keyword_coverage for r in results]
        
        # Count by knowledge source
        dynamic_count = len([r for r in results if r.knowledge_source == "dynamic"])
        static_count = len([r for r in results if r.knowledge_source == "static"])
        
        # Pass rate
        passed = len([r for r in results if r.passed])
        pass_rate = passed / len(results) * 100
        
        # Calculate learning rate (if historical data exists)
        learning_rate = self._calculate_learning_rate(results)
        
        return {
            "total_tests": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "pass_rate": pass_rate,
            "average_score": statistics.mean(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "average_confidence": statistics.mean(confidences),
            "average_keyword_coverage": statistics.mean(keyword_coverages) * 100,
            "knowledge_sources": {
                "dynamic": dynamic_count,
                "static": static_count,
                "dynamic_usage_rate": dynamic_count / len(results) * 100 if results else 0
            },
            "learning_metrics": learning_rate
        }
    
    def _calculate_learning_rate(self, current_results: list[BenchmarkResult]) -> dict[str, Any]:
        """
        Calculate learning rate by comparing current results with historical results
        Shows how much the bot has improved over time
        """
        if not self.historical_results:
            return {
                "available": False,
                "message": "No historical data available"
            }
        
        # Get the most recent historical run
        historical_run = self.historical_results[-1] if self.historical_results else None
        if not historical_run:
            return {"available": False}
        
        # Compare scores
        current_avg_score = statistics.mean([r.score for r in current_results])
        historical_avg_score = historical_run.get("statistics", {}).get("average_score", 0)
        
        improvement = current_avg_score - historical_avg_score
        improvement_percentage = (improvement / historical_avg_score * 100) if historical_avg_score > 0 else 0
        
        # Count how many times dynamic knowledge was used vs static
        current_dynamic_rate = len([r for r in current_results if r.knowledge_source == "dynamic"]) / len(current_results) * 100
        historical_dynamic_rate = historical_run.get("statistics", {}).get("knowledge_sources", {}).get("dynamic_usage_rate", 0)
        
        return {
            "available": True,
            "score_improvement": improvement,
            "score_improvement_percentage": improvement_percentage,
            "current_average_score": current_avg_score,
            "historical_average_score": historical_avg_score,
            "dynamic_knowledge_usage_improvement": current_dynamic_rate - historical_dynamic_rate,
            "current_dynamic_usage": current_dynamic_rate,
            "historical_dynamic_usage": historical_dynamic_rate,
            "total_historical_runs": len(self.historical_results)
        }
    
    def _save_results(self, results: list[BenchmarkResult], statistics_data: dict[str, Any]):
        """Save benchmark results to file"""
        # Save to history
        run_data = {
            "timestamp": datetime.now().isoformat(),
            "results": [self._result_to_dict(r) for r in results],
            "statistics": statistics_data
        }
        
        self.historical_results.append(run_data)
        
        # Save history file
        history_file = self.results_dir / "benchmark_history.json"
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(self.historical_results, f, ensure_ascii=False, indent=2)
        
        # Save latest report
        report_file = self.results_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(run_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Results saved to: {report_file}")
    
    def _result_to_dict(self, result: BenchmarkResult) -> dict[str, Any]:
        """Convert BenchmarkResult to dictionary"""
        return {
            "test_id": result.test_id,
            "timestamp": result.timestamp,
            "response": result.response,
            "confidence": result.confidence,
            "knowledge_source": result.knowledge_source,
            "contains_expected_keywords": result.contains_expected_keywords,
            "keyword_coverage": result.keyword_coverage,
            "passed": result.passed,
            "score": result.score,
            "metadata": result.metadata
        }
    
    def _print_summary(self, stats: dict[str, Any]):
        """Print benchmark summary"""
        print("\n" + "="*60)
        print("📊 BENCHMARK SUMMARY")
        print("="*60)
        print(f"Total Tests: {stats['total_tests']}")
        print(f"Passed: {stats['passed']} | Failed: {stats['failed']}")
        print(f"Pass Rate: {stats['pass_rate']:.1f}%")
        print(f"Average Score: {stats['average_score']:.1f}/100")
        print(f"Average Confidence: {stats['average_confidence']:.2f}")
        print(f"Keyword Coverage: {stats['average_keyword_coverage']:.1f}%")
        
        print("\n📚 Knowledge Sources:")
        print(f"   Dynamic: {stats['knowledge_sources']['dynamic']} ({stats['knowledge_sources']['dynamic_usage_rate']:.1f}%)")
        print(f"   Static: {stats['knowledge_sources']['static']}")
        
        learning = stats.get("learning_metrics", {})
        if learning.get("available"):
            print("\n📈 Learning Metrics:")
            print(f"   Score Improvement: {learning['score_improvement']:+.1f} ({learning['score_improvement_percentage']:+.1f}%)")
            print(f"   Dynamic Usage Improvement: {learning['dynamic_knowledge_usage_improvement']:+.1f}%")
            print(f"   Historical Runs: {learning['total_historical_runs']}")
        
        print("="*60)


def main():
    """Test benchmark system"""
    print("Benchmark System - Test Mode")
    print("This would normally run against a bot instance")
    print("For now, just showing the test cases:\n")
    
    benchmark = BenchmarkSystem()
    
    for test_case in benchmark.test_cases:
        print(f"Test ID: {test_case.test_id}")
        print(f"Category: {test_case.category}")
        print(f"Input: {test_case.input_message}")
        print(f"Expected Keywords: {', '.join(test_case.expected_keywords)}")
        print()


if __name__ == "__main__":
    main()
