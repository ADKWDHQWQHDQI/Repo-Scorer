"""
Test script to demonstrate AI-powered question importance weighting

This script loads questions and shows how the LLM assigns importance weights
based on how critical each governance practice is for repository health.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(src_path))

from repo_scorer.orchestrator import AssessmentOrchestrator
from repo_scorer.config import RepositoryTool


async def demonstrate_importance_weighting():
    """Demonstrate the importance weighting feature"""
    
    print("\n" + "=" * 70)
    print("  AI-Powered Question Importance Weighting Demonstration")
    print("=" * 70 + "\n")
    
    # Create orchestrator
    print("📋 Initializing orchestrator for GitHub...")
    orchestrator = AssessmentOrchestrator(tool=RepositoryTool.GITHUB)
    
    # Check readiness (this triggers importance weight assignment)
    print("🔍 Checking system readiness (this will assign importance weights)...\n")
    is_ready, message = await orchestrator.check_readiness()
    
    if not is_ready:
        print(f"❌ {message}")
        return
    
    print(f"✅ {message}\n")
    
    # Display questions with their importance weights
    print("=" * 70)
    print("  QUESTIONS WITH AI-ASSIGNED IMPORTANCE WEIGHTS")
    print("=" * 70 + "\n")
    
    for pillar_id, pillar in orchestrator.pillars.items():
        print(f"\n📊 {pillar.name}")
        print(f"   Total Weight: {pillar.total_weight} points\n")
        
        # Sort questions by importance (highest first)
        sorted_questions = sorted(pillar.questions, key=lambda q: q.importance, reverse=True)
        
        for i, question in enumerate(sorted_questions, 1):
            # Visual importance indicator
            stars = "⭐" * min(int(question.importance / 2), 5)
            
            # Color coding based on importance
            if question.importance >= 8:
                importance_label = "🔴 CRITICAL"
            elif question.importance >= 7:
                importance_label = "🟡 VERY IMPORTANT"
            elif question.importance >= 5:
                importance_label = "🟢 IMPORTANT"
            else:
                importance_label = "🔵 NICE TO HAVE"
            
            print(f"  {i}. {importance_label} {stars} ({question.importance:.1f}/10)")
            print(f"     Max Score: {question.max_score} points")
            print(f"     Q: {question.text}")
            print()
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("  IMPORTANCE DISTRIBUTION SUMMARY")
    print("=" * 70 + "\n")
    
    all_questions = [q for pillar in orchestrator.pillars.values() for q in pillar.questions]
    
    critical = [q for q in all_questions if q.importance >= 8]
    very_important = [q for q in all_questions if 7 <= q.importance < 8]
    important = [q for q in all_questions if 5 <= q.importance < 7]
    nice_to_have = [q for q in all_questions if q.importance < 5]
    
    print(f"🔴 Critical (8-10):        {len(critical)} questions")
    print(f"🟡 Very Important (7-8):   {len(very_important)} questions")
    print(f"🟢 Important (5-7):        {len(important)} questions")
    print(f"🔵 Nice to Have (1-5):     {len(nice_to_have)} questions\n")
    
    avg_importance = sum(q.importance for q in all_questions) / len(all_questions)
    print(f"📊 Average Importance:     {avg_importance:.2f}/10")
    
    # Show score distribution
    total_score = sum(q.max_score for q in all_questions)
    critical_score = sum(q.max_score for q in critical)
    print(f"\n💯 Total Points:           {total_score}")
    print(f"🎯 Points for Critical:    {critical_score:.1f} ({critical_score/total_score*100:.1f}%)")
    
    print("\n" + "=" * 70)
    print("✅ Importance weighting complete!")
    print("=" * 70 + "\n")
    
    print("💡 Key Benefits:")
    print("   • Critical practices (security, branch protection) get higher weights")
    print("   • Fair scoring based on actual impact on repository health")
    print("   • AI evaluates each question's importance automatically")
    print("   • No manual weight assignment needed\n")


if __name__ == "__main__":
    asyncio.run(demonstrate_importance_weighting())
