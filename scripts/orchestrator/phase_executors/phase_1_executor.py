"""
Phase 1 Executor: Repository Analysis
Direct execution pattern for repository consolidation analysis
"""

from .base_executor import BaseExecutor
from typing import List, Dict, Any
import json
import sys
from pathlib import Path

# Add orchestrator to path for imports
ORCHESTRATOR_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ORCHESTRATOR_DIR.parent.parent))


class Phase1Executor(BaseExecutor):
    """Executes Phase 1: Repository Analysis for Consolidation"""

    def __init__(self, phase: int, state_manager):
        super().__init__(phase, state_manager)

    def execute(self) -> List[str]:
        """Execute Phase 1: Repository Analysis"""
        self.log_info("Starting Phase 1: Repository Analysis")

        # Create Phase 1 specific output directory
        output_dir = self.ensure_output_dir("consolidation/phase1")
        
        # Get workspace path
        workspace_path = str(Path.cwd())
        
        # T1.1: Analyze GitHub repositories
        self.log_info("T1.1: Analyzing repositories...")
        repo_analysis_file = self._execute_t1_1(output_dir, workspace_path)
        if repo_analysis_file:
            self.add_output(repo_analysis_file)
        
        # T1.2: Analyze local workspace
        self.log_info("T1.2: Analyzing workspace...")
        workspace_analysis_file = self._execute_t1_2(output_dir, workspace_path)
        if workspace_analysis_file:
            self.add_output(workspace_analysis_file)
        
        # T1.3: Identify technologies
        self.log_info("T1.3: Identifying technologies...")
        technologies_file = self._execute_t1_3(output_dir, workspace_path, repo_analysis_file)
        if technologies_file:
            self.add_output(technologies_file)
        
        # T1.4: Map dependencies
        self.log_info("T1.4: Mapping dependencies...")
        dependencies_file = self._execute_t1_4(output_dir, workspace_path, repo_analysis_file)
        if dependencies_file:
            self.add_output(dependencies_file)

        self.log_success("Phase 1 completed successfully")
        return self.collect_outputs()

    def _enhance_existing_analysis(self, existing_file: Path, data: Dict[str, Any]):
        """Enhance existing analysis with Phase 1 consolidation context"""
        try:
            # Add consolidation-specific metadata
            if "consolidation_strategy" not in data:
                data["consolidation_strategy"] = {
                    "target_structure": "monorepo",
                    "consolidation_approach": "merge_into_monorepo"
                }

            data["phase"] = 1
            data["enhanced_at"] = self._get_timestamp()

            with open(existing_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log_error(f"Error enhancing analysis: {e}")

    def _enhance_with_phase_0_data(self, repo_data: Dict[str, Any], phase_0_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance repository analysis with Phase 0 discovery data"""
        # Add Phase 0 insights
        if "phase_0_insights" not in repo_data:
            repo_data["phase_0_insights"] = {}
        
        if "repository_analysis" in phase_0_data:
            repo_data["phase_0_insights"]["repository_analysis"] = phase_0_data["repository_analysis"]
        
        if "workspace_analysis" in phase_0_data:
            repo_data["phase_0_insights"]["workspace_analysis"] = phase_0_data["workspace_analysis"]
        
        if "bmc_inventory" in phase_0_data:
            repo_data["phase_0_insights"]["bmc_inventory"] = phase_0_data["bmc_inventory"]
        
        # Perform consolidation-specific analysis
        if "repository_analysis" in phase_0_data:
            consolidation_analysis = self._analyze_for_consolidation(phase_0_data["repository_analysis"])
            repo_data["consolidation_analysis"] = consolidation_analysis
        
        return repo_data

    def _create_new_analysis(self, output_dir: Path, phase_0_data: Dict[str, Any]):
        """Create new analysis if none exists"""
        if phase_0_data:
            # Use Phase 0 data to create comprehensive analysis
            consolidation_analysis = self._create_analysis_from_phase_0(phase_0_data)
        else:
            # Fallback to basic analysis
            consolidation_analysis = self._create_basic_analysis()
        
        output_file = output_dir / "repository_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(consolidation_analysis, f, indent=2, ensure_ascii=False)
        self.add_output(str(output_file))

    def _create_analysis_from_phase_0(self, phase_0_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Phase 1 analysis from Phase 0 data"""
        repo_analysis = phase_0_data.get("repository_analysis", {})
        
        # Extract repository list
        repos = repo_analysis.get("repositories", [])
        if isinstance(repos, list):
            repo_list = repos
        elif isinstance(repos, dict):
            repo_list = list(repos.keys())
        else:
            repo_list = []

        # Perform consolidation analysis
        consolidation_analysis = self._analyze_for_consolidation(repo_analysis)

        return {
            "phase": 1,
            "timestamp": self._get_timestamp(),
            "repositories": repo_list,
            "consolidation_strategy": {
                "target_structure": "monorepo",
                "consolidation_approach": "merge_into_monorepo"
            },
            "consolidation_analysis": consolidation_analysis,
            "phase_0_data_used": True,
            "source": "Phase 0 discovery outputs"
        }

    def _analyze_for_consolidation(self, phase_0_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze repositories specifically for consolidation"""
        repos = phase_0_data.get("repositories", [])

        return {
            "total_repositories": len(repos),
            "consolidation_readiness": {
                "ready": [],
                "needs_review": [],
                "blockers": []
            },
            "estimated_effort": "medium",
            "risks": []
        }

    def _create_basic_analysis(self) -> Dict[str, Any]:
        """Create basic repository analysis if Phase 0 data not available"""
        return {
            "phase": 1,
            "timestamp": self._get_timestamp(),
            "repositories": [
                "bmc-cotizacion-inteligente",
                "chatbot-2311",
                "ChatBOT",
                "background-agents",
                "Dashboard-bmc"
            ],
            "consolidation_strategy": {
                "target_structure": "monorepo",
                "consolidation_approach": "merge_into_monorepo"
            },
            "note": "Basic analysis - Phase 0 data not available"
        }

    def _execute_t1_1(self, output_dir: Path, workspace_path: str) -> str:
        """T1.1: Analyze GitHub repositories"""
        try:
            # Import analysis functions directly
            script_path = Path(workspace_path) / "scripts" / "discovery" / "analyze_repositories.py"
            
            if not script_path.exists():
                self.log_error(f"Analysis script not found: {script_path}")
                return None
            
            # Execute the script
            success, output = self.run_script(str(script_path), cwd=workspace_path)
            
            if success:
                # The script outputs to consolidation/reports, move/copy to phase1
                source_file = Path(workspace_path) / "consolidation" / "reports" / "repository_analysis.json"
                target_file = output_dir / "repository_analysis.json"
                
                if source_file.exists():
                    # Copy and update path
                    import shutil
                    shutil.copy2(source_file, target_file)
                    
                    # Update the file to reflect Phase 1 structure
                    with open(target_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    data["phase"] = 1
                    data["task"] = "T1.1 - Repository Analysis"
                    data["output_path"] = str(target_file)
                    
                    with open(target_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    self.log_success(f"T1.1 completed: {target_file}")
                    return str(target_file)
                else:
                    self.log_error("Repository analysis script did not generate output file")
                    return None
            else:
                self.log_error(f"T1.1 failed: {output}")
                return None
                
        except Exception as e:
            self.log_error(f"Error executing T1.1: {e}")
            return None
    
    def _execute_t1_2(self, output_dir: Path, workspace_path: str) -> str:
        """T1.2: Analyze local workspace"""
        try:
            script_path = Path(workspace_path) / "scripts" / "discovery" / "analyze_workspace.py"
            
            if not script_path.exists():
                self.log_error(f"Workspace analysis script not found: {script_path}")
                return None
            
            # Execute the script
            success, output = self.run_script(str(script_path), cwd=workspace_path)
            
            if success:
                # The script outputs to consolidation/reports, move/copy to phase1
                source_file = Path(workspace_path) / "consolidation" / "reports" / "workspace_analysis.json"
                target_file = output_dir / "workspace_analysis.json"
                
                if source_file.exists():
                    import shutil
                    shutil.copy2(source_file, target_file)
                    
                    # Update the file to reflect Phase 1 structure
                    with open(target_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    data["phase"] = 1
                    data["task"] = "T1.2 - Workspace Analysis"
                    data["output_path"] = str(target_file)
                    
                    with open(target_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    self.log_success(f"T1.2 completed: {target_file}")
                    return str(target_file)
                else:
                    self.log_error("Workspace analysis script did not generate output file")
                    return None
            else:
                self.log_error(f"T1.2 failed: {output}")
                return None
                
        except Exception as e:
            self.log_error(f"Error executing T1.2: {e}")
            return None
    
    def _execute_t1_3(self, output_dir: Path, workspace_path: str, repo_analysis_file: str = None) -> str:
        """T1.3: Identify technologies"""
        try:
            technologies_data = {
                "phase": 1,
                "task": "T1.3 - Technology Identification",
                "timestamp": self._get_timestamp(),
                "workspace": workspace_path
            }
            
            # Try to extract from repository analysis if available
            if repo_analysis_file and Path(repo_analysis_file).exists():
                try:
                    with open(repo_analysis_file, 'r', encoding='utf-8') as f:
                        repo_data = json.load(f)
                    
                    if "technologies" in repo_data:
                        technologies_data["technologies"] = repo_data["technologies"]
                    else:
                        # Extract from structure
                        technologies_data["technologies"] = self._extract_technologies_from_analysis(repo_data)
                except Exception as e:
                    self.log_error(f"Error reading repository analysis: {e}")
            
            # If not available, analyze directly
            if "technologies" not in technologies_data or not technologies_data["technologies"]:
                # Import and call analyze_technologies function
                script_path = Path(workspace_path) / "scripts" / "discovery" / "analyze_repositories.py"
                if script_path.exists():
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("analyze_repos", script_path)
                    analyze_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(analyze_module)
                    
                    technologies = analyze_module.analyze_technologies(workspace_path)
                    technologies_data["technologies"] = technologies
            
            # Save technologies file
            technologies_file = output_dir / "technologies.json"
            with open(technologies_file, 'w', encoding='utf-8') as f:
                json.dump(technologies_data, f, indent=2, ensure_ascii=False)
            
            self.log_success(f"T1.3 completed: {technologies_file}")
            return str(technologies_file)
            
        except Exception as e:
            self.log_error(f"Error executing T1.3: {e}")
            return None
    
    def _execute_t1_4(self, output_dir: Path, workspace_path: str, repo_analysis_file: str = None) -> str:
        """T1.4: Map dependencies"""
        try:
            dependencies_data = {
                "phase": 1,
                "task": "T1.4 - Dependency Mapping",
                "timestamp": self._get_timestamp(),
                "workspace": workspace_path
            }
            
            # Try to extract from repository analysis if available
            if repo_analysis_file and Path(repo_analysis_file).exists():
                try:
                    with open(repo_analysis_file, 'r', encoding='utf-8') as f:
                        repo_data = json.load(f)
                    
                    if "dependencies" in repo_data:
                        dependencies_data["dependencies"] = repo_data["dependencies"]
                    else:
                        # Extract from structure
                        dependencies_data["dependencies"] = self._extract_dependencies_from_analysis(repo_data)
                except Exception as e:
                    self.log_error(f"Error reading repository analysis: {e}")
            
            # If not available, analyze directly
            if "dependencies" not in dependencies_data or not dependencies_data["dependencies"]:
                # Import and call analyze_dependencies function
                script_path = Path(workspace_path) / "scripts" / "discovery" / "analyze_repositories.py"
                if script_path.exists():
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("analyze_repos", script_path)
                    analyze_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(analyze_module)
                    
                    dependencies = analyze_module.analyze_dependencies(workspace_path)
                    dependencies_data["dependencies"] = dependencies
            
            # Save dependencies file
            dependencies_file = output_dir / "dependencies.json"
            with open(dependencies_file, 'w', encoding='utf-8') as f:
                json.dump(dependencies_data, f, indent=2, ensure_ascii=False)
            
            self.log_success(f"T1.4 completed: {dependencies_file}")
            return str(dependencies_file)
            
        except Exception as e:
            self.log_error(f"Error executing T1.4: {e}")
            return None
    
    def _extract_technologies_from_analysis(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technologies from repository analysis data"""
        technologies = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "services": [],
            "tools": []
        }
        
        if "technologies" in repo_data:
            return repo_data["technologies"]
        
        # Extract from structure if available
        if "structure" in repo_data:
            structure = repo_data["structure"]
            if structure.get("python_files"):
                technologies["languages"].append("Python")
            if structure.get("docker_files"):
                technologies["tools"].append("Docker")
        
        return technologies
    
    def _extract_dependencies_from_analysis(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract dependencies from repository analysis data"""
        if "dependencies" in repo_data:
            return repo_data["dependencies"]
        
        return {
            "python": [],
            "node": [],
            "system": []
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

