# Claude Outreach Loop

<!-- Hero demo GIF: record the 45-60 sec silent screen cap, save as docs/demo.gif, then uncomment below -->
<!-- <p align="center"><img src="docs/demo.gif" width="720" alt="Claude Outreach Loop demo"/></p> -->

Tell Claude who to send LinkedIn messages to. It classifies each prospect, drafts in your voice, sends via the [Claude in Chrome](https://claude.ai/chrome) extension, and logs every touch in [Attio](https://attio.com) — in one command.

Built for B2B operators sending 10–50 LinkedIn touches a week who are tired of dual-tracking between LinkedIn tabs and their CRM.

## What it does

- **Classifies prospects:** 1st-degree → DM, enterprise C-suite → blank connection, founders → connection with note, etc.
- **Drafts in your voice:** teaser-style messages with humanization rules to avoid AI tells
- **Sends via browser automation:** uses the Claude in Chrome extension to drive your actual logged-in Chrome session, not a headless server bot. You're responsible for complying with LinkedIn's Terms of Service.
- **Updates Attio automatically:** moves cards on your Kanban, bumps Attempt #, sets Next Follow-up Due, logs notes on Person records
- **Handles edge cases:** pending connections, job changes, multi-threading at one company, acceptance → post-accept DM flow, ghost escalation

## What it doesn't do

- Email outreach (different channel patterns)
- Twitter DMs (too ad-hoc to script reliably)
- Prospect research (that's a separate lead-gen workflow)
- Automated follow-up drips without human confirmation

## Requirements

- **Claude Code** (tested on Claude Opus 4.7)
- **Claude in Chrome** extension, installed and signed in
- **Attio workspace** with API token access
- **Python 3.9+** for helper scripts
- **LinkedIn Premium or Sales Nav** (optional — only needed if you want InMail as Day 7 fallback)

## Install

```bash
mkdir -p ~/.claude/skills && \
  git clone https://github.com/owenakhibi/claude-outreach-loop ~/.claude/skills/claude-outreach-loop
```

Copy the memory templates into your Claude Code project. `YOUR-PROJECT` is the folder name Claude Code uses for your project — run `ls ~/.claude/projects/` to find it:

```bash
PROJECT=YOUR-PROJECT  # replace with your project folder name
mkdir -p ~/.claude/projects/$PROJECT/memory
# Copy everything except MEMORY.md (which you likely already have — merge by hand)
cp ~/.claude/skills/claude-outreach-loop/memory/company_name_usage.md \
   ~/.claude/skills/claude-outreach-loop/memory/humanization_rules.md \
   ~/.claude/skills/claude-outreach-loop/memory/linkedin_outreach_strategy.md \
   ~/.claude/skills/claude-outreach-loop/memory/outreach_attio_updates.md \
   ~/.claude/skills/claude-outreach-loop/memory/outreach_cadence.md \
   ~/.claude/skills/claude-outreach-loop/memory/outreach_sender.md \
   ~/.claude/skills/claude-outreach-loop/memory/outreach_style.md \
   ~/.claude/projects/$PROJECT/memory/
```

Then append the entries from `~/.claude/skills/claude-outreach-loop/memory/MEMORY.md` to your existing `~/.claude/projects/$PROJECT/memory/MEMORY.md` index.

Edit each copied memory file and replace the `{{PLACEHOLDER}}` fields with your values:
- `{{YOUR_NAME}}` — who signs the messages (e.g., "Alex Chen")
- `{{YOUR_FIRST_NAME}}` — the first-name form for sign-offs (e.g., "Alex")
- `{{YOUR_TITLE}}` — your title (e.g., "Head of Partnerships")
- `{{YOUR_COMPANY}}` — public-facing company name
- `{{YOUR_COMPANY_ONE_LINER}}` — ~10-word description of your company
- `{{EXISTING_PARTNERS_REFERENCE}}` — optional social proof (delete references to it if you have none yet)

## Configure

Create a config directory and copy the example env file:
```bash
mkdir -p ~/.config/claude-outreach-loop
cp ~/.claude/skills/claude-outreach-loop/.env.example ~/.config/claude-outreach-loop/.env
```

Then edit `~/.config/claude-outreach-loop/.env` and fill in your real values:
```bash
export ATTIO_API_KEY=your_attio_api_key_here
export ATTIO_LIST_ID=the_uuid_of_your_outreach_list
export ATTIO_WORKSPACE_SLUG=your_workspace_slug
```

Find the list ID by opening your Attio list and copying the UUID from the URL:
`https://app.attio.com/{workspace}/lists/{LIST_ID}/...`

Get the API token from Attio → Settings → Developers → Create new access token. Required scopes:
- `record_permission:read-write`
- `list_entry:read-write`
- `list_configuration:read`
- `object_configuration:read`
- `note:read-write`

Run the setup script to discover your list's attribute schema:
```bash
source ~/.config/claude-outreach-loop/.env && \
  python3 ~/.claude/skills/claude-outreach-loop/scripts/setup.py
```

Expected output: a list of discovered attributes, a STATUS vs SELECT warning if both exist, and `Wrote schema to ~/.config/claude-outreach-loop/schema.json`.

It writes a `schema.json` and flags the critical gotcha: whether your Kanban groups by a `stage` SELECT or a `status` attribute. **Kanban updates must go to the STATUS field, not the SELECT field** — if you skip this, your Kanban won't move.

## Use

Once installed, the skill triggers automatically on phrases like:
- "Send connects to {list of names}"
- "Reach out to {company}"
- "Follow up with {name}"
- "Start the outreach batch"
- "{Name} accepted, send the DM"
- "{Name} replied, log it"

Claude will:
1. Pull profiles from LinkedIn via the Chrome extension
2. Classify each (degree, role, pending status)
3. Draft each message (teaser, post-accept, or warm variant as appropriate)
4. Show you the drafts before sending
5. On approval, send each via the browser
6. Update your Attio list in one batch

## What gets written where

| Claude updates | Where | When |
|---|---|---|
| List entry `to_research` status | Attio list | After each send |
| `last_touch` date | Attio list | After each send |
| `attempt_number` | Attio list | Incremented per touch |
| `next_followup_due` date | Attio list | Set to +3 days |
| Note with message body | Attio Person record | After each send |

## Required Attio list attributes

The skill expects these attributes on your list (exact slugs may vary — setup.py discovers them):

| Attribute | Type | Purpose |
|---|---|---|
| `to_research` (or your Kanban status field) | status | Pipeline stage — Kanban groups here |
| `attempt_number` | number | 1–3 |
| `last_touch` | date | |
| `next_followup_due` | date | |
| `channel` | select | LinkedIn / Email / Twitter / Warm Intro |
| `primary_contact` | record-reference (people) | |
| `additional_contacts` | record-reference (people, multi) | For multi-threading |
| `next_action` | text | Free-form |
| `closed_reason` | select | Meeting Booked / Passed / Ghosted / Wrong Target |
| `category` | select | Your ICP categories |
| `fit_score` | select | High / Medium / Low |

If any are missing, setup.py tells you which and you create them in Attio's UI first.

## Security notes

- **Never commit `.env` files, schema.json, or record-ID caches.** The `.gitignore` in this repo handles this.
- **API tokens should be least-privilege.** Use the scope list above — not admin-all.
- **Rotate tokens quarterly.** Especially if you share session logs or screen recordings.
- **The skill uses your real logged-in Chrome session.** LinkedIn sees normal human browsing. It's not a headless bot.

## Acknowledgments

Humanization rules borrow heavily from [blader/humanizer](https://github.com/blader/humanizer) — the most-starred Claude Code skill for removing AI writing tells. Install it alongside this skill for voice calibration:
```bash
git clone https://github.com/blader/humanizer.git ~/.claude/skills/humanizer
```

## License

MIT. See [LICENSE](LICENSE).

## Contributing

Issues and PRs welcome. Especially interested in:
- CRM adapters beyond Attio (HubSpot, Salesforce, Close, etc.)
- LinkedIn flow variants for regional differences (Europe vs US LinkedIn UX has diverged)
- Better degree-detection that catches "Pending" faster
