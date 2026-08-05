# Import statements
import json
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog  # Importing simpledialog separately
from PIL import Image, ImageTk
import os
import ctypes # To set the taskbar icon on windows
import uuid
from pathlib import Path

from students import save_student_records # Importing the uuid module for generating unique student Ids

# Create the main window
root = tk.Tk()

class SchoolManagementSystem:
    def __init__(self, master):
        self.master = master
        self.master.title("Telix School Management System")
        BASE_DIR = Path(__file__).resolve().parent
        Telix_Icon_Path = BASE_DIR / "assets" / "images" / "telix_image.ico"
        self.master.geometry("600x400")
        
    # Load the .png icon image and convert it to PhotoImage for the title bar
        icon_image = Image.open(Telix_Icon_Path)
        icon_photo = ImageTk.PhotoImage(icon_image)
        

    # Set the application icon for the title bar
        self.master.iconphoto(True, icon_photo) 
        
    # Set the icon for the taskbar on windows
        if os.name == 'nt' : #check if running windows
            #Convert the image to .ico format (you can use the actual .ico file here if available)
            icon_path = Telix_Icon_Path
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("telixinc.SMSapp")
        self.master.wm_iconbitmap(Telix_Icon_Path)  # Set the icon for the taskbar on Windows
        
        self.students = []
        self.teachers = []
        self.total_income = 0
        self.total_expense = 0
        
        #load existing student records from file
        self.load_student_records()
        self.create_widgets()

    #code to import student functions from students.py
    from students import(
        load_student_records,
        add_student,
        modify_student,
        save_student_records,
        delete_student,
        view_student_records,
        view_student_records,
        student_widgets,
    )
        
    #Code to import teacher functions from teachers.py
    from teachers import(
        add_teacher,
        modify_teacher,
        delete_teacher,
        view_teacher_records
    )
    
    #code to import finance functions from finance.py
    from finance import(
        check_profit_loss
    )
    
    #code to import academic recor functions from academic_records.py
    from academic_records import(
        add_academic_records,
        modify_academic_records,
        view_academic_records
    )

    #Code to create widgets
    def create_widgets(self):
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
    
def main():
    app = SchoolManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()
