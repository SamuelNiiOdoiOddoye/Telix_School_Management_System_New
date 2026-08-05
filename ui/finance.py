# Import statements
import json
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog  # Importing simpledialog separately
from PIL import Image, ImageTk
import os
import ctypes # To set the taskbar icon on windows 
from pathlib import Path

BASE_DIR = Path("//Telix_School_Management_System_new//assets//images//telix_image.ico").resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
 
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


#code to create widgets for the finance module
            def finance_widgets(self):
                # Define color variables
                bg_color = "#808080"  # Light gray for background
                text_color = "#333333"  # Dark gray for text
                btn_bg_color = "#4CAF50"  # Green for buttons
                btn_text_color = "white"  # White text for buttons

                # set background color for the main window
                self.master.configure(bg="#808080")

                #Title Label
                self.lbl_title = tk.Label(self.master, text="Telix School Management System", font=("Arial", 16), bg=bg_color , fg="#FF5733")
                self.lbl_title.pack()

                #Add student button
                self.btn_add_student = tk.Button(self.master, text="Add Student", command=self.add_student, bg="#FF5733", fg=btn_text_color)
                self.btn_add_student.pack()

                #Delete student button
                self.btn_delete_student = tk.Button(self.master, text="Delete Student", command=self.delete_student, bg="#FF5733", fg=btn_text_color)
                self.btn_delete_student.pack()

                #Modify student button
                self.btn_modify_student = tk.Button(self.master, text="Modify Student", command=self.modify_student, bg="#FF5733", fg=btn_text_color)
                self.btn_modify_student.pack()

                #Add Academic Records button
                self.btn_add_academic_records = tk.Button(self.master, text="Add Academic Records", command=self.add_academic_records, bg="#FF5733" , fg=btn_text_color)
                self.btn_add_academic_records.pack()

                #Modify academic records
                self.btn_modify_academic_records = tk.Button(self.master, text="Modify Academic Records", command=self.modify_academic_records, bg="#FF5733" , fg=btn_text_color)
                self.btn_modify_academic_records.pack()

                #View student records
                self.btn_view_student_records = tk.Button(self.master, text="View Student Records", command=self.view_student_records, bg="#FF5733", fg=btn_text_color)
                self.btn_view_student_records.pack()

                #Add teacher button
                self.btn_add_teacher = tk.Button(self.master, text="Add Teacher", command=self.add_teacher, bg="#FF5733", fg=btn_text_color)
                self.btn_add_teacher.pack()

                #modify teacher button
                self.btn_modify_teacher = tk.Button(self.master, text="Modify Teacher", command=self.modify_teacher, bg="#FF5733", fg=btn_text_color)
                self.btn_modify_teacher.pack()

                #view teacher records button    
                self.btn_view_teacher_records = tk.Button(self.master, text="View Teacher Records", command=self.view_teacher_records, bg="#FF5733", fg=btn_text_color)
                self.btn_view_teacher_records.pack()

                #view records button 
                self.btn_view_records = tk.Button(self.master, text="View Records", command=self.view_records, bg="#FF5733", fg=btn_text_color)
                self.btn_view_records.pack()

                #check profit/loss button
                self.btn_check_profit = tk.Button(self.master, text="Check Profit/Loss", command=self.check_profit_loss, bg="#FF5733", fg=btn_text_color)
                self.btn_check_profit.pack()
