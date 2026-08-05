# Import statements
import json
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog  # Importing simpledialog separately
from PIL import Image, ImageTk
import os
import ctypes # To set the taskbar icon on windows
import uuid # Importing the uuid module for generating unique teacher Ids
from pathlib import Path

BASE_DIR = Path("//Telix_School_Management_System_new//assets//images//telix_image.ico").resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"



#Code to load teacher_records  
def load_teacher_records(self):
        try:
            with open("teacher_records.json","r") as file:
                self.teachers = json.load(file)
        except FileNotFoundError:
            #If the file is doesn't exist, initialize an empty list
            self.teachers = []    


#Code to add a new teacher record
def add_teacher(self):
        #Gather Teacher information
        teacher_id = str(uuid.uuid4())[:8] # Generate unique teacher ID
        teacher_name = simpledialog.askstring("Add Teacher", "Enter teacher's name")
        teacher_dob = simpledialog.askstring("Add Teacher", "Enter teacher's date of birth (YYYY-MM-DD)")
        teacher_class = simpledialog.askstring("Add Teacher ", "Enter teacher's class/grade: ")
        teacher_salary = simpledialog.askinteger("Add Teacher ", "Enter teacher's salary")
        teacher_gender = simpledialog.askstring("Add Teacher "," Enter teacher's gender")
        teacher_address = simpledialog.askstring("Add Teacher ", "Enter teacher's address")
        teacher_contact = simpledialog.askstring("Ask Teacher ", "Enter teacher's contact info")
        teacher_medical_info = simpledialog.askstring("Ask Teacher ", "Enter teacher's medical info")
        teacher_email_address = simpledialog.askstring("Ask Teacher ", "Enter teacher's email address")
        teacher_emergency_contact = simpledialog.askstring("Ask Teacher", "Enter teacher's emergency contact")
        
        
        # Create Teacher dictionary
        teacher = {
            "TID" : teacher_id,
            "Teacher Name" : teacher_name,
            "Teacher DOB" : teacher_dob,
            "Teacher Class" : teacher_class,
            "Teacher Salary" : teacher_salary,
            "Teacher Gender" : teacher_gender,
            "Teacher Address" : teacher_address,
            "Teacher Contact" : teacher_contact,
            "Teacher MedicalInfo" : teacher_medical_info,
            "Teacher Email Address" : teacher_email_address,
            "Teacher Emergency Contact" : teacher_emergency_contact
        }
        
        #Add teacher to the list
        self.teachers.append(teacher)
        
        #Show success message
        messagebox.showinfo("Success " , f"Teacher {teacher_name} added successfully with TID {teacher_id} .")
        
        pass
            
#Code to delete a teacher record            
def delete_teacher(self):
        teacher_name = simpledialog.askstring("Delete Teacher", "Enter Teacher's name to delete:")
        if teacher_name:
            deleted = False
            for teacher in self.teachers[:]:
                if teacher ["Teacher Name"] == teacher_name:
                    self.teachers.remove(teacher)
                    deleted = True
            if deleted:
                messagebox.showinfo("Succes", f"All records of teacher {teacher_name} have been deleted.")
            else:
                messagebox.showerror("Error", f"Teacher '{teacher_name}' not found.")
                teacher_id = simpledialog.askstring("Delete Teacher", "Enter Teacher's ID to delete:")
                if teacher_id:
                    deleted = False
                    for teacher in self.teachers[:]:
                        if teacher["TID"] == teacher_id:
                            self.teachers.remove(teacher)
                            deleted = True
                            if deleted :
                                messagebox.showinfo("Success", f"All records of teacher {teacher_id} have been deleted.")
                            else:
                                messagebox.showerror("Error", f"Teacher '{teacher_name}' not found.")              

