import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from config import DB_FILE

RECORDS_PER_PAGE = 20

class DBManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Nexinsight Database")
        self.master.geometry("900x500")
        self.master.configure(bg="#d0e8f2")

        self.current_page = 0

        # Table
        self.tree = ttk.Treeview(master, columns=("ID", "Content", "Timestamp", "Sent At"), show='headings', height=15)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200 if col == "Content" else 120)
        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Control Panel
        control_frame = tk.Frame(master, bg="#d0e8f2")
        control_frame.pack(pady=5)

        tk.Label(control_frame, text="ID:", bg="#d0e8f2").pack(side=tk.LEFT, padx=5)
        self.id_entry = tk.Entry(control_frame, width=5)
        self.id_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(control_frame, text="Delete", command=self.delete_row).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Mark as Synced", command=self.mark_as_synced).pack(side=tk.LEFT, padx=5)

        tk.Button(control_frame, text="Refresh", command=self.load_data).pack(side=tk.LEFT, padx=5)

        # Pagination Controls
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

        cursor.execute("SELECT id, content, timestamp, sent_at FROM bills ORDER BY id DESC LIMIT ? OFFSET ?",
                    (RECORDS_PER_PAGE, offset))
        rows = cursor.fetchall()
        conn.close()

        self.tree.tag_configure("unsynced", background="#fddde6")

        for row in rows:
            row_id, content, timestamp, sent_at = row
            tag = "unsynced" if sent_at is None else ""
            self.tree.insert("", tk.END, values=row, tags=(tag,))

        total_pages = (total_records + RECORDS_PER_PAGE - 1) // RECORDS_PER_PAGE
        self.page_label.config(text=f"Page {self.current_page + 1} of {total_pages}")
        self.total_label.config(text=f"Total Entries: {total_records}")


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
