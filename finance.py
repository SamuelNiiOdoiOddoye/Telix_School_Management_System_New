# Import statements
import json
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog  # Importing simpledialog separately
from PIL import Image, ImageTk
import os
import ctypes # To set the taskbar icon on windows 
 
#Code For the Profit/Loss module
def check_profit_loss(self):
        profit_loss_window = tk.Toplevel(self.master)
        profit_loss_window.title("Profit/Loss Analysis")
        profit_loss_window.geometry("400x300")

        # Calculations
        total_income = sum(student["Fees"] for student in self.students)
        total_expense = sum(teacher["Teacher Salary"] for teacher in self.teachers)
        profit_loss = total_income - total_expense

        # Display results
        tk.Label(profit_loss_window, text=f"Total Income: {total_income}").pack(pady=10)
        tk.Label(profit_loss_window, text=f"Total Expenses: {total_expense}").pack(pady=10)
        tk.Label(profit_loss_window, text=f"Profit/Loss: {profit_loss}").pack(pady=10)

        if profit_loss > 0:
            tk.Label(profit_loss_window, text="Profit", fg="green").pack(pady=10)
        else:
            tk.Label(profit_loss_window, text="Loss", fg="red").pack(pady=10)
