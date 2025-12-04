#!/usr/bin/env python3
"""
Knowledge Base Populator
Runs conversation scenarios to populate MongoDB knowledge base
"""

import glob
import json
import os
from datetime import datetime
from typing import Any

from simulate_chat import API_URL, MONGODB_URI, SimulatedChat


class KnowledgeBasePopulator:
    """Populates knowledge base with test conversations"""

    def __init__(self, api_url: str = API_URL, mongodb_uri: str = MONGODB_URI):
        self.chat = SimulatedChat(api_url, mongodb_uri)
        self.stats = {
            "total_scenarios": 0,
            "total_messages": 0,
            "successful": 0,
            "failed": 0,
            "conversations_created": 0,
        }

    def load_scenarios(self, scenarios_dir: str = "test_scenarios") -> list[dict[str, Any]]:
        """Load all scenario files from directory"""
        scenarios = []

        if not os.path.exists(scenarios_dir):
            print(f"❌ Scenarios directory not found: {scenarios_dir}")
            return scenarios

        # Find all JSON files
        pattern = os.path.join(scenarios_dir, "*.json")
        files = glob.glob(pattern)

        for file_path in files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    file_scenarios = json.load(f)
                    # Handle both single scenario and list of scenarios
                    if isinstance(file_scenarios, list):
                        scenarios.extend(file_scenarios)
                    else:
                        scenarios.append(file_scenarios)
                print(
                    f"✅ Loaded {len(file_scenarios) if isinstance(file_scenarios, list) else 1} scenarios from {os.path.basename(file_path)}"
                )
            except Exception as e:
                print(f"⚠️ Error loading {file_path}: {e}")

        return scenarios

    def run_scenario(self, scenario: dict[str, Any], verbose: bool = True) -> dict[str, Any]:
        """Run a single scenario"""
        scenario_name = scenario.get("name", "Unnamed")
        phone = scenario.get("phone", "+59891234567")
        messages = scenario.get("messages", [])

        if verbose:
            print(f"\n{'=' * 70}")
            print(f"📋 Scenario: {scenario_name}")
            print(f"{'=' * 70}")
            if scenario.get("description"):
                print(f"Description: {scenario.get('description')}")
            print()

        # Start new session
        self.chat.start_session(phone)

        results = {
            "scenario_name": scenario_name,
            "phone": phone,
            "messages_sent": 0,
            "messages_successful": 0,
            "messages_failed": 0,
            "responses": [],
        }

        # Process each message
        for i, message in enumerate(messages, 1):
            if not message.strip():
                continue

            if verbose:
                print(f"\n[{i}/{len(messages)}] Processing message...")

            result = self.chat.send_message(message)

            results["messages_sent"] += 1

            if result.get("error"):
                results["messages_failed"] += 1
                if verbose:
                    print(f"❌ Error: {result.get('error')}")
            else:
                results["messages_successful"] += 1
                results["responses"].append(
                    {
                        "message": message,
                        "response": result.get("mensaje", ""),
                        "type": result.get("tipo", ""),
                        "confidence": result.get("confianza", 0),
                    }
                )

            # Small delay between messages
            import time

            time.sleep(0.5)

        # Export conversation
        filename = f"kb_populated_{scenario_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.chat.export_conversation(filename)

        if verbose:
            print(f"\n✅ Scenario complete: {scenario_name}")
            print(
                f"   Messages: {results['messages_successful']}/{results['messages_sent']} successful"
            )

        return results

    def populate(
        self, scenarios_dir: str = "test_scenarios", verbose: bool = True
    ) -> dict[str, Any]:
        """Populate knowledge base with all scenarios"""
        print("=" * 70)
        print("📚 Knowledge Base Populator")
        print("=" * 70)
        print(f"Scenarios directory: {scenarios_dir}")
        print(f"API URL: {API_URL}")
        print(f"MongoDB URI: {MONGODB_URI}")
        print()

        # Load scenarios
        scenarios = self.load_scenarios(scenarios_dir)

        if not scenarios:
            print("❌ No scenarios found")
            return self.stats

        self.stats["total_scenarios"] = len(scenarios)
        print(f"📋 Found {len(scenarios)} scenarios to run")
        print()

        # Run each scenario
        all_results = []
        for i, scenario in enumerate(scenarios, 1):
            try:
                print(f"\n[{i}/{len(scenarios)}] Running scenario...")
                result = self.run_scenario(scenario, verbose)
                all_results.append(result)

                self.stats["total_messages"] += result["messages_sent"]
                self.stats["successful"] += result["messages_successful"]
                self.stats["failed"] += result["messages_failed"]
                self.stats["conversations_created"] += 1

            except Exception as e:
                print(f"❌ Error running scenario: {e}")
                self.stats["failed"] += 1

        # Save results
        results_file = f"kb_population_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "stats": self.stats,
                    "scenarios": all_results,
                    "timestamp": datetime.now().isoformat(),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        # Print summary
        print("\n" + "=" * 70)
        print("📊 Population Summary")
        print("=" * 70)
        print(f"Total scenarios: {self.stats['total_scenarios']}")
        print(f"Total messages: {self.stats['total_messages']}")
        print(f"Successful: {self.stats['successful']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Conversations created: {self.stats['conversations_created']}")
        print(f"\nResults saved to: {results_file}")

        # Show knowledge base stats
        kb_stats = self.chat.get_knowledge_base_stats()
        if not kb_stats.get("error"):
            print("\n📚 Knowledge Base Statistics:")
            print(f"   Total interactions: {kb_stats.get('total_interactions', 0)}")
            if kb_stats.get("by_type"):
                print("   By type:")
                for type_name, count in kb_stats["by_type"].items():
                    print(f"     - {type_name}: {count}")

        return self.stats


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Populate knowledge base with test scenarios")
    parser.add_argument(
        "--scenarios",
        "-s",
        default="test_scenarios",
        help="Directory containing scenario JSON files",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Quiet mode (less verbose output)"
    )

    args = parser.parse_args()

    populator = KnowledgeBasePopulator()
    populator.populate(args.scenarios, verbose=not args.quiet)


if __name__ == "__main__":
    main()
