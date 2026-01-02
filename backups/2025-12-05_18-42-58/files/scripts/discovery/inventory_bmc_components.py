#!/usr/bin/env python3
"""
T0.3: Inventario de componentes BMC
Inventories BMC-specific components: quotation engine, products, zones, integrations
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import re


class BMCComponentInventory:
    """Inventories BMC-specific components"""
    
    def __init__(self, workspace_path: str = "/Users/matias/chatbot2511/chatbot-2311"):
        self.workspace_path = Path(workspace_path)
        self.products = ["Isodec", "Isoroof", "Isopanel", "Isowall", "Isodeck"]
        self.zones = ["Montevideo", "Canelones", "Maldonado", "Rivera"]
    
    def inventory(self) -> Dict[str, Any]:
        """Perform complete BMC component inventory"""
        print("🔍 Starting BMC component inventory...")
        
        results = {
            "inventory_date": datetime.now().isoformat(),
            "quotation_engine": self._inventory_quotation_engine(),
            "products": self._inventory_products(),
            "zones": self._inventory_zones(),
            "integrations": self._inventory_integrations(),
            "n8n_workflows": self._inventory_n8n_workflows(),
            "summary": {}
        }
        
        # Generate summary
        results["summary"] = self._generate_summary(results)
        
        print("✅ BMC component inventory complete")
        return results
    
    def _inventory_quotation_engine(self) -> Dict[str, Any]:
        """Inventory quotation engine components"""
        engine = {
            "found": False,
            "location": None,
            "files": [],
            "functions": [],
            "status": "not_found"
        }
        
        # Look for quotation system files
        quotation_files = list(self.workspace_path.rglob("*cotizacion*.py"))
        quotation_files.extend(list(self.workspace_path.rglob("*quotation*.py")))
        quotation_files.extend(list(self.workspace_path.rglob("sistema_cotizaciones.py")))
        
        if quotation_files:
            engine["found"] = True
            engine["files"] = [str(f.relative_to(self.workspace_path)) for f in quotation_files]
            engine["location"] = str(quotation_files[0].relative_to(self.workspace_path))
            engine["status"] = "found"
            
            # Try to extract functions
            try:
                content = quotation_files[0].read_text(encoding='utf-8', errors='ignore')
                functions = re.findall(r'def\s+(\w+)', content)
                engine["functions"] = functions[:10]  # First 10 functions
            except:
                pass
        
        return engine
    
    def _inventory_products(self) -> Dict[str, Any]:
        """Inventory BMC products"""
        products_data = {
            "products_found": [],
            "products_missing": [],
            "product_files": [],
            "pricing_data": {}
        }
        
        # Search for product references
        for product in self.products:
            found = False
            product_files = []
            
            # Search in Python files
            for py_file in self.workspace_path.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    if product.lower() in content.lower():
                        found = True
                        product_files.append(str(py_file.relative_to(self.workspace_path)))
                except:
                    pass
            
            # Search in JSON files
            for json_file in self.workspace_path.rglob("*.json"):
                try:
                    content = json_file.read_text(encoding='utf-8', errors='ignore')
                    if product.lower() in content.lower():
                        found = True
                        if json_file not in product_files:
                            product_files.append(str(json_file.relative_to(self.workspace_path)))
                except:
                    pass
            
            if found:
                products_data["products_found"].append(product)
                products_data["product_files"].extend(product_files)
            else:
                products_data["products_missing"].append(product)
        
        # Look for pricing matrix
        pricing_files = list(self.workspace_path.rglob("*precio*.json"))
        pricing_files.extend(list(self.workspace_path.rglob("matriz*.json")))
        
        if pricing_files:
            try:
                pricing_file = pricing_files[0]
                pricing_data = json.loads(pricing_file.read_text(encoding='utf-8', errors='ignore'))
                products_data["pricing_data"]["file"] = str(pricing_file.relative_to(self.workspace_path))
                products_data["pricing_data"]["has_data"] = bool(pricing_data)
            except:
                pass
        
        return products_data
    
    def _inventory_zones(self) -> Dict[str, Any]:
        """Inventory pricing zones"""
        zones_data = {
            "zones_found": [],
            "zones_missing": [],
            "zone_files": []
        }
        
        # Search for zone references
        for zone in self.zones:
            found = False
            zone_files = []
            
            # Search in Python files
            for py_file in self.workspace_path.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    if zone.lower() in content.lower():
                        found = True
                        zone_files.append(str(py_file.relative_to(self.workspace_path)))
                except:
                    pass
            
            # Search in JSON files
            for json_file in self.workspace_path.rglob("*.json"):
                try:
                    content = json_file.read_text(encoding='utf-8', errors='ignore')
                    if zone.lower() in content.lower():
                        found = True
                        if json_file not in zone_files:
                            zone_files.append(str(json_file.relative_to(self.workspace_path)))
                except:
                    pass
            
            if found:
                zones_data["zones_found"].append(zone)
                zones_data["zone_files"].extend(zone_files)
            else:
                zones_data["zones_missing"].append(zone)
        
        return zones_data
    
    def _inventory_integrations(self) -> Dict[str, Any]:
        """Inventory integration components"""
        integrations = {
            "whatsapp": {
                "found": False,
                "files": [],
                "status": "not_found"
            },
            "n8n": {
                "found": False,
                "files": [],
                "status": "not_found"
            },
            "qdrant": {
                "found": False,
                "files": [],
                "status": "not_found"
            },
            "chatwoot": {
                "found": False,
                "files": [],
                "status": "not_found"
            }
        }
        
        # WhatsApp integration
        whatsapp_files = list(self.workspace_path.rglob("*whatsapp*.py"))
        if whatsapp_files:
            integrations["whatsapp"]["found"] = True
            integrations["whatsapp"]["files"] = [str(f.relative_to(self.workspace_path)) for f in whatsapp_files]
            integrations["whatsapp"]["status"] = "found"
        
        # n8n integration
        n8n_files = list(self.workspace_path.rglob("*n8n*.py"))
        if n8n_files:
            integrations["n8n"]["found"] = True
            integrations["n8n"]["files"] = [str(f.relative_to(self.workspace_path)) for f in n8n_files]
            integrations["n8n"]["status"] = "found"
        
        # Qdrant integration
        qdrant_files = list(self.workspace_path.rglob("*qdrant*.py"))
        for py_file in self.workspace_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if "qdrant" in content.lower() or "from qdrant" in content.lower():
                    if py_file not in qdrant_files:
                        qdrant_files.append(py_file)
            except:
                pass
        
        if qdrant_files:
            integrations["qdrant"]["found"] = True
            integrations["qdrant"]["files"] = [str(f.relative_to(self.workspace_path)) for f in qdrant_files]
            integrations["qdrant"]["status"] = "found"
        
        # Chatwoot integration
        chatwoot_files = list(self.workspace_path.rglob("*chatwoot*.py"))
        for py_file in self.workspace_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if "chatwoot" in content.lower():
                    if py_file not in chatwoot_files:
                        chatwoot_files.append(py_file)
            except:
                pass
        
        if chatwoot_files:
            integrations["chatwoot"]["found"] = True
            integrations["chatwoot"]["files"] = [str(f.relative_to(self.workspace_path)) for f in chatwoot_files]
            integrations["chatwoot"]["status"] = "found"
        
        return integrations
    
    def _inventory_n8n_workflows(self) -> Dict[str, Any]:
        """Inventory n8n workflows"""
        workflows = {
            "found": False,
            "workflow_directory": None,
            "workflows": [],
            "main_workflow": None
        }
        
        # Look for n8n workflow directories
        workflow_dirs = [
            self.workspace_path / "n8n_workflows",
            self.workspace_path / "n8n-workflows",
            self.workspace_path / "workflows"
        ]
        
        for wf_dir in workflow_dirs:
            if wf_dir.exists() and wf_dir.is_dir():
                workflows["found"] = True
                workflows["workflow_directory"] = str(wf_dir.relative_to(self.workspace_path))
                
                # Find workflow files
                wf_files = list(wf_dir.rglob("*.json"))
                workflows["workflows"] = [f.name for f in wf_files]
                
                # Look for main orchestrator
                main_wf = list(wf_dir.rglob("*orchestrator*.json"))
                main_wf.extend(list(wf_dir.rglob("*MAIN*.json")))
                if main_wf:
                    workflows["main_workflow"] = main_wf[0].name
                
                break
        
        return workflows
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate inventory summary"""
        quotation = results.get("quotation_engine", {})
        products = results.get("products", {})
        zones = results.get("zones", {})
        integrations = results.get("integrations", {})
        workflows = results.get("n8n_workflows", {})
        
        integrations_found = sum(1 for i in integrations.values() if i.get("found", False))
        
        return {
            "quotation_engine_found": quotation.get("found", False),
            "products_found": len(products.get("products_found", [])),
            "zones_found": len(zones.get("zones_found", [])),
            "integrations_found": integrations_found,
            "n8n_workflows_found": workflows.get("found", False),
            "components_found": (
                (1 if quotation.get("found") else 0) +
                len(products.get("products_found", [])) +
                len(zones.get("zones_found", [])) +
                integrations_found +
                (1 if workflows.get("found") else 0)
            ),
            "status": "completed"
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Inventory BMC components")
    parser.add_argument("--workspace", "-w", default="/Users/matias/chatbot2511/chatbot-2311",
                       help="Workspace path to analyze")
    parser.add_argument("--output", "-o", default="consolidation/discovery/bmc_inventory.json",
                       help="Output file path")
    
    args = parser.parse_args()
    
    # Run inventory
    inventory = BMCComponentInventory(workspace_path=args.workspace)
    results = inventory.inventory()
    
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

