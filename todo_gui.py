import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import httpx

DEFAULT_URL = "http://127.0.0.1:8000"


class TodoApp:
    def __init__(self, root, api_url: str = DEFAULT_URL):
        self.api_url = api_url
        self.client = httpx.Client(base_url=api_url, timeout=10.0)
        self.root = root
        self.root.title("Todo Manager")
        self.root.geometry("850x450")
        self._build_ui()
        self.refresh()

    def _request(self, method: str, path: str, **kwargs):
        try:
            resp = self.client.request(method, path, **kwargs)
            if not resp.is_success:
                raise Exception(resp.text)
            return resp.json() if resp.content else None
        except httpx.ConnectError:
            raise Exception(f"Cannot connect to API at {self.api_url}")
        except httpx.TimeoutException:
            raise Exception("Request timed out")

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
        btns.pack(fill="x")
        for txt, cmd in [
            ("Add", self._add),
            ("Edit", self._edit),
            ("Toggle", self._toggle),
            ("Delete", self._delete),
            ("Refresh", self.refresh),
        ]:
            ttk.Button(btns, text=txt, command=cmd).pack(side="left", padx=5)

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            todos = self._request("GET", "/todos")
            for t in (todos or []):
                status = "Done" if t["completed"] else "Pending"
                self.tree.insert(
                    "",
                    "end",
                    values=(t["id"], status, t["title"], t.get("description", ""), t["created_at"]),
                )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Select a todo first.")
            return None
        return int(self.tree.item(sel[0], "values")[0])

    def _handle(self, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _add(self):
        title = simpledialog.askstring("Add", "Title:")
        if not title:
            return
        desc = simpledialog.askstring("Add", "Description (optional):") or ""
        self._handle(lambda: self._request("POST", "/todos", json={"title": title, "description": desc}))

    def _edit(self):
        tid = self._get_selected_id()
        if not tid:
            return
        try:
            todo = self._request("GET", f"/todos/{tid}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        nt = simpledialog.askstring("Edit", "Title:", initialvalue=todo["title"])
        if nt is None:
            return
        nd = simpledialog.askstring("Edit", "Description:", initialvalue=todo.get("description", ""))
        if nd is None:
            return
        self._handle(lambda: self._request("PUT", f"/todos/{tid}", json={"title": nt, "description": nd}))

    def _toggle(self):
        tid = self._get_selected_id()
        if not tid:
            return
        try:
            todo = self._request("GET", f"/todos/{tid}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self._handle(
            lambda: self._request("PUT", f"/todos/{tid}", json={"completed": not todo["completed"]})
        )

    def _delete(self):
        tid = self._get_selected_id()
        if not tid:
            return
        if messagebox.askyesno("Confirm", f"Delete todo #{tid}?"):
            self._handle(lambda: self._request("DELETE", f"/todos/{tid}"))


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()