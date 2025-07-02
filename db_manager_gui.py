import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from config import DB_FILE

RECORDS_PER_PAGE = 20

class DBManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("NexInsight Database Manager")
        self.master.geometry("1000x600")
        self.master.configure(bg="#d0e8f2")

        self.current_page = 0

        # Table with Scrollbars
        table_frame = tk.Frame(master)
        table_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("ID", "Content", "Timestamp", "Sent At"), show='headings', height=15)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars
        ysb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        xsb = ttk.Scrollbar(master, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        ysb.pack(side=tk.RIGHT, fill=tk.Y)
        xsb.pack(fill=tk.X)

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            if col == "Content":
                self.tree.column(col, width=400)
            else:
                self.tree.column(col, width=120)

        self.tree.tag_configure("unsynced", background="#fddde6")
        self.tree.bind("<Double-1>", self.show_full_content)

        # Control Panel
        control_frame = tk.Frame(master, bg="#d0e8f2")
        control_frame.pack(pady=5)

        tk.Label(control_frame, text="ID:", bg="#d0e8f2").pack(side=tk.LEFT, padx=5)
        self.id_entry = tk.Entry(control_frame, width=8)
        self.id_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(control_frame, text="Delete", command=self.delete_row).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Mark as Synced", command=self.mark_as_synced).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Refresh", command=self.load_data).pack(side=tk.LEFT, padx=5)

        # Pagination
        nav_frame = tk.Frame(master, bg="#d0e8f2")
        nav_frame.pack(pady=5)

        self.page_label = tk.Label(nav_frame, text="Page 1", bg="#d0e8f2")
        self.page_label.pack(side=tk.LEFT, padx=10)

        tk.Button(nav_frame, text="Previous", command=self.prev_page).pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="Next", command=self.next_page).pack(side=tk.LEFT, padx=5)

        self.total_label = tk.Label(nav_frame, text="", bg="#d0e8f2")
        self.total_label.pack(side=tk.LEFT, padx=10)

        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        offset = self.current_page * RECORDS_PER_PAGE

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bills")
        total_records = cursor.fetchone()[0]

        cursor.execute("SELECT id, content, timestamp, sent_at FROM bills ORDER BY id DESC LIMIT ? OFFSET ?", (RECORDS_PER_PAGE, offset))
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            row_id, content, timestamp, sent_at = row
            preview = (content[:100] + "...") if len(content) > 100 else content
            tag = "unsynced" if sent_at is None else ""
            self.tree.insert("", tk.END, values=(row_id, preview, timestamp, sent_at), tags=(tag,))

        total_pages = max(1, (total_records + RECORDS_PER_PAGE - 1) // RECORDS_PER_PAGE)
        self.page_label.config(text=f"Page {self.current_page + 1} of {total_pages}")
        self.total_label.config(text=f"Total Entries: {total_records}")

    def show_full_content(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        bill_id = item["values"][0]

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM bills WHERE id = ?", (bill_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            content = result[0]
            self.show_popup(f"Full Content - ID {bill_id}", content)

    def show_popup(self, title, content):
        popup = tk.Toplevel(self.master)
        popup.title(title)
        popup.geometry("700x500")

        text_area = scrolledtext.ScrolledText(popup, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_area.insert(tk.END, content)
        text_area.configure(state='disabled')

    def delete_row(self):
        try:
            bill_id = int(self.id_entry.get())
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bills WHERE id = ?", (bill_id,))
            conn.commit()
            conn.close()
            self.load_data()
            messagebox.showinfo("Success", f"Deleted bill ID {bill_id}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric ID.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mark_as_synced(self):
        try:
            bill_id = int(self.id_entry.get())
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp FROM bills WHERE id = ?", (bill_id,))
            row = cursor.fetchone()
            if not row:
                raise Exception("ID not found.")
            timestamp = row[0]
            cursor.execute("UPDATE bills SET sent_at = ? WHERE id = ?", (timestamp, bill_id))
            conn.commit()
            conn.close()
            self.load_data()
            messagebox.showinfo("Success", f"Marked bill ID {bill_id} as synced.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric ID.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def next_page(self):
        self.current_page += 1
        self.load_data()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_data()

def open_db_manager():
    root = tk.Tk()
    app = DBManagerApp(root)
    root.mainloop()
