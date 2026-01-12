"""Command-line interface for interactive assessment"""

import asyncio
import json
import sys
from typing import Optional
from pathlib import Path

# Add src directory to path so repo_scorer can be imported
src_path = Path(__file__).resolve().parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from repo_scorer.orchestrator import AssessmentOrchestrator
from repo_scorer.config import RepositoryTool


class Colors:
    """ANSI color codes"""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_header():
    """Print application header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(
        f"{Colors.BOLD}{Colors.CYAN}  Repository Quality Scorer - Powered by Local LLM{Colors.END}"
    )
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}\n")


def select_repository_tool() -> RepositoryTool:
    """Prompt user to select repository tool"""
    print(f"{Colors.BOLD}Select your repository tool:{Colors.END}")
    print(f"  {Colors.BLUE}1.{Colors.END} GitHub")
    print(f"  {Colors.BLUE}2.{Colors.END} GitLab")
    print(f"  {Colors.BLUE}3.{Colors.END} Azure DevOps")
    
    while True:
        choice = input(f"\n{Colors.CYAN}Enter your choice (1-3): {Colors.END}").strip()
        
        if choice == "1":
            return RepositoryTool.GITHUB
        elif choice == "2":
            return RepositoryTool.GITLAB
        elif choice == "3":
            return RepositoryTool.AZURE_DEVOPS
        else:
            print(f"{Colors.RED}Invalid choice. Please enter 1, 2, or 3.{Colors.END}")


async def run_interactive_assessment(model: Optional[str] = None):
    """
    Run interactive assessment in CLI

    Args:
        model: Optional Ollama model name
    """
    print_header()
    
    # Select repository tool
    tool = select_repository_tool()
    tool_name = tool.value.replace("_", " ").title()
    print(f"\n{Colors.GREEN}✓ Selected: {tool_name}{Colors.END}\n")

    orchestrator = AssessmentOrchestrator(tool=tool, model=model)

    # Check system readiness
    print(f"{Colors.YELLOW}Checking system readiness...{Colors.END}")
    is_ready, message = await orchestrator.check_readiness()

    if not is_ready:
        print(f"{Colors.RED}✗ {message}{Colors.END}")
        print(f"\n{Colors.YELLOW}Please ensure:{Colors.END}")
        print("  1. Ollama is installed and running")
        print(f"  2. Model is available: ollama pull {orchestrator.ollama.model}")
        sys.exit(1)

    print(f"{Colors.GREEN}✓ {message}{Colors.END}")
    print(f"{Colors.GREEN}✓ Model: {orchestrator.ollama.model}{Colors.END}")
    print(f"{Colors.GREEN}✓ Total Questions: {len(orchestrator.questions)}{Colors.END}\n")

    print(f"{Colors.BOLD}Instructions:{Colors.END}")
    print(f"  • Answer each question based on your {tool_name} repository practices")
    print("  • Answer naturally (yes, no, partially, unsure, etc.)")
    print("  • The AI will interpret your answer")
    print("  • Scores are calculated automatically\n")

    input(f"{Colors.CYAN}Press Enter to start the assessment...{Colors.END}")
    print()

    question_count = 0
    total_questions = len(orchestrator.questions)

    # Iterate through all questions
    while True:
        question_tuple = orchestrator.get_next_question()

        if question_tuple is None:
            break

        pillar_id, question, pillar_name = question_tuple
        question_count += 1

        # Display progress
        print(f"{Colors.BOLD}{Colors.HEADER}[{question_count}/{total_questions}] {pillar_name}{Colors.END}")
        print(f"{Colors.BOLD}Q: {question.text}{Colors.END}")
        print(f"   (Max score: {question.max_score} points)")

        # Get user answer
        user_answer = input(f"\n{Colors.CYAN}Your answer: {Colors.END}").strip()

        if not user_answer:
            user_answer = "unsure"

        # Process answer
        print(f"{Colors.YELLOW}  Processing...{Colors.END}")
        result = await orchestrator.process_answer(question.id, user_answer)

        # Show result
        classification_color = {
            "yes": Colors.GREEN,
            "partial": Colors.YELLOW,
            "no": Colors.RED,
            "unsure": Colors.YELLOW,
        }.get(result.classification, Colors.END)

        print(
            f"  {classification_color}Classified as: {result.classification}{Colors.END}"
        )
        print(
            f"  {Colors.GREEN}Score: {result.score_earned}/{result.max_score}{Colors.END}"
        )
        print()

    # Finalize assessment
    print(f"\n{Colors.YELLOW}Generating final report...{Colors.END}\n")
    final_result = await orchestrator.finalize_assessment()

    # Display results
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  FINAL RESULTS{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}\n")

    # Final score
    score_color = Colors.GREEN if final_result.final_score >= 70 else (
        Colors.YELLOW if final_result.final_score >= 50 else Colors.RED
    )
    print(
        f"{Colors.BOLD}Final Score: {score_color}{final_result.final_score}/100{Colors.END}\n"
    )

    # Breakdown
    print(f"{Colors.BOLD}Pillar Breakdown:{Colors.END}")
    for pillar_name, (earned, max_score) in final_result.breakdown.items():
        percentage = (earned / max_score * 100) if max_score > 0 else 0
        print(
            f"  • {pillar_name}: {earned}/{max_score} ({percentage:.1f}%)"
        )

    # Summary
    if final_result.summary:
        print(f"\n{Colors.BOLD}AI Summary:{Colors.END}")
        print(f"  {final_result.summary}\n")

    # Ask if user wants JSON export
    print(f"\n{Colors.CYAN}Would you like to export results as JSON? (y/n): {Colors.END}", end="")
    export = input().strip().lower()

    if export == "y":
        filename = "assessment_results.json"
        with open(filename, "w") as f:
            json.dump(final_result.model_dump(), f, indent=2)
        print(f"{Colors.GREEN}✓ Results exported to {filename}{Colors.END}\n")

    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Repository Quality Scorer - Interactive CLI"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Ollama model to use (default: phi-3:mini)",
        default=None,
    )

    args = parser.parse_args()

    try:
        asyncio.run(run_interactive_assessment(model=args.model))
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Assessment cancelled by user.{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
