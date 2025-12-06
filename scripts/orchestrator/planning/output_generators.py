"""
Output Generators Module
Generates JSON and Markdown outputs for planning agent
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class OutputGenerators:
    """Generates structured outputs for planning agent"""

    def __init__(self, output_directory: str = "consolidation/pr_analysis"):
        self.output_dir = Path(output_directory)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_analysis_report(self, pr_number: int, analysis: Dict[str, Any],
                                impact: Dict[str, Any], strategy: Dict[str, Any]) -> str:
        """Generate PR Analysis Report (JSON)"""
        report = {
            "pr_number": pr_number,
            "analysis_date": datetime.now().isoformat(),
            "metadata": analysis.get("task_1.1", {}),
            "files_changed": analysis.get("task_1.2", {}),
            "purpose": analysis.get("task_1.3", {}),
            "dependencies": analysis.get("task_1.4", {}),
            "impact_assessment": {
                "architecture": impact.get("task_2.1", {}),
                "consolidation_plan": impact.get("task_2.2", {}),
                "bmc_domain": impact.get("task_2.3", {}),
                "security": impact.get("task_2.4", {})
            },
            "integration_strategy": {
                "merge_strategy": strategy.get("task_3.1", {}),
                "testing_strategy": strategy.get("task_3.2", {}),
                "documentation_updates": strategy.get("task_3.3", {})
            }
        }

        output_file = self.output_dir / f"pr_{pr_number}_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return str(output_file)

    def generate_task_list(self, pr_number: int, plan: Dict[str, Any]) -> str:
        """Generate Detailed Task List (Markdown)"""
        tasks = plan.get("task_4.1", [])
        phase_integration = plan.get("task_4.2", {})

        markdown = f"# Task List for PR #{pr_number}\n\n"
        markdown += f"**Generated:** {datetime.now().isoformat()}\n\n"

        # Group tasks by phase
        tasks_by_phase = phase_integration.get("tasks_by_phase", {})

        for phase, phase_tasks in tasks_by_phase.items():
            markdown += f"## Phase {phase}\n\n"
            for task in phase_tasks:
                markdown += self._format_task(task)

        # Add unassigned tasks
        assigned_task_ids = set()
        for phase_tasks in tasks_by_phase.values():
            assigned_task_ids.update(task.get("task_id") for task in phase_tasks)

        unassigned = [task for task in tasks if task.get("task_id") not in assigned_task_ids]
        if unassigned:
            markdown += "## Unassigned Tasks\n\n"
            for task in unassigned:
                markdown += self._format_task(task)

        output_file = self.output_dir / f"pr_{pr_number}_tasks.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)

        return str(output_file)

    def generate_plan_updates(self, pr_number: int, plan: Dict[str, Any]) -> Optional[str]:
        """Generate Consolidation Plan Updates (Markdown)"""
        phase_integration = plan.get("task_4.2", {})
        phase_updates = phase_integration.get("phase_executor_updates", [])
        new_phase = phase_integration.get("new_phase_required", False)

        if not phase_updates and not new_phase:
            return None  # No updates needed

        markdown = f"# Consolidation Plan Updates for PR #{pr_number}\n\n"
        markdown += f"**Generated:** {datetime.now().isoformat()}\n\n"

        if new_phase:
            markdown += "## New Phase Required\n\n"
            markdown += "A new phase may be required based on the changes in this PR.\n\n"

        if phase_updates:
            markdown += "## Phase Updates\n\n"
            for update in phase_updates:
                markdown += f"### Phase {update.get('phase', 'N/A')}\n\n"
                markdown += f"- **Update Type:** {update.get('update_type', 'N/A')}\n"
                markdown += f"- **Tasks to Add:** {len(update.get('tasks_to_add', []))}\n\n"

        output_file = self.output_dir / f"pr_{pr_number}_plan_updates.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)

        return str(output_file)

    def generate_integration_checklist(self, pr_number: int, strategy: Dict[str, Any]) -> str:
        """Generate Integration Checklist (Markdown)"""
        merge_strategy = strategy.get("task_3.1", {})
        testing_strategy = strategy.get("task_3.2", {})

        markdown = f"# Integration Checklist for PR #{pr_number}\n\n"
        markdown += f"**Generated:** {datetime.now().isoformat()}\n\n"

        markdown += "## Pre-Merge Checks\n\n"
        markdown += "- [ ] Documentation reviewed\n"
        markdown += "- [ ] No conflicts with existing plans\n"
        markdown += "- [ ] Dependencies verified\n"
        markdown += "- [ ] Tests passing\n\n"

        markdown += "## Merge Steps\n\n"
        markdown += f"1. [ ] Review PR changes\n"
        markdown += f"2. [ ] Verify branch compatibility ({merge_strategy.get('target_branch', 'main')})\n"
        markdown += f"3. [ ] Execute merge ({merge_strategy.get('merge_strategy', 'direct_merge')})\n\n"

        markdown += "## Post-Merge Validation\n\n"
        markdown += "- [ ] Documentation accessible\n"
        markdown += "- [ ] Links verified\n"
        markdown += "- [ ] Integration complete\n\n"

        markdown += "## Testing Requirements\n\n"
        if testing_strategy.get("test_updates_required"):
            markdown += "- [ ] Update test suite\n"
        if testing_strategy.get("integration_testing", {}).get("required"):
            markdown += "- [ ] Run integration tests\n"
        if testing_strategy.get("bmc_testing", {}).get("required"):
            markdown += "- [ ] Run BMC-specific tests\n"
        markdown += "- [ ] Documentation review\n"
        markdown += "- [ ] Link validation\n"

        output_file = self.output_dir / f"pr_{pr_number}_integration_checklist.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)

        return str(output_file)

    def _format_task(self, task: Dict[str, Any]) -> str:
        """Format a single task in markdown"""
        markdown = f"- [ ] **{task.get('task_id', 'T?')}:** {task.get('task_name', 'Task')}\n"

        if task.get("script"):
            markdown += f"  - **Script:** `{task['script']}`\n"

        if task.get("action"):
            markdown += f"  - **Action:** {task['action']}\n"

        if task.get("files"):
            files_str = ", ".join(task["files"][:3])
            if len(task["files"]) > 3:
                files_str += f" (+{len(task['files']) - 3} more)"
            markdown += f"  - **Files:** {files_str}\n"

        if task.get("dependencies"):
            markdown += f"  - **Dependencies:** {', '.join(task['dependencies'])}\n"

        if task.get("output"):
            markdown += f"  - **Output:** `{task['output']}`\n"

        if task.get("priority"):
            markdown += f"  - **Priority:** {task['priority']}\n"

        if task.get("agent"):
            markdown += f"  - **Agent:** {task['agent']}\n"

        if task.get("estimated_duration"):
            markdown += f"  - **Estimated Duration:** {task['estimated_duration']}\n"

        if task.get("bmc_context"):
            markdown += f"  - **BMC Context:** {task['bmc_context']}\n"

        markdown += "\n"
        return markdown

