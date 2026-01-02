#!/usr/bin/env python3
"""
T0.5: Assessment de motor de cotizaciones
Assesses quotation engine completeness: products, zones, pricing logic, services
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import re


class QuotationEngineAssessor:
    """Assesses quotation engine completeness and functionality"""
    
    def __init__(self, workspace_path: str = "/Users/matias/chatbot2511/chatbot-2311"):
        self.workspace_path = Path(workspace_path)
        self.expected_products = ["Isodec", "Isoroof", "Isopanel", "Isowall", "Isodeck"]
        self.expected_zones = ["Montevideo", "Canelones", "Maldonado", "Rivera"]
    
    def assess(self) -> Dict[str, Any]:
        """Perform complete quotation engine assessment"""
        print("🔍 Starting quotation engine assessment...")
        
        results = {
            "assessment_date": datetime.now().isoformat(),
            "product_catalog": self._assess_product_catalog(),
            "pricing_zones": self._assess_pricing_zones(),
            "dimensions_handling": self._assess_dimensions_handling(),
            "additional_services": self._assess_additional_services(),
            "functionality_gaps": self._identify_functionality_gaps(),
            "summary": {}
        }
        
        # Generate summary
        results["summary"] = self._generate_summary(results)
        
        print("✅ Quotation engine assessment complete")
        return results
    
    def _assess_product_catalog(self) -> Dict[str, Any]:
        """Assess product catalog completeness"""
        catalog = {
            "products_found": [],
            "products_missing": [],
            "products_with_pricing": [],
            "completeness": 0.0
        }
        
        # Find quotation system files
        quotation_files = list(self.workspace_path.rglob("*cotizacion*.py"))
        quotation_files.extend(list(self.workspace_path.rglob("sistema_cotizaciones.py")))
        
        if not quotation_files:
            catalog["error"] = "Quotation system files not found"
            return catalog
        
        # Search for products in code and data files
        all_content = ""
        for qf in quotation_files:
            try:
                all_content += qf.read_text(encoding='utf-8', errors='ignore')
            except:
                pass
        
        # Check JSON files for product data
        json_files = list(self.workspace_path.rglob("*.json"))
        for json_file in json_files:
            try:
                data = json.loads(json_file.read_text(encoding='utf-8', errors='ignore'))
                if isinstance(data, dict):
                    all_content += json.dumps(data).lower()
            except:
                pass
        
        # Check for each product
        for product in self.expected_products:
            if product.lower() in all_content.lower():
                catalog["products_found"].append(product)
            else:
                catalog["products_missing"].append(product)
        
        # Check for pricing data
        pricing_files = list(self.workspace_path.rglob("*precio*.json"))
        pricing_files.extend(list(self.workspace_path.rglob("matriz*.json")))
        
        if pricing_files:
            try:
                pricing_data = json.loads(pricing_files[0].read_text(encoding='utf-8', errors='ignore'))
                if isinstance(pricing_data, dict):
                    for product in catalog["products_found"]:
                        if product.lower() in str(pricing_data).lower():
                            catalog["products_with_pricing"].append(product)
            except:
                pass
        
        # Calculate completeness
        if self.expected_products:
            catalog["completeness"] = round(len(catalog["products_found"]) / len(self.expected_products), 2)
        
        return catalog
    
    def _assess_pricing_zones(self) -> Dict[str, Any]:
        """Assess pricing zone logic"""
        zones = {
            "zones_found": [],
            "zones_missing": [],
            "zone_logic_implemented": False,
            "completeness": 0.0
        }
        
        # Find quotation files
        quotation_files = list(self.workspace_path.rglob("*cotizacion*.py"))
        quotation_files.extend(list(self.workspace_path.rglob("sistema_cotizaciones.py")))
        
        all_content = ""
        for qf in quotation_files:
            try:
                all_content += qf.read_text(encoding='utf-8', errors='ignore')
            except:
                pass
        
        # Check for each zone
        for zone in self.expected_zones:
            if zone.lower() in all_content.lower():
                zones["zones_found"].append(zone)
            else:
                zones["zones_missing"].append(zone)
        
        # Check for zone-based pricing logic
        zone_keywords = ["zona", "zone", "precio", "price", "montevideo", "canelones", "maldonado", "rivera"]
        zone_logic_indicators = sum(1 for keyword in zone_keywords if keyword in all_content.lower())
        zones["zone_logic_implemented"] = zone_logic_indicators >= 3
        
        # Calculate completeness
        if self.expected_zones:
            zones["completeness"] = round(len(zones["zones_found"]) / len(self.expected_zones), 2)
        
        return zones
    
    def _assess_dimensions_handling(self) -> Dict[str, Any]:
        """Assess handling of dimensions (espesores, medidas)"""
        dimensions = {
            "espesor_handling": False,
            "dimension_handling": False,
            "calculation_logic": False,
            "completeness": 0.0
        }
        
        # Find quotation files
        quotation_files = list(self.workspace_path.rglob("*cotizacion*.py"))
        quotation_files.extend(list(self.workspace_path.rglob("sistema_cotizaciones.py")))
        
        all_content = ""
        for qf in quotation_files:
            try:
                all_content += qf.read_text(encoding='utf-8', errors='ignore')
            except:
                pass
        
        # Check for espesor handling
        espesor_keywords = ["espesor", "thickness", "grosor"]
        dimensions["espesor_handling"] = any(keyword in all_content.lower() for keyword in espesor_keywords)
        
        # Check for dimension handling
        dimension_keywords = ["dimension", "medida", "size", "ancho", "alto", "largo", "width", "height", "length"]
        dimensions["dimension_handling"] = any(keyword in all_content.lower() for keyword in dimension_keywords)
        
        # Check for calculation logic
        calc_keywords = ["calcular", "calculate", "precio", "price", "total", "sum", "multiply"]
        dimensions["calculation_logic"] = any(keyword in all_content.lower() for keyword in calc_keywords)
        
        # Calculate completeness
        checks = [dimensions["espesor_handling"], dimensions["dimension_handling"], dimensions["calculation_logic"]]
        dimensions["completeness"] = round(sum(checks) / len(checks), 2)
        
        return dimensions
    
    def _assess_additional_services(self) -> Dict[str, Any]:
        """Assess additional services (flete, instalación)"""
        services = {
            "flete_handling": False,
            "instalacion_handling": False,
            "other_services": [],
            "completeness": 0.0
        }
        
        # Find quotation files
        quotation_files = list(self.workspace_path.rglob("*cotizacion*.py"))
        quotation_files.extend(list(self.workspace_path.rglob("sistema_cotizaciones.py")))
        
        all_content = ""
        for qf in quotation_files:
            try:
                all_content += qf.read_text(encoding='utf-8', errors='ignore')
            except:
                pass
        
        # Check for flete (shipping)
        flete_keywords = ["flete", "shipping", "envio", "delivery", "transporte"]
        services["flete_handling"] = any(keyword in all_content.lower() for keyword in flete_keywords)
        
        # Check for instalación (installation)
        instalacion_keywords = ["instalacion", "installation", "montaje", "setup"]
        services["instalacion_handling"] = any(keyword in all_content.lower() for keyword in instalacion_keywords)
        
        # Check for other services
        other_service_keywords = ["servicio", "service", "adicional", "extra", "opcional"]
        for keyword in other_service_keywords:
            if keyword in all_content.lower():
                services["other_services"].append(keyword)
        
        # Calculate completeness
        checks = [services["flete_handling"], services["instalacion_handling"]]
        services["completeness"] = round(sum(checks) / len(checks), 2) if checks else 0.0
        
        return services
    
    def _identify_functionality_gaps(self) -> List[Dict[str, Any]]:
        """Identify gaps in quotation engine functionality"""
        gaps = []
        
        # This would be enhanced with actual code analysis
        # For now, we'll identify based on assessment results
        
        # Check if quotation files exist
        quotation_files = list(self.workspace_path.rglob("*cotizacion*.py"))
        if not quotation_files:
            gaps.append({
                "type": "critical",
                "description": "Quotation engine files not found",
                "priority": "P0"
            })
        
        return gaps
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate assessment summary"""
        catalog = results.get("product_catalog", {})
        zones = results.get("pricing_zones", {})
        dimensions = results.get("dimensions_handling", {})
        services = results.get("additional_services", {})
        
        overall_completeness = (
            catalog.get("completeness", 0) +
            zones.get("completeness", 0) +
            dimensions.get("completeness", 0) +
            services.get("completeness", 0)
        ) / 4
        
        return {
            "products_completeness": catalog.get("completeness", 0),
            "zones_completeness": zones.get("completeness", 0),
            "dimensions_completeness": dimensions.get("completeness", 0),
            "services_completeness": services.get("completeness", 0),
            "overall_completeness": round(overall_completeness, 2),
            "status": "functional" if overall_completeness >= 0.7 else "needs_improvement",
            "gaps_identified": len(results.get("functionality_gaps", []))
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Assess quotation engine")
    parser.add_argument("--workspace", "-w", default="/Users/matias/chatbot2511/chatbot-2311",
                       help="Workspace path to analyze")
    parser.add_argument("--output", "-o", default="consolidation/discovery/quotation_assessment.json",
                       help="Output file path")
    
    args = parser.parse_args()
    
    # Run assessment
    assessor = QuotationEngineAssessor(workspace_path=args.workspace)
    results = assessor.assess()
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Results saved to: {output_path}")
    print(f"📊 Summary: {results.get('summary', {})}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

