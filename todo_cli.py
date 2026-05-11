"""
CLI LAYER: Terminal interface. Uses SDK exclusively."""
import argparse
import sys
from todo_sdk import TodoSDK
from todo_core import TodoError

def format_table(todos: list) -> str:
    if not todos: return "No todos found."
    header = f"{'ID':<5} {'Status':<10} {'Title':<25} {'Description'}"
    rows = [header, "─" * len(header)]
    for t in todos:
        status = "✅ Done" if t["completed"] else "⏳ Pending"
        desc = (t["description"] or "—")[:25]
        rows.append(f"{t['id']:<5} {status:<10} {t['title']:<25} {desc}")
    return "\n".join(rows)

def main():
    parser = argparse.ArgumentParser(description="Todo CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all todos")
    sub.add_parser("completed", help="List completed")
    sub.add_parser("pending", help="List pending")
    
    a = sub.add_parser("add"); a.add_argument("title"); a.add_argument("-d", "--desc", default=None)
    u = sub.add_parser("update"); u.add_argument("id", type=int); u.add_argument("-t", "--title", default=None); u.add_argument("-d", "--desc", default=None); u.add_argument("-c", "--complete", action="store_true")
    d = sub.add_parser("delete"); d.add_argument("id", type=int)
    e = sub.add_parser("export"); e.add_argument("filepath")
    i = sub.add_parser("import"); i.add_argument("filepath")

    args = parser.parse_args()
    sdk = TodoSDK()

    try:
        match args.command:
            case "list": print(format_table(sdk.list()))
            case "completed": print(format_table(sdk.list(completed_only=True)))
            case "pending": print(format_table(sdk.list(completed_only=False)))
            case "add":
                t = sdk.add(args.title, args.desc or "")
                print(f"✅ Added: {t['title']} (ID: {t['id']})")
            case "update":
                updates = {}
                if args.title: updates["title"] = args.title
                if args.desc is not None: updates["description"] = args.desc
                if args.complete: updates["completed"] = True
                t = sdk.update(args.id, **updates)
                print(f"📝 Updated: {t['title']}")
            case "delete": 
                sdk.delete(args.id)
                print(f"🗑️ Deleted ID {args.id}")
            case "export":
                sdk.export_json(args.filepath)
                print(f"💾 Exported to {args.filepath}")
            case "import":
                imported = sdk.import_json(args.filepath)
                print(f"📥 Imported {len(imported)} todos")
    except TodoError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
