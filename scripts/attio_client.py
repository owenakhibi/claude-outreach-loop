#!/usr/bin/env python3
"""
Minimal Attio REST client used by the outreach loop.

Usage:
    from scripts.attio_client import AttioClient
    c = AttioClient()  # reads ATTIO_API_KEY from env
    c.update_list_entry(entry_id, {"to_research": "Outreach Sent", ...})
"""
import json
import os
import urllib.request
import urllib.error
from datetime import date, timedelta


class AttioClient:
    API = "https://api.attio.com/v2"

    def __init__(self, api_key=None, list_id=None, schema_path=None):
        self.api_key = api_key or os.environ["ATTIO_API_KEY"]
        self.list_id = list_id or os.environ.get("ATTIO_LIST_ID")
        self.H = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if schema_path:
            with open(schema_path) as f:
                self.schema = json.load(f)
        else:
            self.schema = None

    def _request(self, method, path, body=None):
        url = f"{self.API}{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, headers=self.H, method=method)
        try:
            with urllib.request.urlopen(req) as r:
                raw = r.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            raise RuntimeError(f"{method} {path} failed: {e.code} {err_body[:400]}") from None

    # --- Records ---

    def create_company(self, name, domain=None, description=None, linkedin=None):
        values = {"name": [{"value": name}]}
        if domain:
            values["domains"] = [{"domain": domain}]
        if description:
            values["description"] = [{"value": description}]
        if linkedin:
            values["linkedin"] = [{"value": linkedin}]
        r = self._request("POST", "/objects/companies/records", {"data": {"values": values}})
        return r["data"]["id"]["record_id"]

    def create_person(self, first, last, title=None, linkedin=None, company_id=None, description=None, email=None):
        values = {
            "name": [{"first_name": first, "last_name": last, "full_name": f"{first} {last}"}],
        }
        if title:
            values["job_title"] = [{"value": title}]
        if linkedin and linkedin.startswith("http"):
            values["linkedin"] = [{"value": linkedin}]
        if company_id:
            values["company"] = [{"target_object": "companies", "target_record_id": company_id}]
        if description:
            values["description"] = [{"value": description}]
        if email:
            values["email_addresses"] = [{"email_address": email}]
        r = self._request("POST", "/objects/people/records", {"data": {"values": values}})
        return r["data"]["id"]["record_id"]

    def update_record(self, obj_slug, record_id, values):
        return self._request("PATCH", f"/objects/{obj_slug}/records/{record_id}", {"data": {"values": values}})

    # --- List entries ---

    def list_entries(self, list_id=None):
        list_id = list_id or self.list_id
        r = self._request("POST", f"/lists/{list_id}/entries/query", {"limit": 500})
        return r["data"]

    def create_list_entry(self, parent_object, parent_record_id, entry_values, list_id=None):
        list_id = list_id or self.list_id
        body = {"data": {
            "parent_object": parent_object,
            "parent_record_id": parent_record_id,
            "entry_values": entry_values,
        }}
        r = self._request("POST", f"/lists/{list_id}/entries", body)
        return r["data"]["id"]["entry_id"]

    def update_list_entry(self, entry_id, entry_values, list_id=None):
        """Patch a list entry's values. For status-type fields, pass a plain string value."""
        list_id = list_id or self.list_id
        return self._request("PATCH", f"/lists/{list_id}/entries/{entry_id}", {"data": {"entry_values": entry_values}})

    def delete_list_entry(self, entry_id, list_id=None):
        list_id = list_id or self.list_id
        return self._request("DELETE", f"/lists/{list_id}/entries/{entry_id}")

    # --- Notes ---

    def create_note(self, parent_object, parent_record_id, title, content, fmt="plaintext"):
        body = {"data": {
            "parent_object": parent_object,
            "parent_record_id": parent_record_id,
            "title": title,
            "format": fmt,
            "content": content,
        }}
        r = self._request("POST", "/notes", body)
        return r["data"]["id"]["note_id"]

    # --- Convenience: log an outreach touch ---

    def log_touch(self, entry_id, person_record_id, status, channel, message, attempt=1, followup_days=3):
        """All-in-one: update list entry status + log a note on the person."""
        today = date.today().isoformat()
        followup = (date.today() + timedelta(days=followup_days)).isoformat()

        self.update_list_entry(entry_id, {
            "to_research": status,              # status string (update field name if your list uses different slug)
            "attempt_number": [{"value": attempt}],
            "last_touch": [{"value": today}],
            "next_followup_due": [{"value": followup}],
        })

        self.create_note(
            parent_object="people",
            parent_record_id=person_record_id,
            title=f"LinkedIn {channel} sent {today}",
            content=f"Sent on {today}:\n\n{message}\n\nNext follow-up: {followup}",
        )
