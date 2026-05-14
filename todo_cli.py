import argparse
import json
import sys

import httpx

DEFAULT_URL = "http://127.0.0.1:8000"


def format_table(todos: list) -> str:
    if not todos:
        return "No todos found."
    header = f"{'ID':<5} {'Status':<10} {'Title':<25} {'Description'}"
    rows = [header, "─" * len(header)]
    for t in todos:
        status = "✅ Done" if t["completed"] else "⏳ Pending"
        desc = (t.get("description") or "—")[:25]
        rows.append(f"{t['id']:<5} {status:<10} {t['title']:<25} {desc}")
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser(description="Todo CLI")
    parser.add_argument("--url", default=DEFAULT_URL, help="API base URL")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all todos")
    sub.add_parser("completed", help="List completed")
    sub.add_parser("pending", help="List pending")

    a = sub.add_parser("add")
    a.add_argument("title")
    a.add_argument("-d", "--desc", default=None)

    u = sub.add_parser("update")
    u.add_argument("id", type=int)
    u.add_argument("-t", "--title", default=None)
    u.add_argument("-d", "--desc", default=None)
    u.add_argument("-c", "--complete", action="store_true")

    d = sub.add_parser("delete")
    d.add_argument("id", type=int)

    e = sub.add_parser("export")
    e.add_argument("filepath")

    i = sub.add_parser("import")
    i.add_argument("filepath")

    args = parser.parse_args()
    client = httpx.Client(base_url=args.url, timeout=10.0)

    def api_error(resp: httpx.Response):
        print(f"❌ API Error: {resp.text}", file=sys.stderr)
        sys.exit(1)

    try:
        match args.command:
            case "list":
                resp = client.get("/todos")
                if not resp.is_success:
                    api_error(resp)
                print(format_table(resp.json()))

            case "completed":
                resp = client.get("/todos", params={"completed": "true"})
                if not resp.is_success:
                    api_error(resp)
                print(format_table(resp.json()))

            case "pending":
                resp = client.get("/todos", params={"completed": "false"})
                if not resp.is_success:
                    api_error(resp)
                print(format_table(resp.json()))

            case "add":
                resp = client.post("/todos", json={"title": args.title, "description": args.desc or ""})
                if not resp.is_success:
                    api_error(resp)
                t = resp.json()
                print(f"✅ Added: {t['title']} (ID: {t['id']})")

            case "update":
                updates = {}
                if args.title:
                    updates["title"] = args.title
                if args.desc is not None:
                    updates["description"] = args.desc
                if args.complete:
                    updates["completed"] = True
                resp = client.put(f"/todos/{args.id}", json=updates)
                if not resp.is_success:
                    api_error(resp)
                t = resp.json()
                print(f"📝 Updated: {t['title']}")

            case "delete":
                resp = client.delete(f"/todos/{args.id}")
                if not resp.is_success:
                    api_error(resp)
                print(f"🗑️ Deleted ID {args.id}")

            case "export":
                resp = client.get("/todos")
                if not resp.is_success:
                    api_error(resp)
                with open(args.filepath, "w") as f:
                    json.dump(resp.json(), f, indent=2)
                print(f"💾 Exported to {args.filepath}")

            case "import":
                with open(args.filepath, "r") as f:
                    data = json.load(f)
                resp = client.post("/todos/batch", json=data)
                if not resp.is_success:
                    api_error(resp)
                imported = len(resp.json())
                print(f"📥 Imported {imported} todos")

    except httpx.ConnectError:
        print(f"❌ Cannot connect to API at {args.url}. Is the server running?", file=sys.stderr)
        sys.exit(1)
    except httpx.TimeoutException:
        print(f"❌ Request timed out", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()