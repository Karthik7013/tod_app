"""
GUI LAYER: Tkinter desktop app. Uses SDK exclusively."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from todo_sdk import TodoSDK
from todo_core import TodoError

class TodoApp:
    def __init__(self, root):
        self.sdk = TodoSDK()
        self.root = root
        self.root.title("Todo Manager")
        self.root.geometry("850x450")
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill="both", expand=True)

        cols = ("id", "status", "title", "description", "created_at")
        self.tree = ttk.Treeview(frm, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=150 if c != "id" else 40, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(frm, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        btns = ttk.Frame(self.root, padding=5)
        btns.pack(fill="x")        for txt, cmd in [("➕ Add", self._add), ("✏️ Edit", self._edit), ("✅ Toggle", self._toggle), ("🗑️ Delete", self._delete), ("🔄 Refresh", self.refresh)]:
            ttk.Button(btns, text=txt, command=cmd).pack(side="left", padx=5)

    def refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for t in self.sdk.list():
            status = "✅ Done" if t["completed"] else "⏳ Pending"
            self.tree.insert("", "end", values=(t["id"], status, t["title"], t["description"], t["created_at"]))

    def _get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Select a todo first.")
            return None
        return self.tree.item(sel[0], "values")[0]

    def _handle_sdk(self, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            self.refresh()
        except TodoError as e:
            messagebox.showerror("Error", str(e))

    def _add(self):
        title = simpledialog.askstring("Add", "Title:")
        if not title: return
        desc = simpledialog.askstring("Add", "Description (optional):") or ""
        self._handle_sdk(self.sdk.add, title, desc)

    def _edit(self):
        tid = self._get_selected_id()
        if not tid: return
        todo = self.sdk.get(tid)
        nt = simpledialog.askstring("Edit", "Title:", initialvalue=todo["title"])
        if nt is None: return
        nd = simpledialog.askstring("Edit", "Description:", initialvalue=todo["description"])
        self._handle_sdk(self.sdk.update, tid, title=nt, description=nd)

    def _toggle(self):
        tid = self._get_selected_id()
        if not tid: return
        todo = self.sdk.get(tid)
        self._handle_sdk(self.sdk.update, tid, completed=not todo["completed"])

    def _delete(self):
        tid = self._get_selected_id()
        if not tid: return
        if messagebox.askyesno("Confirm", f"Delete todo #{tid}?"):
            self._handle_sdk(self.sdk.delete, tid)
if __name__ == "__main__":
    root = tk.Tk()
    TodoApp(root)
    root.mainloop()