#Code to modify teacher record
def modify_teacher(self):
        teacher_name = simpledialog.askstring("Modify Teacher","Enter teacher's name to modify:")
        if teacher_name:
           for teacher in self.teachers:
               if teacher["Teacher Name"] == teacher_name:
                   #Allow modification of Teacher information
                   teacher["Teacher Name"] = simpledialog.askstring("Modify Teacher", "Enter teacher's new name:", initialvalue=teacher["Teacher Name"])
                   teacher["Teacher DOB"]=simpledialog.askstring("Modify Teacher", "Enter teacher's new date fo birth (YYYY-MM-DD):", initialvalue=teacher["Teacher DOB"])
                   teacher["Teacher Class"]=simpledialog.askstring("Modify Teacher", "Enter teacher's new class/grade:", initialvalue=teacher["Teacher Class"])
                   teacher["Teacher Salary"]=simpledialog.askstring("Modify Teacher","Enter teacher's new salary:", initialvalue=teacher["Teacher Salary"])
                   teacher["Teacher Gender"]=simpledialog.askstring("Modify Teacher", "Enter teacher's new gender:", initialvalue=teacher["Teacher Gender"])
                   teacher["Teacher Address"]=simpledialog.askstring("Modify Teacher", "Enter teacher's new address:", initialvalue=teacher["Teacher Address"])
                   teacher["Teacher Contact"]=simpledialog.askstring("Modify Teacher", "Enter teacher's new contact:", initialvalue=teacher["Teacher Contact"])
                   teacher["Teacher MedicalInfo"]=simpledialog.askstring("Modify Teacher", "Enter teacher's new medical info:", initialvalue=teacher["Teacher MedicalInfo"])
                   teacher["Teacher Email Address"]=simpledialog.askstring("Modify Teacher", "Enter teacher's new email address:", initialvalue=teacher["Teacher Email Address"])
                   teacher["Teacher Emergency Contact"]=simpledialog.askstring("Modify Teacher","Enter teacher's new emergency contact:",initialvalue=teacher["Teacher Emergency contact"])
                   messagebox.showinfo("Success",f"Information of teacher {teacher_name} has been mofified.")
                   return
        messagebox.showerror("Error", f"Teacher '{teacher_name}' not found.")

#Code to view teacher records
def view_teacher_records(self):
        # Check if the teacher records window is already open
        if hasattr(self, "teacher_records_window") and self.teacher_records_window.winfo_exists():
            # If it's open, bring it to focus and return
            self.teacher_records_window.lift()
            return  
        
        # Create a new window to display teacher records
        self.teacher_records_window = tk.Toplevel(self.master)
        self.teacher_records_window.title("Teacher Records")
        self.teacher_records_window.geometry("1000x800")  # Adjust the window size as needed

        # Create a frame to hold the teacher records
        records_frame = tk.Frame(self.teacher_records_window)
        records_frame.pack(fill=tk.BOTH, expand=True)

        # Add a scrollbar to the frame
        scrollbar = tk.Scrollbar(records_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a canvas to scroll the frame
        canvas = tk.Canvas(records_frame, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure the scrollbar to scroll the canvas
        scrollbar.config(command=canvas.yview)

        # Create another frame inside the canvas to hold the teacher records
        teacher_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=teacher_frame, anchor=tk.NW)

        # Function to update the scroll region when the size of the teacher frame changes
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        teacher_frame.bind("<Configure>", on_frame_configure)

        # Iterate over the teacher list and display their information
        for index, teacher in enumerate(self.teachers, start=1):
            teacher_label = tk.Label(teacher_frame, text=f"Teacher {index}:", font=("Arial", 12, "bold"))
            teacher_label.grid(row=index, column=0, sticky="w")

            # Display teacher information
            for row , (key, value) in enumerate(teacher.items(), start=index):
                info_label = tk.Label(teacher_frame, text=f"{key}: {value}" , wraplength=500 , justify="left")
                info_label.grid(row=row, column=1, sticky="w")

        # Update the scroll region to fit the contents of the teacher frame
        teacher_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

#code for teacher_widgets
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
