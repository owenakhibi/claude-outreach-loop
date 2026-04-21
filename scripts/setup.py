#!/usr/bin/env python3
"""
One-time setup: discover your Attio list schema and write it to schema.json.

Usage:
    export ATTIO_API_KEY=...
    export ATTIO_LIST_ID=...
    python3 scripts/setup.py

Writes a schema.json that the rest of the skill reads to know which attribute
IDs to write to. Also prints WARNINGS about any Kanban-confusing attribute pairs
(e.g., both a SELECT and STATUS attribute that look the same).
"""
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.attio.com/v2"
TIMEOUT = 30

REQUIRED_ATTRS = [
    "attempt_number",
    "last_touch",
    "next_followup_due",
    "channel",
]
RECOMMENDED_ATTRS = [
    "primary_contact",
    "additional_contacts",
    "next_action",
    "closed_reason",
    "category",
    "fit_score",
]


def _get(url, headers):
    """GET helper with proper error handling for HTTP, network, and timeout errors."""
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:400]
        print(f"ERROR: {e.code} from {url}\n{body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: network error reaching {url}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except TimeoutError:
        print(f"ERROR: timeout (>{TIMEOUT}s) reaching {url}", file=sys.stderr)
        sys.exit(1)


def main():
    key = os.environ.get("ATTIO_API_KEY")
    list_id = os.environ.get("ATTIO_LIST_ID")
    if not key or not list_id:
        print("ERROR: set ATTIO_API_KEY and ATTIO_LIST_ID env vars", file=sys.stderr)
        print("  tip: `source ~/.config/claude-outreach-loop/.env` first", file=sys.stderr)
        sys.exit(1)

    headers = {"Authorization": f"Bearer {key}"}

    # Verify token + workspace
    me = _get(f"{API}/self", headers).get("data", {})
    if me.get("active") is False:
        print("ERROR: token is inactive or revoked. Generate a new one in Attio → Settings → Developers.", file=sys.stderr)
        sys.exit(1)
    workspace_name = me.get("workspace_name", "?")
    workspace_slug = me.get("workspace_slug", "?")
    workspace_id = me.get("workspace_id")
    print(f"Authenticated to workspace: {workspace_name} ({workspace_slug})")

    # List attributes
    resp = _get(f"{API}/lists/{list_id}/attributes?limit=100", headers)
    attrs = resp.get("data", [])
    if not attrs:
        print(f"ERROR: list {list_id} has no attributes, or doesn't exist, or token lacks `list_configuration:read`", file=sys.stderr)
        sys.exit(1)
    print(f"\nFound {len(attrs)} attributes on list {list_id}:")

    schema = {
        "list_id": list_id,
        "workspace_id": workspace_id,
        "workspace_slug": workspace_slug,
        "attrs": {},
        "options": {},
        "types": {},
    }

    status_attrs = []
    select_attrs = []

    for a in attrs:
        slug = a.get("api_slug")
        atype = a.get("type")
        aid = a.get("id", {}).get("attribute_id")
        title = a.get("title", slug or "?")
        if not slug or not aid:
            continue
        schema["attrs"][slug] = aid
        schema["types"][slug] = atype
        print(f"  {slug:30} | {atype:20} | {title}")

        if atype == "status":
            status_attrs.append(slug)
        elif atype == "select":
            select_attrs.append(slug)
            opts_resp = _get(f"{API}/lists/{list_id}/attributes/{aid}/options", headers)
            opts = opts_resp.get("data", [])
            schema["options"][slug] = {
                o.get("title"): o.get("id", {}).get("option_id")
                for o in opts
                if not o.get("is_archived") and o.get("title")
            }

    print(f"\nSTATUS attributes (Kanban-capable): {status_attrs or '(none)'}")
    print(f"SELECT attributes (filter-capable):  {select_attrs or '(none)'}")

    # Remember which status slug the client should write to
    if status_attrs:
        schema["status_slug"] = status_attrs[0]
        if len(status_attrs) > 1:
            print(f"\nNOTE: multiple STATUS attributes found. Using '{status_attrs[0]}' as primary. "
                  f"Edit schema.json to set 'status_slug' to your Kanban's actual grouping field if different.")

    if status_attrs and select_attrs:
        print("\n" + "!" * 60)
        print("! WARNING: This list has BOTH STATUS and SELECT attributes.")
        print("! Kanban views typically group by the STATUS attribute.")
        print("! The skill will write updates to the STATUS slug by default.")
        print(f"! Primary STATUS slug: {status_attrs[0]}")
        print("! If your Kanban uses a different grouping field, check in Attio UI:")
        print("! open a Kanban view → View settings → 'Group by' field,")
        print("! then manually edit schema.json's 'status_slug' field.")
        print("!" * 60)

    # Validate required + recommended attributes
    missing_required = [a for a in REQUIRED_ATTRS if a not in schema["attrs"]]
    missing_recommended = [a for a in RECOMMENDED_ATTRS if a not in schema["attrs"]]
    if missing_required:
        print(f"\nWARNING: these REQUIRED attributes are missing from your list — the skill will break without them:")
        for a in missing_required:
            print(f"  - {a}")
        print("  Create them in Attio UI → list settings → attributes, then re-run this script.")
    if missing_recommended:
        print(f"\nNote: these RECOMMENDED attributes are missing (the skill still works, but with reduced functionality):")
        for a in missing_recommended:
            print(f"  - {a}")

    if not status_attrs:
        print("\nWARNING: no STATUS attribute found on this list. The Kanban will not update correctly.")

    # Write schema
    out_path = os.path.expanduser(os.environ.get("SCHEMA_PATH", "schema.json"))
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(schema, f, indent=2)
    print(f"\nWrote schema to {out_path}")


if __name__ == "__main__":
    main()
