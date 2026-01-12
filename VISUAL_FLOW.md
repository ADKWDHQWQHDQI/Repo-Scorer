# Visual Flow: AI-Driven Adaptive Questioning

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    START ASSESSMENT                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  Ask Base Question 1   │
            │  (Fixed Question)      │
            └───────────┬───────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  User Provides Answer  │
            └───────────┬───────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   AI Classifies Answer         │
        │   (yes/partial/no/unsure)      │
        └───────────┬───────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────┐
    │   Calculate Base Question Score       │
    └───────────┬───────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────┐
│  🆕 AI DECISION POINT (Adaptive Logic)            │
│  ─────────────────────────────────────────────    │
│  • Check if follow-up questions exist             │
│  • Evaluate answer completeness                   │
│  • Consider classification type                   │
│  • AI decides: Should we ask more?                │
└─────────────┬─────────────────────────────────────┘
              │
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌─────────┐         ┌──────────────┐
│ Answer  │         │ Answer is    │
│ is      │         │ vague/partial│
│ complete│         │ or negative  │
└────┬────┘         └──────┬───────┘
     │                     │
     │                     ▼
     │         ┌───────────────────────┐
     │         │  🔁 Trigger Follow-Up  │
     │         │  Question (Dynamic)    │
     │         └───────────┬───────────┘
     │                     │
     │                     ▼
     │         ┌───────────────────────┐
     │         │  User Answers Follow-Up│
     │         └───────────┬───────────┘
     │                     │
     │                     ▼
     │         ┌───────────────────────┐
     │         │  AI Classifies +      │
     │         │  Score Follow-Up      │
     │         └───────────┬───────────┘
     │                     │
     └─────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  More Base Questions? │
    └─────────┬─────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
  [YES]               [NO]
    │                   │
    │                   ▼
    │         ┌─────────────────────┐
    │         │  Calculate Final    │
    │         │  Score & Breakdown  │
    │         └──────────┬──────────┘
    │                    │
    │                    ▼
    │         ┌─────────────────────┐
    │         │  AI Generates       │
    │         │  Summary            │
    │         └──────────┬──────────┘
    │                    │
    └────────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │   ASSESSMENT COMPLETE   │
            └────────────────────────┘
```

---

## Comparison: Before vs After

### BEFORE (Fixed Questionnaire)

```
Q1 → Answer → Classify → Score → Q2 → Answer → Classify → Score → ... → Q15 → END
                                                                            ↓
                                                                    Same for everyone
```

### AFTER (Adaptive Questioning)

```
                        ┌─ Follow-up? ─┐
                        │     YES       │
Q1 → Answer → Classify ─┤               ├─→ Follow-up Q → Answer → Score
                        │     NO        │
                        └───────────────┘
                                ↓
                        Continue to Q2
                                ↓
                        (Different path for each user)
```

---

## Example Scenario Paths

### Path A: Strong Repository

```
User Type: Experienced team with good practices

Q1: "Is CI/CD implemented?"
└─→ "Yes, fully automated on all PRs" [YES]
    └─→ AI: Skip follow-up ✓

Q2: "Is branch protection enforced?"
└─→ "Yes, 2 reviewers + tests required" [YES]
    └─→ AI: Skip follow-up ✓

Q3: "Are CODEOWNERS files used?"
└─→ "Yes, for all critical paths" [YES]
    └─→ AI: Skip follow-up ✓

...15 questions total (no follow-ups)
Time: ~3 minutes
Score: ~95/100
```

### Path B: Developing Repository

```
User Type: Team improving their processes

Q1: "Is CI/CD implemented?"
└─→ "Kind of, basic pipeline exists" [PARTIAL]
    └─→ AI: Ask follow-up ✓
        └─→ FQ: "Does it run on all PRs?"
            └─→ "Not all, only main branch" [PARTIAL]
                └─→ Score: 2/2 (follow-up)

