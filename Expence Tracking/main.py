import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import matplotlib.pyplot as plt
from tkcalendar import DateEntry

# Database Setup
def init_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        category TEXT,
                        amount REAL,
                        description TEXT,
                        user_id INTEGER,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

def signup():
    def register():
        new_username = new_username_entry.get()
        new_password = new_password_entry.get()
        
        if not new_username or not new_password:
            messagebox.showerror("Error", "All fields are required")
            return
        
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_username, new_password))
            conn.commit()
            messagebox.showinfo("Success", "User registered successfully!")
            signup_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        conn.close()
    
    signup_window = tk.Toplevel(login_window)
    signup_window.title("Signup")
    signup_window.geometry("300x200")
    tk.Label(signup_window, text="New Username:").pack()
    new_username_entry = tk.Entry(signup_window)
    new_username_entry.pack()
    tk.Label(signup_window, text="New Password:").pack()
    new_password_entry = tk.Entry(signup_window, show="*")
    new_password_entry.pack()
    tk.Button(signup_window, text="Register", command=register).pack()

# User Authentication
def login():
    username = username_entry.get()
    password = password_entry.get()
    
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        global current_user_id
        current_user_id = user[0]
        login_window.destroy()
        main_app()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

def clear_fields():
    date_entry.set_date(datetime.date.today())
    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    category_var.set("Others")

# Add Expense
def add_expense():
    date = date_entry.get()
    category = category_var.get()
    amount = amount_entry.get()
    description = description_entry.get()
    
    if not date or not category or not amount:
        messagebox.showwarning("Input Error", "Please fill in all required fields.")
        return
    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Input Error", "Amount must be a number.")
        return
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (user_id, date, category, amount, description) VALUES (?, ?, ?, ?, ?)",
                   (current_user_id, date, category, amount, description))
    conn.commit()
    conn.close()
    load_expenses()
    clear_fields()

# Edit Expense
def edit_expense():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select an expense to edit.")
        return
    
    item = tree.item(selected_item[0], "values")  # Ensure first selected item is used
    if not item or len(item) < 5:
        messagebox.showerror("Data Error", "Selected item does not contain expected values.")
        return
    
    expense_id, date, category, amount, description = item[:5]
    
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Expense")
    edit_window.geometry("300x250")
    
    tk.Label(edit_window, text="Date:").pack()
    date_entry = DateEntry(edit_window)
    date_entry.set_date(date)
    date_entry.pack()
    
    tk.Label(edit_window, text="Category:").pack()
    category_var = tk.StringVar(value=category)
    tk.Entry(edit_window, textvariable=category_var).pack()
    
    tk.Label(edit_window, text="Amount:").pack()
    amount_entry = tk.Entry(edit_window)
    amount_entry.insert(0, amount)
    amount_entry.pack()
    
    tk.Label(edit_window, text="Description:").pack()
    description_entry = tk.Entry(edit_window)
    description_entry.insert(0, description)
    description_entry.pack()
    
    def update_expense():
        new_date = date_entry.get()
        new_category = category_var.get()
        new_amount = amount_entry.get()
        new_description = description_entry.get()
        
        try:
            new_amount = float(new_amount)
        except ValueError:
            messagebox.showerror("Input Error", "Amount must be a number.")
            return
        
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE expenses SET date=?, category=?, amount=?, description=? WHERE id=?",
                       (new_date, new_category, new_amount, new_description, expense_id))
        conn.commit()
        conn.close()
        load_expenses()
        edit_window.destroy()
    
    tk.Button(edit_window, text="Update", command=update_expense).pack()

# Load Expenses
def load_expenses():
    for row in tree.get_children():
        tree.delete(row)
    
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE user_id=? ORDER BY date DESC", (current_user_id,))
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)
    conn.close()

def delete_expense():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select an expense to delete.")
        return
    
    item = tree.item(selected_item[0], "values")
    if not item:
        return
    
    expense_id = item[0]
    
    confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this expense?")
    if confirm:
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        conn.commit()
        conn.close()
        load_expenses()
        messagebox.showinfo("Success", "Expense deleted successfully.")

# Expense Categories Pie Chart
def show_pie_chart():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        messagebox.showinfo("No Data", "No expenses available to display.")
        return
    
    categories, amounts = zip(*data)
    plt.figure(figsize=(6,6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title("Expense Categories Distribution")
    plt.show()

# Dark and Light Mode Toggle
def toggle_theme():
    global dark_mode
    if dark_mode:
        root.tk_setPalette(background="white", foreground="black")
        dark_mode = False
    else:
        root.tk_setPalette(background="grey", foreground="white") # black doesn't look good 
        dark_mode = True
    root.update()

# Main GUI
def main_app():
    global root, date_entry, category_var, amount_entry, description_entry, tree, dark_mode
    dark_mode = False
    root = tk.Tk()
    root.title("Expense Tracker")
    root.geometry("700x500")
    
    frame = tk.Frame(root)
    frame.pack(pady=10)
    
    tk.Label(frame, text="Date:").grid(row=0, column=0)
    date_entry = DateEntry(frame, width=12)
    date_entry.grid(row=0, column=1)
    
    category_var = tk.StringVar(value="Food")
    tk.Label(frame, text="Category:").grid(row=1, column=0)
    category_menu = ttk.Combobox(frame, textvariable=category_var, values=["Food", "Transport", "Bills", "Entertainment", "Others"])
    category_menu.grid(row=1, column=1)
    
    amount_entry = tk.Entry(frame)
    tk.Label(frame, text="Amount:").grid(row=2, column=0)
    amount_entry.grid(row=2, column=1)
    
    description_entry = tk.Entry(frame)
    tk.Label(frame, text="Description:").grid(row=3, column=0)
    description_entry.grid(row=3, column=1)
    
    tk.Button(frame, text="Add Expense", command=add_expense).grid(row=4, column=0, columnspan=2)
    tk.Button(frame, text="Edit Expense", command=edit_expense).grid(row=5, column=0, columnspan=2)
    
    tree = ttk.Treeview(root, columns=("ID", "Date", "Category", "Amount", "Description"), show="headings")
    for col in ("ID", "Date", "Category", "Amount", "Description"):
        tree.heading(col, text=col)
    tree.pack()
    toggle_button = tk.Button(root, text="Toggle Theme", command=toggle_theme)
    toggle_button.place(relx=0.9, rely=0.05, anchor="ne")
    button_frame = tk.Frame(root)
    button_frame.pack(side="bottom", pady=20)
    pie_chart_button = tk.Button(button_frame, text="Show Pie Chart", command=show_pie_chart)
    pie_chart_button.grid(row=0, column=0, padx=10)
    delete_button = tk.Button(button_frame, text="Delete Expense", command=delete_expense)
    delete_button.grid(row=0, column=1, padx=10)
    load_expenses()
    root.mainloop()

init_db()
# Login Window
login_window = tk.Tk()
login_window.geometry("300x200")
login_window.title("Login")
tk.Label(login_window, text="Username:").pack()
username_entry = tk.Entry(login_window)
username_entry.pack()
tk.Label(login_window, text="Password:").pack()
password_entry = tk.Entry(login_window, show="*")
password_entry.pack()
tk.Button(login_window, text="Login", command=login).pack()
tk.Button(login_window, text="Signup", command=signup).pack()
login_window.mainloop()
