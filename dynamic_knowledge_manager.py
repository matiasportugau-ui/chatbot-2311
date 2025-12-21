#!/usr/bin/env python3
"""
Dynamic Knowledge Manager
Implements the "Dynamic Truth Layer" architecture with priority-based knowledge retrieval
Level 1 (Priority): dynamic_knowledge.json (Agent corrections)
Level 2 (Static): Original PDFs and manuals
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class KnowledgeQuery:
    """Query for knowledge retrieval"""
    query_text: str
    query_type: str  # "product", "price", "technical", "procedure", "general"
    context: dict[str, Any]
    

@dataclass
class KnowledgeResult:
    """Result from knowledge retrieval"""
    content: str
    source: str  # "dynamic" or "static"
    confidence: float
    metadata: dict[str, Any]
    priority_level: int  # 1 = dynamic, 2 = static


class DynamicKnowledgeManager:
    """Manages dynamic knowledge with priority-based retrieval"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent
        self.dynamic_knowledge_path = self.project_root / "dynamic_knowledge.json"
        self.static_knowledge_path = self.project_root / "conocimiento_consolidado.json"
        
        self.dynamic_knowledge = self._load_dynamic_knowledge()
        self.static_knowledge = self._load_static_knowledge()
        
        print(f"✅ Dynamic Knowledge Manager initialized")
        print(f"   - Dynamic corrections: {self.dynamic_knowledge['metadata']['total_corrections']}")
        print(f"   - Static knowledge loaded: {bool(self.static_knowledge)}")
    
    def _load_dynamic_knowledge(self) -> dict[str, Any]:
        """Load dynamic knowledge from JSON"""
        if not self.dynamic_knowledge_path.exists():
            print(f"⚠️ Dynamic knowledge file not found: {self.dynamic_knowledge_path}")
            return self._create_default_dynamic_knowledge()
        
        try:
            with open(self.dynamic_knowledge_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading dynamic knowledge: {e}")
            return self._create_default_dynamic_knowledge()
    
    def _load_static_knowledge(self) -> dict[str, Any]:
        """Load static knowledge from consolidated JSON"""
        if not self.static_knowledge_path.exists():
            print(f"⚠️ Static knowledge file not found: {self.static_knowledge_path}")
            return {}
        
        try:
            with open(self.static_knowledge_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading static knowledge: {e}")
            return {}
    
    def _create_default_dynamic_knowledge(self) -> dict[str, Any]:
        """Create default dynamic knowledge structure"""
        return {
            "metadata": {
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_corrections": 0,
                "total_conflicts": 0
            },
            "corrections": {
                "products": {},
                "prices": {},
                "technical_specs": {},
                "procedures": {},
                "responses": {}
            },
            "conflicts": [],
            "learning_history": []
        }
    
    def query_knowledge(self, query: KnowledgeQuery) -> KnowledgeResult:
        """
        Query knowledge with priority-based retrieval
        Level 1 (Dynamic) is always checked first
        """
        # First, check dynamic knowledge (Level 1 - Priority)
        dynamic_result = self._search_dynamic_knowledge(query)
        if dynamic_result and dynamic_result.confidence > 0.7:
            return dynamic_result
        
        # If no good match in dynamic, check static knowledge (Level 2)
        static_result = self._search_static_knowledge(query)
        
        # Return the best result, preferring dynamic if available
        if dynamic_result and static_result:
            # If both exist, check for conflicts
            if self._is_conflicting(dynamic_result, static_result):
                print(f"⚠️ Conflict detected between dynamic and static knowledge")
                # Dynamic always wins
                return dynamic_result
            # Return higher confidence
            return dynamic_result if dynamic_result.confidence >= static_result.confidence else static_result
        
        return dynamic_result or static_result or self._create_not_found_result(query)
    
    def _search_dynamic_knowledge(self, query: KnowledgeQuery) -> Optional[KnowledgeResult]:
        """Search in dynamic knowledge (Level 1)"""
        query_lower = query.query_text.lower()
        corrections = self.dynamic_knowledge.get("corrections", {})
        
        # Search by query type
        if query.query_type in corrections:
            category = corrections[query.query_type]
            
            # Simple keyword matching (can be improved with embeddings)
            for key, value in category.items():
                if key.lower() in query_lower or any(kw.lower() in query_lower for kw in value.get("keywords", [])):
                    return KnowledgeResult(
                        content=json.dumps(value, ensure_ascii=False, indent=2),
                        source="dynamic",
                        confidence=0.9,
                        metadata={
                            "correction_id": key,
                            "category": query.query_type,
                            "last_updated": value.get("last_updated", "unknown")
                        },
                        priority_level=1
                    )
        
        return None
    
    def _search_static_knowledge(self, query: KnowledgeQuery) -> Optional[KnowledgeResult]:
        """Search in static knowledge (Level 2)"""
        if not self.static_knowledge:
            return None
        
        query_lower = query.query_text.lower()
        
        # Search in conocimiento_productos
        productos = self.static_knowledge.get("conocimiento_productos", {})
        for producto_id, producto_data in productos.items():
            if producto_id.lower() in query_lower:
                return KnowledgeResult(
                    content=json.dumps(producto_data, ensure_ascii=False, indent=2, default=str),
                    source="static",
                    confidence=0.7,
                    metadata={
                        "producto_id": producto_id,
                        "source": "conocimiento_consolidado.json"
                    },
                    priority_level=2
                )
        
        # Search in interacciones for similar queries
        interacciones = self.static_knowledge.get("interacciones", [])
        for interaccion in interacciones[-50:]:  # Check last 50 interactions
            mensaje = interaccion.get("mensaje_cliente", "").lower()
            if any(word in mensaje for word in query_lower.split() if len(word) > 3):
                return KnowledgeResult(
                    content=interaccion.get("respuesta_agente", ""),
                    source="static",
                    confidence=0.6,
                    metadata={
                        "interaction_id": interaccion.get("id", "unknown"),
                        "source": "conocimiento_consolidado.json"
                    },
                    priority_level=2
                )
        
        return None
    
    def _is_conflicting(self, dynamic_result: KnowledgeResult, static_result: KnowledgeResult) -> bool:
        """Check if two results are conflicting"""
        # Simple heuristic: if content is significantly different
        return len(set(dynamic_result.content.split()) & set(static_result.content.split())) < 5
    
    def _create_not_found_result(self, query: KnowledgeQuery) -> KnowledgeResult:
        """Create a result when knowledge is not found"""
        return KnowledgeResult(
            content=f"No se encontró información específica sobre: {query.query_text}",
            source="none",
            confidence=0.0,
            metadata={"query_type": query.query_type},
            priority_level=3
        )
    
    def add_correction(
        self,
        correction_type: str,
        correction_id: str,
        correction_data: dict[str, Any],
        source_agent: str
    ) -> bool:
        """
        Add a new correction to dynamic knowledge
        
        Args:
            correction_type: "products", "prices", "technical_specs", "procedures", "responses"
            correction_id: Unique identifier for the correction
            correction_data: The correction data
            source_agent: ID of the agent who made the correction
        
        Returns:
            True if successful
        """
        try:
            # Check for conflicts
            if correction_type in self.dynamic_knowledge["corrections"]:
                existing = self.dynamic_knowledge["corrections"][correction_type].get(correction_id)
                if existing:
                    # Conflict detected
                    conflict = {
                        "correction_id": correction_id,
                        "correction_type": correction_type,
                        "existing_data": existing,
                        "new_data": correction_data,
                        "source_agent": source_agent,
                        "timestamp": datetime.now().isoformat(),
                        "status": "pending_resolution"
                    }
                    self.dynamic_knowledge["conflicts"].append(conflict)
                    self.dynamic_knowledge["metadata"]["total_conflicts"] += 1
                    print(f"⚠️ Conflict detected for {correction_type}/{correction_id}")
                    self._save_dynamic_knowledge()
                    return False
            
            # Add correction
            if correction_type not in self.dynamic_knowledge["corrections"]:
                self.dynamic_knowledge["corrections"][correction_type] = {}
            
            correction_data["last_updated"] = datetime.now().isoformat()
            correction_data["source_agent"] = source_agent
            
            self.dynamic_knowledge["corrections"][correction_type][correction_id] = correction_data
            
            # Update metadata
            self.dynamic_knowledge["metadata"]["total_corrections"] += 1
            self.dynamic_knowledge["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Add to learning history
            self.dynamic_knowledge["learning_history"].append({
                "timestamp": datetime.now().isoformat(),
                "action": "correction_added",
                "correction_type": correction_type,
                "correction_id": correction_id,
                "source_agent": source_agent
            })
            
            # Save
            self._save_dynamic_knowledge()
            print(f"✅ Correction added: {correction_type}/{correction_id}")
            return True
        
        except Exception as e:
            print(f"❌ Error adding correction: {e}")
            return False
    
    def resolve_conflict(self, conflict_index: int, resolution: str) -> bool:
        """
        Resolve a conflict by choosing which data to keep
        
        Args:
            conflict_index: Index of conflict in conflicts list
            resolution: "keep_existing", "use_new", or "merge"
        
        Returns:
            True if successful
        """
        try:
            if conflict_index >= len(self.dynamic_knowledge["conflicts"]):
                print(f"❌ Invalid conflict index: {conflict_index}")
                return False
            
            conflict = self.dynamic_knowledge["conflicts"][conflict_index]
            
            if resolution == "use_new":
                # Replace with new data
                self.dynamic_knowledge["corrections"][conflict["correction_type"]][conflict["correction_id"]] = conflict["new_data"]
            elif resolution == "keep_existing":
                # Keep existing, do nothing
                pass
            elif resolution == "merge":
                # Merge both (simple merge, can be improved)
                existing = self.dynamic_knowledge["corrections"][conflict["correction_type"]][conflict["correction_id"]]
                new = conflict["new_data"]
                merged = {**existing, **new, "merged": True, "merge_timestamp": datetime.now().isoformat()}
                self.dynamic_knowledge["corrections"][conflict["correction_type"]][conflict["correction_id"]] = merged
            
            # Mark conflict as resolved
            conflict["status"] = "resolved"
            conflict["resolution"] = resolution
            conflict["resolved_at"] = datetime.now().isoformat()
            
            self._save_dynamic_knowledge()
            print(f"✅ Conflict resolved: {resolution}")
            return True
        
        except Exception as e:
            print(f"❌ Error resolving conflict: {e}")
            return False
    
    def _save_dynamic_knowledge(self):
        """Save dynamic knowledge to file"""
        try:
            with open(self.dynamic_knowledge_path, "w", encoding="utf-8") as f:
                json.dump(self.dynamic_knowledge, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving dynamic knowledge: {e}")
    
    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about the knowledge base"""
        return {
            "dynamic": {
                "total_corrections": self.dynamic_knowledge["metadata"]["total_corrections"],
                "total_conflicts": self.dynamic_knowledge["metadata"]["total_conflicts"],
                "pending_conflicts": len([c for c in self.dynamic_knowledge["conflicts"] if c["status"] == "pending_resolution"]),
                "last_updated": self.dynamic_knowledge["metadata"]["last_updated"]
            },
            "static": {
                "has_data": bool(self.static_knowledge),
                "productos": len(self.static_knowledge.get("conocimiento_productos", {})),
                "interacciones": len(self.static_knowledge.get("interacciones", []))
            }
        }


def main():
    """Test dynamic knowledge manager"""
    manager = DynamicKnowledgeManager()
    
    # Test query
    print("\n=== Testing Knowledge Query ===")
    query = KnowledgeQuery(
        query_text="¿Cuál es el precio del Isodec?",
        query_type="price",
        context={}
    )
    result = manager.query_knowledge(query)
    print(f"Source: {result.source} (Level {result.priority_level})")
    print(f"Confidence: {result.confidence}")
    print(f"Content preview: {result.content[:200]}...")
    
    # Test adding correction
    print("\n=== Testing Add Correction ===")
    success = manager.add_correction(
        correction_type="prices",
        correction_id="isodec_100mm",
        correction_data={
            "product": "Isodec",
            "thickness": "100mm",
            "price_per_m2": 1500.00,
            "currency": "UYU",
            "keywords": ["isodec", "precio", "100mm"]
        },
        source_agent="agent_001"
    )
    print(f"Correction added: {success}")
    
    # Get statistics
    print("\n=== Knowledge Statistics ===")
    stats = manager.get_statistics()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
