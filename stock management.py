import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib import pyplot as plt
from datetime import datetime

# Database Connection
conn = sqlite3.connect("new_inventory.db")  # New database
cursor = conn.cursor()

# Create Tables
cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    expiry_date TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
                    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL)''')

conn.commit()

# Sample data for testing alerts
cursor.execute("SELECT COUNT(*) FROM products")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO products (name, quantity, price, expiry_date) VALUES (?, ?, ?, ?)",
                   ("Test Expired Product", 10, 50.0, "2023-01-01"))
    cursor.execute("INSERT INTO products (name, quantity, price, expiry_date) VALUES (?, ?, ?, ?)",
                   ("Test Low Stock Product", 3, 30.0, "2025-12-31"))
    conn.commit()

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("900x500")

        # Dashboard Frame
        self.dashboard_frame = tk.Frame(root)
        self.dashboard_frame.pack(pady=10)

        self.product_count_label = tk.Label(self.dashboard_frame, text="Total Products: 0", font=("Arial", 12, "bold"))
        self.product_count_label.pack(side=tk.LEFT, padx=20)

        self.employee_count_label = tk.Label(self.dashboard_frame, text="Total Employees: 0", font=("Arial", 12, "bold"))
        self.employee_count_label.pack(side=tk.LEFT, padx=20)

        self.update_dashboard()

        # Tabs
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(expand=1, fill="both")

        self.product_frame = ttk.Frame(self.tabs)
        self.employee_frame = ttk.Frame(self.tabs)

        self.tabs.add(self.product_frame, text="Products")
        self.tabs.add(self.employee_frame, text="Employees")

        self.setup_product_tab()
        self.setup_employee_tab()

        # Check alerts continuously
        self.root.after(1000, self.check_alerts)

    def setup_product_tab(self):
        frame = self.product_frame

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

        tk.Label(form_frame, text="Expiry Date (YYYY-MM-DD):").grid(row=3, column=0)
        self.product_expiry_entry = tk.Entry(form_frame)
        self.product_expiry_entry.grid(row=3, column=1)

        tk.Button(form_frame, text="Add Product", command=self.add_product).grid(row=4, column=0, pady=5)
        tk.Button(form_frame, text="Update Product", command=self.update_product).grid(row=4, column=1, pady=5)
        tk.Button(form_frame, text="Delete Product", command=self.delete_product).grid(row=4, column=2, pady=5)
        tk.Button(frame, text="Show Stock Graph", command=self.show_stock_graph).pack(pady=5)

        self.product_tree = ttk.Treeview(frame, columns=("ID", "Name", "Quantity", "Price", "Expiry Date"), show="headings")
        for col in ("ID", "Name", "Quantity", "Price", "Expiry Date"):
            self.product_tree.heading(col, text=col)
        self.product_tree.pack(pady=10)

        self.load_products()

    def add_product(self):
        name = self.product_name_entry.get()
        quantity = self.product_quantity_entry.get()
        price = self.product_price_entry.get()
        expiry = self.product_expiry_entry.get()

        if name and quantity.isdigit():
            try:
                price = float(price)
                datetime.strptime(expiry, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid price or date format")
                return

            cursor.execute("INSERT INTO products (name, quantity, price, expiry_date) VALUES (?, ?, ?, ?)",
                           (name, int(quantity), price, expiry))
            conn.commit()
            self.load_products()
            self.update_dashboard()

            self.product_name_entry.delete(0, tk.END)
            self.product_quantity_entry.delete(0, tk.END)
            self.product_price_entry.delete(0, tk.END)
            self.product_expiry_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Invalid input")

    def update_product(self):
        selected_item = self.product_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "No product selected")
            return

        product_id = self.product_tree.item(selected_item)['values'][0]
        name = self.product_name_entry.get()
        quantity = self.product_quantity_entry.get()
        price = self.product_price_entry.get()
        expiry = self.product_expiry_entry.get()

        if name and quantity.isdigit():
            try:
                price = float(price)
                datetime.strptime(expiry, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid price or date format")
                return

            cursor.execute("UPDATE products SET name=?, quantity=?, price=?, expiry_date=? WHERE id=?",
                           (name, int(quantity), price, expiry, product_id))
            conn.commit()
            self.load_products()
            self.update_dashboard()
        else:
            messagebox.showerror("Error", "Invalid input")

    def delete_product(self):
        selected_item = self.product_tree.focus()
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
        cursor.execute("SELECT id, name, quantity, price, expiry_date FROM products")
        for row in cursor.fetchall():
            self.product_tree.insert("", "end", values=row)

    def show_stock_graph(self):
        cursor.execute("SELECT name, quantity FROM products")
        data = cursor.fetchall()
        if not data:
            messagebox.showinfo("Info", "No products to display.")
            return

        names = [row[0] for row in data]
        quantities = [row[1] for row in data]

        plt.figure(figsize=(8, 5))
        plt.bar(names, quantities, color='skyblue')
        plt.xlabel('Product Name')
        plt.ylabel('Quantity')
        plt.title('Product Stock Levels')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def setup_employee_tab(self):
        frame = self.employee_frame

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

        self.employee_tree = ttk.Treeview(frame, columns=("ID", "Name", "Age"), show="headings")
        for col in ("ID", "Name", "Age"):
            self.employee_tree.heading(col, text=col)
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

            self.employee_name_entry.delete(0, tk.END)
            self.employee_age_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Invalid input")

    def delete_employee(self):
        selected_item = self.employee_tree.focus()
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

    def check_alerts(self):
        stockout_items = []
        expired_items = []
        today = datetime.today().date()

        cursor.execute("SELECT name, quantity, expiry_date FROM products")
        for row in cursor.fetchall():
            name, quantity, expiry = row
            if quantity <= 5:
                stockout_items.append(name)

            try:
                expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
                if expiry_date < today:
                    expired_items.append(name)
            except Exception as e:
                print(f"Date error for {name}: {e}")

        if stockout_items:
            messagebox.showwarning("Stock Alert", f"Low stock for: {', '.join(stockout_items)}")

        if expired_items:
            messagebox.showerror("Expiry Alert", f"Expired products: {', '.join(expired_items)}")

        # Check again after 10 seconds
        self.root.after(10000, self.check_alerts)

def on_closing():
    conn.close()
    root.destroy()

root = tk.Tk()
app = InventoryApp(root)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()


      