Q2: "Is branch protection enforced?"
└─→ "Partially, only on main" [PARTIAL]
    └─→ AI: Ask follow-up ✓
        └─→ FQ: "Is it enforced on all critical branches?"
            └─→ "No, just main" [NO]
                └─→ Score: 1/2 (follow-up)

Q3: "Are secrets prevented?"
└─→ "No, not yet" [NO]
    └─→ AI: Ask follow-up ✓
        └─→ FQ: "Is remediation tracked?"
            └─→ "We're planning it" [UNSURE]
                └─→ Score: 0.5/2 (follow-up)

...20 questions total (15 base + 5 follow-ups)
Time: ~5 minutes
Score: ~75/110
```

---

## AI Decision Logic

```python
def ai_decide_follow_up(original_question, user_answer, classification, follow_up):
    """
    AI evaluates context to decide if follow-up adds value
    """

    # AI considers:
    factors = [
        "Is the answer vague or incomplete?",
        "Did user already address the follow-up topic?",
        "Would follow-up clarify scoring?",
        "Is user engaged or fatigued?"
    ]

    # AI prompt:
    """
    Original: "{original_question}"
    Answer: "{user_answer}"
    Classification: {classification}
    Follow-up: "{follow_up}"

    Should we ask this follow-up? (yes/no)
    """

    # Returns:
    if ai_response == "yes":
        queue_follow_up()  # Add to pending questions
    else:
        skip_follow_up()   # Continue to next base question
```

---

## Scoring Evolution

### Before Enhancement

```
Total Points: 100
Distribution: 15 questions × 6.67 points each
Everyone gets: Same 15 questions
```

### After Enhancement

```
Total Possible: 110 (100 base + 10 follow-ups)
Distribution:
  - Base: 15 × 6.67 = 100 points
  - Follow-ups: 5 × 2 = 10 points (conditional)

Strong repo:
  → Answers: Mostly "yes" (complete)
  → Follow-ups: 0-1
  → Score: ~95/100 (95%)

Weak repo:
  → Answers: Mostly "partial"/"no" (incomplete)
  → Follow-ups: 4-5
  → Score: ~75/110 (68%)
```

---

## Key Enhancement Points

### 1. **AI Controls Flow** (Agent-like)

- Not just classification
- Decides what happens next
- True adaptive behavior

### 2. **Context-Aware**

- Considers previous answer
- Evaluates completeness
- Avoids redundant questions

### 3. **User-Friendly**

- Strong teams: Faster assessment
- Weak teams: More thorough probing
- Natural conversation flow

### 4. **Technically Sound**

- Simple implementation (~172 lines)
- No breaking changes
- Backward compatible
- Fallback to rules if AI fails

---

## Testing Scenarios

### Test 1: Skip Follow-Up (Complete Answer)

```
Input:
  Q: "Is CI/CD implemented?"
  A: "Yes, GitHub Actions runs on every PR with required checks"

Expected:
  Classification: yes
  Follow-ups triggered: 0
  AI decision: Skip (answer is complete)
```

### Test 2: Trigger Follow-Up (Partial Answer)

```
Input:
  Q: "Is branch protection enforced?"
  A: "Sort of, we have some rules"

Expected:
  Classification: partial
  Follow-ups triggered: 1
  AI decision: Ask (answer is vague)
  Follow-up: "Are protections consistent across all critical branches?"
```

### Test 3: Trigger Follow-Up (Negative Answer)

```
Input:
  Q: "Are secrets prevented from being committed?"
  A: "No, not implemented"

Expected:
  Classification: no
  Follow-ups triggered: 1
  AI decision: Ask (improvement-oriented)
  Follow-up: "Are developers notified when secrets are detected?"
```

---

## Summary

**Enhancement**: AI-driven adaptive questioning
**Implementation**: 4 files, ~172 lines of code
**Impact**: Transforms fixed survey into intelligent conversation
**AI Role**: Classifies answers + Decides next question + Generates summary
**Value**: Better UX, stronger AI justification, minimal risk
