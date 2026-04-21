---
name: Humanization rules for cold outreach
description: Apply these rules to every cold email, LinkedIn InMail, Twitter DM drafted. Target is text that doesn't read AI-generated.
type: feedback
---

Every cold message must pass a humanization filter before sending. Goal: text that reads like a busy operator typed it at 11pm, not a ChatGPT draft.

**Why:** AI-detection as a reflex is standard at exec levels. An email that reads AI-generated gets archived unread. Every humanization miss costs a reply.

**How to apply:**

### The 15 rules (in priority order)

1. **Kill every em-dash.** Use commas, periods, or parentheses. Em-dashes are the single loudest 2025–2026 AI tell.
2. **Keep cold emails under ~90 words.** CEO cold over 90 words reads AI-authored by default.
3. **Vary sentence length violently** — a 3-word sentence next to a 22-word one. AI clusters at 17–19 words with low variance.
4. **Open with a specific fact, not a compliment.** "Saw your Q1 framing of AI as growth multiplier" > "I was impressed by your work." Compliments = #1 template signal.
5. **Use contractions everywhere** — don't, you're, we're, I've, it's, we'd.
6. **Kill tricolons** (X, Y, and Z patterns). Pick one.
7. **Specific numbers, never round.** $47K not $50K. 3 pilots not "a few pilots." 500 hours not "lots of hours."
8. **Name a specific recent thing only a human tracking the space would know** — "Before their YC demo day," "after SF AI Week last month."
9. **Drop the sign-off flourish.** No "Best regards," "Looking forward to hearing from you," "I hope this finds you well." Use "— {{YOUR_FIRST_NAME}}" or just the name.
10. **One intentional informality** per email max (lowercase opener, sentence fragment, "fwiw," "tbh"). More than one reads performative.
11. **No bolding, bullets, or headers in cold email body.** Prose only.
12. **Cut hedges.** "might potentially" / "could possibly" / "may be able to" → delete.
13. **Time-anchored CTA.** "15 min Thursday or Friday?" not "at your convenience."
14. **Shortest usable company name.** Use nicknames over legal names when it reads natural.
15. **Read aloud. If any sentence could live on LinkedIn, rewrite it.**

### Opener preference

"Hey {Name}, I'm {{YOUR_NAME}}." — "Hey" over "Hi" feels warmer without being unprofessional. Always include self-introduction on cold messages since prospects don't know you.

### Words/phrases to delete on sight

delve, leverage, robust, underscore, crucial, pivotal, ensure, utilize, seamless, unlock, foster, empower, streamline, nestled, testament, landscape, showcase, highlight, groundbreaking, transformative, cutting-edge, synergy, holistic, intricate, evolving, navigate, realm, tapestry, myriad, plethora, endeavor

Phrases: "It's worth noting," "I hope this message finds you well," "I wanted to reach out," "In today's fast-paced world," "At its core," "Let's dive in," "I hope this helps," "Exciting opportunity," "Not just X, it's Y," "From X to Y" (false-range), "marking a pivotal moment," "I'd love to connect," "circle back," "touch base," "bandwidth."

Three-plus of these = 80%+ AI on GPTZero. One is survivable. Two is risky.

### Words/phrases to use more

"Quick one," "Fast one," "Worth a look?" "Worth 15?" Proper nouns with context ("{mutual} at {firm} mentioned you"). Specific numbers. Time anchors ("Thursday," "before demo day"). Trade shorthand (domain jargon that proves you know the space). Stacked contractions. Soft fragments ("Short version:" "Context:" "One ask.").

### Subject-line rules

- **Sentence case or lowercase**, never Title Case
- **Under 6 words**, ideal 3–4
- **Names, not categories** — `alex @ acme` > `Intro from Partnerships Team`
- **Questions outperform statements** for cold
- **No emojis, no brackets** like [IMPORTANT]
- **Fragments are fine** — "quick intro re: {their company}?"

### How scanners score (GPTZero / Originality.ai / Copyleaks)

- **Perplexity** (word predictability) — fix with unexpected word choices, fragments, jargon
- **Burstiness** (sentence-length variance) — fix by mixing 4-word and 25-word sentences
- **Pattern matching** — em-dashes, tricolons, banned vocab, title-case subjects, "not just X, it's Y" parallelism

### Recommended companion tool

**blader/humanizer** — https://github.com/blader/humanizer (most-starred Claude Code humanization skill). Voice-calibrates to your writing sample. Install:
```bash
git clone https://github.com/blader/humanizer.git ~/.claude/skills/humanizer/
```

### Workflow per email

1. Draft with the facts
2. Run through `/humanizer` with a sample of your real writing for voice calibration
3. Scan for banned words list — delete all matches
4. Cut word count ~30%
5. Read aloud — kill any LinkedIn-sounding sentence
6. Ship
