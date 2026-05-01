#!/usr/bin/env python3
"""Trello API CLI - Manage boards, lists, cards, labels, and checklists."""

import os
import sys
import json
import requests
from pathlib import Path


# Load .env file manually to avoid dotenv dependency
def load_env():
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("\"'"))


load_env()

KEY = os.environ.get("TRELLO_API_KEY")
TOKEN = os.environ.get("TRELLO_API_TOKEN")
BASE = "https://api.trello.com/1"


def auth():
    return {"key": KEY, "token": TOKEN}


def api(method, endpoint, **params):
    """Make API request and return JSON response."""
    url = f"{BASE}/{endpoint}"
    resp = getattr(requests, method)(url, params={**auth(), **params})
    if not resp.ok:
        print(f"Error {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)
    try:
        return resp.json()
    except:
        return {}


def fmt(data, fields=None, msg=None):
    """Output minimal formatted data. Only essential fields, compact format."""
    if msg:
        print(msg)
        return
    if isinstance(data, list):
        if not data:
            print("(empty)")
            return
        # Extract only specified fields for lists
        if fields:
            clean = [
                {k: item.get(k) for k in fields if item.get(k) is not None}
                for item in data
            ]
        else:
            clean = data
        for item in clean:
            parts = []
            if "name" in item:
                parts.append(item["name"])
            if "id" in item:
                parts.append(f"[{item['id']}]")
            if "desc" in item and item["desc"]:
                desc = (
                    item["desc"][:50] + "..."
                    if len(item.get("desc", "")) > 50
                    else item["desc"]
                )
                parts.append(f"- {desc}")
            if "color" in item:
                parts.append(f"({item['color']})")
            if "state" in item:
                parts.append(f"[{'x' if item['state'] == 'complete' else ' '}]")
            print(" ".join(parts) if parts else json.dumps(item))
    elif isinstance(data, dict):
        # Single item - show key details only
        out = []
        if "name" in data:
            out.append(f"Name: {data['name']}")
        if "id" in data:
            out.append(f"ID: {data['id']}")
        if "desc" in data and data["desc"]:
            out.append(
                f"Desc: {data['desc'][:100]}{'...' if len(data.get('desc', '')) > 100 else ''}"
            )
        if "url" in data:
            out.append(f"URL: {data['url']}")
        if "idList" in data:
            out.append(f"List: {data['idList']}")
        if "labels" in data and data["labels"]:
            labels = ", ".join(
                f"{l.get('name', 'unnamed')}({l.get('color', 'none')})"
                for l in data["labels"]
            )
            out.append(f"Labels: {labels}")
        if "checklists" in data and data["checklists"]:
            for cl in data["checklists"]:
                items = cl.get("checkItems", [])
                done = sum(1 for i in items if i.get("state") == "complete")
                out.append(f"Checklist '{cl.get('name')}': {done}/{len(items)}")
        if "due" in data and data["due"]:
            out.append(f"Due: {data['due']}")
        print("\n".join(out) if out else json.dumps(data))


def list_boards():
    boards = api("get", "members/me/boards", fields="name,id")
    fmt(boards, ["name", "id"])


def list_lists(bid):
    lists = api("get", f"boards/{bid}/lists", fields="name,id")
    fmt(lists, ["name", "id"])


def list_cards(lid):
    cards = api("get", f"lists/{lid}/cards", fields="name,id,desc")
    fmt(cards, ["name", "id", "desc"])


def get_card(cid):
    card = api("get", f"cards/{cid}", checklists="all")
    fmt(card)


def list_labels(bid):
    labels = api("get", f"boards/{bid}/labels")
    fmt(labels, ["name", "id", "color"])


def list_checklists(cid):
    card = api("get", f"cards/{cid}", checklists="all")
    for cl in card.get("checklists", []):
        print(f"{cl['name']} [{cl['id']}]")
        for item in cl.get("checkItems", []):
            done = "x" if item.get("state") == "complete" else " "
            print(f"  [{done}] {item['name']} [{item['id']}]")


COMMANDS = {
    "list_boards": list_boards,
    "create_board": lambda n, d="": fmt(
        None,
        msg=f"Board '{n}' created: {api('post', 'boards', name=n, desc=d).get('id')}",
    ),
    "list_lists": list_lists,
    "create_list": lambda bid, n: fmt(
        None,
        msg=f"List '{n}' created: {api('post', 'lists', idBoard=bid, name=n).get('id')}",
    ),
    "update_list": lambda lid, n: fmt(None, msg=f"List renamed to '{n}'")
    or api("put", f"lists/{lid}", name=n),
    "list_cards": list_cards,
    "get_card": get_card,
    "create_card": lambda lid, n, d="": fmt(
        None,
        msg=f"Card '{n}' created: {api('post', 'cards', idList=lid, name=n, desc=d).get('id')}",
    ),
    "move_card": lambda cid, lid: fmt(None, msg="Card moved")
    or api("put", f"cards/{cid}", idList=lid),
    "delete_card": lambda cid: fmt(None, msg="Card deleted")
    or api("delete", f"cards/{cid}"),
    "update_card_desc": lambda cid, d: fmt(None, msg="Description updated")
    or api("put", f"cards/{cid}", desc=d),
    "list_labels": list_labels,
    "create_label": lambda bid, n, c: fmt(
        None,
        msg=f"Label '{n}' ({c}) created: {api('post', 'labels', idBoard=bid, name=n, color=c).get('id')}",
    ),
    "add_label": lambda cid, lid: fmt(None, msg="Label added")
    or api("post", f"cards/{cid}/idLabels", value=lid),
    "remove_label": lambda cid, lid: fmt(None, msg="Label removed")
    or api("delete", f"cards/{cid}/idLabels/{lid}"),
    "create_checklist": lambda cid, n="Checklist": fmt(
        None,
        msg=f"Checklist '{n}' created: {api('post', 'checklists', idCard=cid, name=n).get('id')}",
    ),
    "add_checkitem": lambda clid, n: fmt(
        None,
        msg=f"Item '{n}' added: {api('post', f'checklists/{clid}/checkItems', name=n).get('id')}",
    ),
    "list_checklists": list_checklists,
    "complete_checkitem": lambda cid, clid, iid: fmt(None, msg="Item completed")
    or api("put", f"cards/{cid}/checklist/{clid}/checkItem/{iid}", state="complete"),
    "uncomplete_checkitem": lambda cid, clid, iid: fmt(None, msg="Item uncompleted")
    or api("put", f"cards/{cid}/checklist/{clid}/checkItem/{iid}", state="incomplete"),
}

if __name__ == "__main__":
    if not KEY or not TOKEN:
        print(
            "Error: Set TRELLO_API_KEY and TRELLO_API_TOKEN env vars", file=sys.stderr
        )
        sys.exit(1)

    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Commands: {', '.join(sorted(COMMANDS.keys()))}")
        sys.exit(1)

    cmd, args = sys.argv[1], sys.argv[2:]
    try:
        COMMANDS[cmd](*args)
    except TypeError as e:
        print(f"Error: Wrong args for '{cmd}'", file=sys.stderr)
        sys.exit(1)
