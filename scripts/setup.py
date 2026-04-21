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
import urllib.request
import urllib.error

API = "https://api.attio.com/v2"

def main():
    key = os.environ.get("ATTIO_API_KEY")
    list_id = os.environ.get("ATTIO_LIST_ID")
    if not key or not list_id:
        print("ERROR: set ATTIO_API_KEY and ATTIO_LIST_ID env vars", file=sys.stderr)
        sys.exit(1)

    H = {"Authorization": f"Bearer {key}"}

    # Verify token
    req = urllib.request.Request(f"{API}/self", headers=H)
    try:
        me = json.loads(urllib.request.urlopen(req).read())
        print(f"Authenticated to workspace: {me.get('workspace_name','?')} ({me.get('workspace_slug','?')})")
    except urllib.error.HTTPError as e:
        print(f"ERROR verifying token: {e.code} {e.read().decode()[:400]}", file=sys.stderr)
        sys.exit(1)

    # List attributes
    req = urllib.request.Request(f"{API}/lists/{list_id}/attributes?limit=100", headers=H)
    attrs = json.loads(urllib.request.urlopen(req).read())["data"]
    print(f"\nFound {len(attrs)} attributes on list {list_id}:")

    schema = {
        "list_id": list_id,
        "workspace_id": me.get("workspace_id"),
        "workspace_slug": me.get("workspace_slug"),
        "attrs": {},
        "options": {},
        "types": {},
    }

    status_attrs = []
    select_attrs = []

    for a in attrs:
        slug = a["api_slug"]
        atype = a["type"]
        aid = a["id"]["attribute_id"]
        schema["attrs"][slug] = aid
        schema["types"][slug] = atype
        print(f"  {slug:30} | {atype:20} | {a['title']}")

        if atype == "status":
            status_attrs.append(slug)
        elif atype == "select":
            select_attrs.append(slug)
            # Fetch options
            opts_req = urllib.request.Request(f"{API}/lists/{list_id}/attributes/{aid}/options", headers=H)
            opts = json.loads(urllib.request.urlopen(opts_req).read())["data"]
            schema["options"][slug] = {o["title"]: o["id"]["option_id"] for o in opts if not o.get("is_archived")}

    print(f"\nSTATUS attributes (Kanban-capable): {status_attrs or '(none)'}")
    print(f"SELECT attributes (filter-capable):  {select_attrs or '(none)'}")

    if status_attrs and select_attrs:
        print("\n" + "!" * 60)
        print("! WARNING: This list has BOTH STATUS and SELECT attributes.")
        print("! Kanban views typically group by the STATUS attribute.")
        print("! When writing updates, use the STATUS slug to move Kanban cards.")
        print(f"! Your STATUS attribute(s): {status_attrs}")
        print("! If you're not sure which one the Kanban uses, check in Attio UI:")
        print("! open a Kanban view -> View settings -> 'Group by' field.")
        print("!" * 60)

    # Write
    out_path = os.environ.get("SCHEMA_PATH", "schema.json")
    with open(out_path, "w") as f:
        json.dump(schema, f, indent=2)
    print(f"\nWrote schema to {out_path}")

if __name__ == "__main__":
    main()
