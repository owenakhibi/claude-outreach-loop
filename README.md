# Claude Outreach Loop

<!-- Hero demo GIF: record the 45-60 sec silent screen cap, save as docs/demo.gif, then uncomment below -->
<!-- <p align="center"><img src="docs/demo.gif" width="720" alt="Claude Outreach Loop demo"/></p> -->

Tell Claude who to send LinkedIn messages to. It classifies each prospect, drafts in your voice, sends via the [Claude in Chrome](https://claude.ai/chrome) extension, and logs every touch in [Attio](https://attio.com) — in one command.

Built for B2B operators sending 10–50 LinkedIn touches a week who are tired of dual-tracking between LinkedIn tabs and their CRM.

## What it does

- **Classifies prospects:** 1st-degree → DM, enterprise C-suite → blank connection, founders → connection with note, etc.
- **Drafts in your voice:** teaser-style messages with humanization rules to avoid AI tells
- **Sends via browser automation:** uses the Claude in Chrome extension to drive your actual LinkedIn session — not a server-side bot, no LinkedIn ToS violation risk beyond what a human does
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
git clone https://github.com/owenakhibi/claude-outreach-loop ~/.claude/skills/claude-outreach-loop
```

Copy memory templates to your Claude project:
```bash
mkdir -p ~/.claude/projects/YOUR-PROJECT/memory
cp ~/.claude/skills/claude-outreach-loop/memory/*.md ~/.claude/projects/YOUR-PROJECT/memory/
```

Edit each memory file and replace the `{{PLACEHOLDER}}` fields with your values:
- `{{YOUR_NAME}}` — who signs the messages
- `{{YOUR_TITLE}}`
- `{{YOUR_COMPANY}}` — public-facing company name
- `{{YOUR_COMPANY_ONE_LINER}}` — ~10-word description
- `{{EXISTING_PARTNERS}}` — optional social proof (delete the line if you have none yet)

## Configure

Create `~/.config/claude-outreach-loop/.env`:
```bash
ATTIO_API_KEY=your_attio_api_key_here
ATTIO_LIST_ID=the_uuid_of_your_outreach_list
ATTIO_WORKSPACE_SLUG=your_workspace_slug
```

Find the list ID by opening your Attio list and copying the UUID from the URL:
`https://app.attio.com/{workspace}/lists/{LIST_ID}/...`

Get the API token from Attio → Settings → Developers → Create new access token. Required scopes:
- `record_permission:read-write`
- `list_entry:read-write`
- `list_configuration:read`
- `object_configuration:read`
- `note:read-write`
- `user_management:read`

Run the setup script to discover your list's attribute schema:
```bash
source ~/.config/claude-outreach-loop/.env
python3 ~/.claude/skills/claude-outreach-loop/scripts/setup.py
```

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
