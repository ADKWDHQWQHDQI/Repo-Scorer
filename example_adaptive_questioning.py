"""
Example demonstrating AI-driven adaptive questioning in action

This script shows how the enhanced assessment adapts based on user answers.
"""

import asyncio
from repo_scorer.orchestrator import AssessmentOrchestrator
from repo_scorer.config import RepositoryTool


async def example_adaptive_assessment():
    """Demonstrate adaptive questioning with different answer types"""
    
    print("=" * 70)
    print("AI-DRIVEN ADAPTIVE QUESTIONING DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Create orchestrator
    orchestrator = AssessmentOrchestrator(RepositoryTool.GITHUB)
    
    # Check system readiness
    ready, message = await orchestrator.check_readiness()
    if not ready:
        print(f"❌ System not ready: {message}")
        return
    
    print(f"✅ {message}")
    print()
    
    # Example 1: Complete answer → No follow-up
    print("=" * 70)
    print("SCENARIO 1: Complete Answer (No Follow-up Expected)")
    print("=" * 70)
    
    question1 = orchestrator.get_next_question()
    if question1:
        pillar_id, question, pillar_name = question1
        print(f"\n📋 Question: {question.text}")
        print(f"🎯 Question ID: {question.id}")
        
        # User gives complete answer
        user_answer1 = "Yes, we have full CI/CD with GitHub Actions running automatically on every pull request with required status checks before merge."
        print(f"💬 User Answer: {user_answer1}")
        
        result1 = await orchestrator.process_answer(question.id, user_answer1)
        print(f"\n🤖 AI Classification: {result1.classification}")
        print(f"📊 Score: {result1.score_earned}/{result1.max_score}")
        print(f"🔍 Follow-ups Pending: {len(orchestrator.pending_follow_ups)}")
        
        if orchestrator.pending_follow_ups:
            print("   → AI decided: Follow-up needed")
        else:
            print("   → AI decided: Answer is complete, skip follow-up ✓")
    
    print()
    
    # Example 2: Partial answer → Follow-up triggered
    print("=" * 70)
    print("SCENARIO 2: Partial Answer (Follow-up Expected)")
    print("=" * 70)
    
    question2 = orchestrator.get_next_question()
    if question2:
        pillar_id, question, pillar_name = question2
        print(f"\n📋 Question: {question.text}")
        print(f"🎯 Question ID: {question.id}")
        
        # User gives vague/partial answer
        user_answer2 = "Sort of, we have some protection on main branch but not consistent."
        print(f"💬 User Answer: {user_answer2}")
        
        result2 = await orchestrator.process_answer(question.id, user_answer2)
        print(f"\n🤖 AI Classification: {result2.classification}")
        print(f"📊 Score: {result2.score_earned}/{result2.max_score}")
        print(f"🔍 Follow-ups Pending: {len(orchestrator.pending_follow_ups)}")
        
        if orchestrator.pending_follow_ups:
            print("   → AI decided: Follow-up needed ✓")
            
            # Get the follow-up question
            follow_up = orchestrator.get_next_question()
            if follow_up:
                _, fq, _ = follow_up
                print(f"\n🔁 FOLLOW-UP Question: {fq.text}")
                print(f"   Follow-up ID: {fq.id}")
                print(f"   Max Score: {fq.max_score} points")
        else:
            print("   → AI decided: Skip follow-up")
    
    print()
    
    # Example 3: Negative answer → Follow-up triggered
    print("=" * 70)
    print("SCENARIO 3: Negative Answer (Follow-up Expected)")
    print("=" * 70)
    
    # Find a question with follow-ups configured
    for _ in range(3):
        question3 = orchestrator.get_next_question()
        if question3:
            pillar_id, question, pillar_name = question3
            # Skip if it's a follow-up from previous question
            if "_followup_" in question.id:
                continue
                
            print(f"\n📋 Question: {question.text}")
            print(f"🎯 Question ID: {question.id}")
            
            # User gives negative answer
            user_answer3 = "No, we don't have that implemented yet."
            print(f"💬 User Answer: {user_answer3}")
            
            result3 = await orchestrator.process_answer(question.id, user_answer3)
            print(f"\n🤖 AI Classification: {result3.classification}")
            print(f"📊 Score: {result3.score_earned}/{result3.max_score}")
            print(f"🔍 Follow-ups Pending: {len(orchestrator.pending_follow_ups)}")
            
            if orchestrator.pending_follow_ups:
                print("   → AI decided: Follow-up needed ✓")
                
                # Get the follow-up question
                follow_up = orchestrator.get_next_question()
                if follow_up:
                    _, fq, _ = follow_up
                    print(f"\n🔁 FOLLOW-UP Question: {fq.text}")
                    print(f"   Follow-up ID: {fq.id}")
                    print(f"   Max Score: {fq.max_score} points")
                break
            else:
                print("   → No follow-up configured for this question")
    
    print()
    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("✅ AI adapts question flow based on user responses")
    print("✅ Complete answers → Skip follow-ups (efficient)")
    print("✅ Partial/No answers → Trigger follow-ups (thorough)")
    print("✅ Different users get different question paths")
    print()


async def show_follow_up_config():
    """Display configured follow-up questions"""
    from repo_scorer.config import FOLLOW_UP_QUESTIONS
    
    print("=" * 70)
    print("CONFIGURED FOLLOW-UP QUESTIONS")
    print("=" * 70)
    print()
    
    if not FOLLOW_UP_QUESTIONS:
        print("No follow-up questions configured.")
        return
    
    for base_id, follow_ups in FOLLOW_UP_QUESTIONS.items():
        print(f"📌 Base Question: {base_id}")
        for i, fq in enumerate(follow_ups, 1):
            print(f"   └─ Follow-up {i}: {fq.text}")
            print(f"      Triggers on: {', '.join(fq.trigger_classifications)}")
            print(f"      Score: {fq.max_score} points")
            print()


if __name__ == "__main__":
    print()
    print("🚀 AI-Driven Adaptive Questioning Enhancement")
    print()
    
    # Show configuration
    asyncio.run(show_follow_up_config())
    
    # Run demonstration
    asyncio.run(example_adaptive_assessment())
