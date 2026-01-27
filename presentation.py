import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Database Connection
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

# Create Tables if not exist
cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
                    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL)''')

conn.commit()

# ------------------ GUI Application ------------------

class InventoryApp:
    def __init__(self, root):  # ✅ Correct constructor
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("800x500")

        # Dashboard Frame
        self.dashboard_frame = tk.Frame(root)
        self.dashboard_frame.pack(pady=10)

        self.product_count_label = tk.Label(self.dashboard_frame, text="Total Products: 0", font=("Arial", 12, "bold"))
        self.product_count_label.pack(side=tk.LEFT, padx=20)

        self.employee_count_label = tk.Label(self.dashboard_frame, text="Total Employees: 0", font=("Arial", 12, "bold"))
        self.employee_count_label.pack(side=tk.LEFT, padx=20)

        self.update_dashboard()

        # Tabs for Products & Employees
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(expand=1, fill="both")

        self.product_frame = ttk.Frame(self.tabs)
        self.employee_frame = ttk.Frame(self.tabs)

        self.tabs.add(self.product_frame, text="Products")
        self.tabs.add(self.employee_frame, text="Employees")

        # Setup both tabs
        self.setup_product_tab()
        self.setup_employee_tab()

    # ------------------ Product Management ------------------
    def setup_product_tab(self):
        frame = self.product_frame

        # Product Form
        form_frame = tk.Frame(frame)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Product Name:").grid(row=0, column=0)
        self.product_name_entry = tk.Entry(form_frame)
        self.product_name_entry.grid(row=0, column=1)

        tk.Label(form_frame, text="Quantity:").grid(row=1, column=0)
        self.product_quantity_entry = tk.Entry(form_frame)
        self.product_quantity_entry.grid(row=1, column=1)

        tk.Label(form_frame, text="Price:").grid(row=2, column=0)
        self.product_price_entry = tk.Entry(form_frame)
        self.product_price_entry.grid(row=2, column=1)

        tk.Button(form_frame, text="Add Product", command=self.add_product).grid(row=3, column=0, pady=5)
        tk.Button(form_frame, text="Update Product", command=self.update_product).grid(row=3, column=1, pady=5)
        tk.Button(form_frame, text="Delete Product", command=self.delete_product).grid(row=3, column=2, pady=5)

        # Product Table
        self.product_tree = ttk.Treeview(frame, columns=("ID", "Name", "Quantity", "Price"), show="headings")
        self.product_tree.heading("ID", text="ID")
        self.product_tree.heading("Name", text="Name")
        self.product_tree.heading("Quantity", text="Quantity")
        self.product_tree.heading("Price", text="Price")

        self.product_tree.pack(pady=10)
        self.load_products()

    def add_product(self):
        name = self.product_name_entry.get()
        quantity = self.product_quantity_entry.get()
        price = self.product_price_entry.get()

        if name and quantity.isdigit() and price.replace(".", "", 1).isdigit():
            cursor.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", 
                           (name, int(quantity), float(price)))
            conn.commit()
            self.load_products()
            self.update_dashboard()
        else:
            messagebox.showerror("Error", "Invalid input")

    def update_product(self):
        selected_item = self.product_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No product selected")
            return

        product_id = self.product_tree.item(selected_item)['values'][0]
        name = self.product_name_entry.get()
        quantity = self.product_quantity_entry.get()
        price = self.product_price_entry.get()

        if name and quantity.isdigit() and price.replace(".", "", 1).isdigit():
            cursor.execute("UPDATE products SET name=?, quantity=?, price=? WHERE id=?", 
                           (name, int(quantity), float(price), product_id))
            conn.commit()
            self.load_products()
            self.update_dashboard()
        else:
            messagebox.showerror("Error", "Invalid input")

    def delete_product(self):
        selected_item = self.product_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No product selected")
            return

        product_id = self.product_tree.item(selected_item)['values'][0]
        cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()
        self.load_products()
        self.update_dashboard()

    def load_products(self):
        self.product_tree.delete(*self.product_tree.get_children())
        cursor.execute("SELECT * FROM products")
        for row in cursor.fetchall():
            self.product_tree.insert("", "end", values=row)

    # ------------------ Employee Management ------------------
    def setup_employee_tab(self):
        frame = self.employee_frame

        # Employee Form
        form_frame = tk.Frame(frame)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Employee Name:").grid(row=0, column=0)
        self.employee_name_entry = tk.Entry(form_frame)
        self.employee_name_entry.grid(row=0, column=1)

        tk.Label(form_frame, text="Age:").grid(row=1, column=0)
        self.employee_age_entry = tk.Entry(form_frame)
        self.employee_age_entry.grid(row=1, column=1)

        tk.Button(form_frame, text="Add Employee", command=self.add_employee).grid(row=2, column=0, pady=5)
        tk.Button(form_frame, text="Delete Employee", command=self.delete_employee).grid(row=2, column=1, pady=5)

        # Employee Table
        self.employee_tree = ttk.Treeview(frame, columns=("ID", "Name", "Age"), show="headings")
        self.employee_tree.heading("ID", text="ID")
        self.employee_tree.heading("Name", text="Name")
        self.employee_tree.heading("Age", text="Age")

        self.employee_tree.pack(pady=10)
        self.load_employees()

    def add_employee(self):
        name = self.employee_name_entry.get()
        age = self.employee_age_entry.get()

        if name and age.isdigit():
            cursor.execute("INSERT INTO employees (name, age) VALUES (?, ?)", (name, int(age)))
            conn.commit()
            self.load_employees()
            self.update_dashboard()
        else:
            messagebox.showerror("Error", "Invalid input")

    def delete_employee(self):
        selected_item = self.employee_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No employee selected")
            return

        emp_id = self.employee_tree.item(selected_item)['values'][0]
        cursor.execute("DELETE FROM employees WHERE emp_id=?", (emp_id,))
        conn.commit()
        self.load_employees()
        self.update_dashboard()

    def load_employees(self):
        self.employee_tree.delete(*self.employee_tree.get_children())
        cursor.execute("SELECT * FROM employees")
        for row in cursor.fetchall():
            self.employee_tree.insert("", "end", values=row)

    def update_dashboard(self):
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM employees")
        employee_count = cursor.fetchone()[0]

        self.product_count_label.config(text=f"Total Products: {product_count}")
        self.employee_count_label.config(text=f"Total Employees: {employee_count}")


# Run the app
root = tk.Tk()
app = InventoryApp(root)
root.mainloop()
