import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# -------------------------
# In-Memory Data
# -------------------------
students = {}   # {id: {"name":..., "class":..., "fee":..., "paid":...}}
payments = []   # list of receipts
next_id = 1

# -------------------------
# Utility Functions
# -------------------------
def add_student(name, cls, fee):
    global next_id
    students[next_id] = {
        "name": name,
        "class": cls,
        "fee": float(fee),
        "paid": 0.0
    }
    next_id += 1


def record_payment(student_id, amount):
    stu = students[student_id]
    stu["paid"] += amount
    rec_no = f"RC{len(payments)+1:04d}"
    pay = {
        "receipt": rec_no,
        "id": student_id,
        "name": stu["name"],
        "class": stu["class"],
        "amount": amount,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    payments.append(pay)
    return pay


def get_due_list():
    due = []
    for sid, s in students.items():
        balance = s["fee"] - s["paid"]
        if balance > 0:
            due.append((sid, s["name"], s["class"], s["fee"], s["paid"], balance))
    return due


# -------------------------
# Custom Styling (CSS-like)
# -------------------------
def set_style():
    style = ttk.Style()
    style.theme_use("clam")  # modern look

    style.configure("TButton",
                    font=("Arial", 11, "bold"),
                    padding=6,
                    background="#4CAF50",
                    foreground="white")
    style.map("TButton",
              background=[("active", "#45a049")])

    style.configure("Treeview",
                    background="#f0faff",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="#f0faff",
                    font=("Arial", 10))
    style.configure("Treeview.Heading",
                    font=("Arial", 11, "bold"),
                    background="#007acc",
                    foreground="white")

    style.map("Treeview",
              background=[("selected", "#3399ff")])

# -------------------------
# Windows
# -------------------------
class StudentWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Student Record Management")
        self.configure(bg="#e6f2ff")

        tk.Label(self, text="Name", bg="#e6f2ff", font=("Arial", 11)).grid(row=0, column=0, pady=5, sticky="w")
        tk.Label(self, text="Class", bg="#e6f2ff", font=("Arial", 11)).grid(row=1, column=0, pady=5, sticky="w")
        tk.Label(self, text="Annual Fee", bg="#e6f2ff", font=("Arial", 11)).grid(row=2, column=0, pady=5, sticky="w")

        self.name_entry = tk.Entry(self, font=("Arial", 11))
        self.class_entry = tk.Entry(self, font=("Arial", 11))
        self.fee_entry = tk.Entry(self, font=("Arial", 11))

        self.name_entry.grid(row=0, column=1, pady=5, padx=5)
        self.class_entry.grid(row=1, column=1, pady=5, padx=5)
        self.fee_entry.grid(row=2, column=1, pady=5, padx=5)

        self.selected_id = None  # Track selected student

        # Buttons
        ttk.Button(self, text="Add Student", command=self.add_student).grid(row=3, columnspan=2, pady=5)
        ttk.Button(self, text="Update Student", command=self.update_student).grid(row=4, columnspan=2, pady=5)
        ttk.Button(self, text="Delete Student", command=self.delete_student).grid(row=5, columnspan=2, pady=5)

        # Student Table
        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Class", "Fee", "Paid"), show="headings")
        for col in ("ID", "Name", "Class", "Fee", "Paid"):
            self.tree.heading(col, text=col, anchor=tk.CENTER)
            self.tree.column(col, anchor=tk.CENTER)
        self.tree.grid(row=6, columnspan=2, pady=10, padx=5, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        self.refresh()

    def add_student(self):
        try:
            name = self.name_entry.get().strip()
            cls = self.class_entry.get().strip()
            fee = float(self.fee_entry.get().strip())

            if not name or not cls:
                raise ValueError("Name and Class cannot be empty.")

            add_student(name, cls, fee)
            messagebox.showinfo("Success", "Student added successfully")
            self.clear_fields()
            self.refresh()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid data.")

    def update_student(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Please select a student to update.")
            return

        try:
            name = self.name_entry.get().strip()
            cls = self.class_entry.get().strip()
            fee = float(self.fee_entry.get().strip())

            if not name or not cls:
                raise ValueError("Name and Class cannot be empty.")

            students[self.selected_id]["name"] = name
            students[self.selected_id]["class"] = cls
            students[self.selected_id]["fee"] = fee

            messagebox.showinfo("Success", "Student record updated.")
            self.clear_fields()
            self.refresh()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid data.")

    def delete_student(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Please select a student to delete.")
            return

        student = students[self.selected_id]
        if student["paid"] > 0:
            messagebox.showwarning("Not Allowed", "Cannot delete a student with existing payments.")
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this student?"):
            del students[self.selected_id]
            self.selected_id = None
            self.clear_fields()
            self.refresh()
            messagebox.showinfo("Deleted", "Student record deleted.")

    def on_row_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item["values"]
            self.selected_id = values[0]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, values[1])
            self.class_entry.delete(0, tk.END)
            self.class_entry.insert(0, values[2])
            self.fee_entry.delete(0, tk.END)
            self.fee_entry.insert(0, values[3])

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.class_entry.delete(0, tk.END)
        self.fee_entry.delete(0, tk.END)
        self.selected_id = None

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for sid, s in students.items():
            self.tree.insert("", "end", values=(sid, s["name"], s["class"], s["fee"], s["paid"]))


class PaymentWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Fee Payment Recording")
        self.configure(bg="#e6f2ff")

        tk.Label(self, text="Select Student", bg="#e6f2ff", font=("Arial", 11)).grid(row=0, column=0, pady=5, sticky="w")
        self.student_cb = ttk.Combobox(self, values=[f"{sid}-{s['name']}" for sid, s in students.items()], font=("Arial", 11))
        self.student_cb.grid(row=0, column=1, pady=5)

        tk.Label(self, text="Amount", bg="#e6f2ff", font=("Arial", 11)).grid(row=1, column=0, pady=5, sticky="w")
        self.amount_entry = tk.Entry(self, font=("Arial", 11))
        self.amount_entry.grid(row=1, column=1, pady=5)

        ttk.Button(self, text="Record Payment", command=self.make_payment).grid(row=2, columnspan=2, pady=10)

    def make_payment(self):
        try:
            student_id = int(self.student_cb.get().split("-")[0])
            amount = float(self.amount_entry.get())
            pay = record_payment(student_id, amount)
            ReceiptWindow(self, pay)
            messagebox.showinfo("Success", f"Payment recorded. Receipt {pay['receipt']}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


class DueListWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Due List")
        self.configure(bg="#e6f2ff")

        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Class", "Fee", "Paid", "Due"), show="headings")
        for col in ("ID", "Name", "Class", "Fee", "Paid", "Due"):
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, pady=5, padx=5)

        for row in get_due_list():
            self.tree.insert("", "end", values=row)


class ReceiptWindow(tk.Toplevel):
    def __init__(self, master, receipt):
        super().__init__(master)
        self.title("Receipt")
        self.configure(bg="#e6f2ff")

        text = tk.Text(self, width=40, height=12, bg="white", fg="black", font=("Courier", 11))
        text.pack(pady=10, padx=10)
        text.insert("end", f"Receipt No: {receipt['receipt']}\n")
        text.insert("end", f"Date: {receipt['date']}\n")
        text.insert("end", f"Student: {receipt['name']} (Class {receipt['class']})\n")
        text.insert("end", f"Amount Paid: ₹{receipt['amount']:.2f}\n")
        text.config(state="disabled")


# -------------------------
# Main Application
# -------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("School Fee Management System")
        self.geometry("450x350")
        self.configure(bg="#b3e0ff")

        set_style()  # Apply CSS-like styles

        tk.Label(self, text="🏫 School Fee Management System", font=("Arial", 16, "bold"), bg="#b3e0ff", fg="#003366").pack(pady=20)

        ttk.Button(self, text="Student Record Management", width=35, command=lambda: StudentWindow(self)).pack(pady=5)
        ttk.Button(self, text="Fee Payment Recording", width=35, command=lambda: PaymentWindow(self)).pack(pady=5)
        ttk.Button(self, text="Due List Generation", width=35, command=lambda: DueListWindow(self)).pack(pady=5)


if __name__ == "__main__":
    app = App()
    app.mainloop()
