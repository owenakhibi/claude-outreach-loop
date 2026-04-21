---
name: claude-outreach-loop
description: >
  Run a LinkedIn → Attio outreach workflow end-to-end from Claude Code: classify
  a prospect, draft the right message in your voice, send it via the Claude in
  Chrome browser automation, and log the touch in your Attio CRM list. Use this
  skill whenever the user says "send connects to X", "reach out to X", "start the
  outreach batch", "follow up with X", "{name} accepted send the DM", "{name}
  replied log it", or anything that involves actually sending LinkedIn messages
  and syncing CRM state. Also use when a prospect accepts a connection or replies
  — the follow-up DM and CRM update flow live here too.
---

# Claude Outreach Loop

End-to-end LinkedIn + Attio workflow for Claude Code. Built for operators who send 10–50 cold/warm LinkedIn touches per week and want Claude to handle both the sending (via Claude in Chrome) and the CRM updating (via Attio's API).

## Before you use this skill — one-time setup

Copy the template memory files (all except `MEMORY.md` — merge that index by hand) into your Claude Code project memory directory: `~/.claude/projects/<your-project>/memory/`. The `<your-project>` folder name is what Claude Code uses for your project — check `ls ~/.claude/projects/` to find it.

Then **fill in the placeholders** in each copied file:
- `{{YOUR_NAME}}`, `{{YOUR_FIRST_NAME}}`, `{{YOUR_TITLE}}` — who signs the messages
- `{{YOUR_COMPANY}}`, `{{YOUR_COMPANY_ONE_LINER}}` — what you tell prospects
- `{{EXISTING_PARTNERS_REFERENCE}}` — optional social proof you drop into messages (delete references if you have none yet)

Copy `.env.example` to `~/.config/claude-outreach-loop/.env` and fill in:
- `ATTIO_API_KEY` (from Attio → Settings → Developers → Create token)
- `ATTIO_LIST_ID` (the UUID of your target list — see setup script)
- `ATTIO_WORKSPACE_SLUG`

Run `scripts/setup.py` once to discover your Attio schema (attribute IDs, option IDs) and write a `schema.json` the skill reads.

## What this skill needs

- **Claude Code** (with skill support)
- **Claude in Chrome** extension installed and logged in to LinkedIn
- **Attio account** with API access (Premium or similar — API is free on most paid tiers)
- **Python 3.9+** for the helper scripts (used from Bash, not imported)

## The core workflow

### 1. Classify the target

Visit the LinkedIn profile first and check:

- **1st-degree connection?** → send DM directly, skip the connection step
- **Already pending?** → skip sending, but update CRM to "Outreach Sent" if not already
- **2nd/3rd-degree + enterprise C-suite** (F500, public-co CEO, President of Division)? → **blank connection request** (no note). In our experience, blank outperforms noted on acceptance rate for heavy-inbox execs because notes often trigger LinkedIn's "sales spam" pattern-match. Calibrate to your own data.
- **2nd/3rd-degree + founder / startup CEO / mid-market exec**? → **connection with a teaser note**. Curiosity-driven audience — a short note earns both the accept AND engagement.
- **Job changed?** → flag it, consider retargeting. Stale primary contacts are the #1 data-rot problem.
- **Connect button hidden?** → it's under the "More" dropdown. Common for high-follower accounts where LinkedIn makes Follow the primary action.

### 2. Draft the message in your voice

**Teaser template — the default for most cold LinkedIn sends:**
```
Hey {first_name}, we're working on something {company} could benefit from. Would love to tell you more.
```

**Variations:**
- "Worth 15 min to share?"
- "Could I put 15 mins in your calendar?" (specific CTA reads human)

**Post-accept DM (after a connection is accepted):**
Observational opener + curiosity pitch + specific CTA. Works well:
```
Hey {first_name}, I think you'll be interested in what we're building. Could I put 15 mins in your calendar?
```

If they recently changed jobs:
```
Hey {first_name}, I can see you're no longer at {old_company}, but I think you'll be interested in what we're building, could I put 15 mins in your calendar?
```

**For leadership search / connectors (not direct buyers):**
```
Hey {first_name}, we're working on something at the intersection of {their_industry} and {your_domain}. Given what you do, think you'll find it interesting. Could I put 15 mins in your calendar?
```

**Warm 1st-degree DM (they already know you):**
```
Hey {first_name}, we're working on something {company} could benefit from. Worth 15 min to share?
```

Or the credential form:
```
Hey {first_name}, I run partnerships at {{YOUR_COMPANY}} ({{YOUR_COMPANY_ONE_LINER}}). {company}'s {specific_detail} is a natural fit. {{EXISTING_PARTNERS_REFERENCE}}. Worth 15 min?
```

**Never do:**
- Em-dashes (use commas, periods, parens) — this is the loudest 2026 AI tell
- "Hi" openers (use "Hey" — slightly warmer without being unprofessional)
- "curious to be connected" / "worth being connected" / "keen to connect" (AI template tells)
- Starting with the person's name when you can lead with a hook instead
- Title Case subject lines
- Banned-word vocabulary: delve, leverage, robust, utilize, seamless, unlock, foster, ensure, pivotal, crucial, navigate, empower, endeavor, holistic, tapestry, myriad, plethora

See `memory/humanization_rules.md` for the full list and reasoning.

### 3. Send via Claude in Chrome

**Tools needed** (load via ToolSearch at runtime if not already available):
- `mcp__Claude_in_Chrome__tabs_context_mcp`
- `mcp__Claude_in_Chrome__navigate`
- `mcp__Claude_in_Chrome__computer` (screenshot, left_click, type)
- `mcp__Claude_in_Chrome__find` (natural-language element lookup — critical for the Connect menu item which shifts position)

**Connection request flow:**
1. Navigate to profile URL
2. Screenshot to check state (1st / 2nd / 3rd-degree, Pending badge, etc.)
3. If Connect button visible directly at the primary action bar (typically ~x=188 px in 1400px viewport), click it
4. If only Follow/Message/More visible: click More → use `find` with query "Connect menu item" → click it
5. Modal appears: "Add a note to your invitation?"
6. **For blank connection:** click "Send without a note" (usually the right/blue button)
7. **For noted connection:** click "Add a note" (left/outline button) → click into the text area → type message → click "Send" (bottom-right of modal)

**DM flow (1st-degree or post-accept):**
1. Navigate to profile URL
2. Click "Message" button
3. New message modal opens — click into "Write a message..." textarea
4. Type message
5. Click "Send" (bottom-right of message panel)

**Common gotchas:**
- **Messaging panel lingers** from previous send when you navigate to a new profile. Close it with the X button before clicking buttons on the new profile — otherwise your next click may hit the wrong element.
- **"Pending" badge** = connection already out. Skip.
- **Creators / high-follower accounts** often have Follow as primary, Connect hidden under More.
- **Dropdown clicks sometimes misfire** — if the first click on a menu item doesn't advance, re-click or use the `find` tool to get a fresh element ref.
- **`find` can return wrong results** (e.g., a Connect button from the "People you may know" sidebar instead of the profile's menu). Specify location in the query: `"Connect menu item in profile actions dropdown"`.

### 4. Update your Attio list (the critical path)

**The #1 bug to avoid:** Attio lists can have BOTH a `stage` SELECT field AND a `to_research` STATUS field that look identical but behave differently in Kanban views. **Kanban groups by the STATUS field.** If your updates don't appear on the Kanban, you're probably writing to the SELECT field instead of the STATUS field. Check your list's attribute definitions.

**Payload shape for a send (illustrative — use `scripts/attio_client.py`'s `update_list_entry` for the actual call):**
```python
# Sent as the body of PATCH /v2/lists/{list_id}/entries/{entry_id}
patch = {"data": {"entry_values": {
    "to_research": "Outreach Sent",        # STATUS type: bare string title
    "attempt_number": [{"value": attempt}],
    "last_touch": [{"value": today_iso}],
    "next_followup_due": [{"value": today_plus_3_iso}],
}}}
```
Note: the actual status attribute slug depends on your list — `setup.py` discovers it and writes it to `schema.json`. The client reads from there; don't hardcode `to_research` in your own adapters.

**Recommended status values (adapt to your list):**
- "To Research" (default initial)
- "Ready to Reach out"
- "Outreach Sent" (after Day 0 touch)
- "In conversation" (after they reply — not just accept)
- "Partner" / "Closed Won" (deal signed)
- "Passed" / "Closed Lost" (explicit no or ghosted after 3 touches)

**When to increment Attempt #:**
- Initial touch = 1
- First follow-up after no reply (Day 3) = 2
- Second follow-up (Day 7) = 3
- Max 3, then Close

**When they accept but don't reply:** don't change status, keep Outreach Sent. Bump Attempt # when you send the follow-up DM.

**When they reply:** move to "In conversation".

**Multi-threading at one company (contacting multiple execs):**
- Primary Contact = your main target
- Additional execs → put in an `additional_contacts` multi-reference field (create it if your list doesn't have one)
- Attempt # counts total touches at the company across all contacts
- Log each individual touch as a Note on the Company record (`POST /v2/notes`)

### 5. Log a Note on the Person record for every send

Every LinkedIn touch should produce a note on the person's record. Use `attio_client.create_note(...)` in `scripts/attio_client.py` — the payload shape below is illustrative:
```python
# Sent as the body of POST /v2/notes
note_body = {"data": {
    "parent_object": "people",
    "parent_record_id": person_record_id,
    "title": f"LinkedIn {channel} sent {today}",
    "format": "plaintext",
    "content": f"Sent on {today}:\n\n{message_text}\n\nNext follow-up: {next_due}"
}}
```

This keeps message history discoverable on the Person without cluttering the list entry.

## Handling acceptances + replies

**Connection accepted (no reply yet):**
- No status change — still "Outreach Sent"
- Send the post-accept DM (use post-accept template above)
- Bump Attempt # to 2
- Update Last Touch, Next Follow-up Due

**Reply received:**
- Move `to_research` → "In conversation"
- Update Next Action field with what they said (one-liner)
- Don't auto-send follow-ups from here — let the human drive

**Meeting booked:**
- Move `to_research` → "In conversation" (stays here through the meeting)
- After the meeting, based on outcome: Partner, Passed, or keep as In conversation

## Adding new companies + people mid-flow

When a LinkedIn URL is shared to add:

1. Navigate the profile in Chrome, extract name + current title + current company
2. Check if the company exists in `{data_dir}/company_ids.json`. If not, create it (watch for 409 conflicts on domain uniqueness)
3. Create the Person record linked to the company
4. Decide list placement:
   - New company target → create a list entry with Category + Fit + Primary Contact
   - Additional contact at existing company → add to that company's `additional_contacts` multi-reference
5. Classify — Category + Fit + Channel from your list's option set

## Red flags to catch on every profile

- **Job change:** title doesn't match what's in CRM → flag + retarget
- **"Open to New Opportunities":** they're job hunting, may not be at current company long
- **Deprioritized/wrong contacts:** acquired companies where the previous target is now in a different role (e.g., acquired-company CTO who's no longer the commercial buyer)
- **Already pending connection:** don't re-send, just sync CRM state
- **48+ hours silent after accept:** move to a "Ready to Reach out" reminder column, not an auto-drip

## Batch pattern for firing a group

1. Classify each target (blank / noted / DM / warm / skip)
2. Group by channel type (all blanks first, then notes, then DMs)
3. For each: navigate → send → verify "Invitation sent" toast or message-in-thread
4. Close any lingering panels before moving to the next profile
5. Bulk-update CRM at the end with one script that processes the list
6. Verify by querying the list and grouping by status

## Files this skill operates on

(After setup — paths are yours to configure)

- `{config_dir}/.env` — `ATTIO_API_KEY`, `ATTIO_LIST_ID`, `ATTIO_WORKSPACE_SLUG`
- `{data_dir}/schema.json` — list + attribute IDs + status/option IDs (generated by `scripts/setup.py`)
- `{data_dir}/company_ids.json` — company name → record_id cache
- `{data_dir}/people_ids.json` — person name → record_id cache
- `{memory_dir}/*.md` — your voice, cadence, humanization rules

## What this skill does NOT do

- **Email outreach** — different channel, longer messages, dated hooks. See your CRM's native email integration or a dedicated skill.
- **Twitter DMs** — ad-hoc, not scriptable reliably.
- **Warm intros** — those need a connector's judgment; the skill can draft but shouldn't auto-send.
- **Researching new prospects from scratch** — a separate lead-gen skill's job. This skill takes targets as input and operates on them.
- **Calendar booking threading** — human judgment call.

## References

Memory files that ship with this skill (template them for your org):
- `outreach_sender.md` — who signs outbound
- `outreach_style.md` — your preferred opener + CTA style
- `humanization_rules.md` — anti-AI-tell checklist
- `linkedin_outreach_strategy.md` — blank vs noted connection logic
- `outreach_attio_updates.md` — CRM field mapping
- `outreach_cadence.md` — 3-touch, Day 0/3/7
- `company_name_usage.md` — how you refer to your company externally
