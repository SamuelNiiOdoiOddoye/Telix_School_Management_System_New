# Import statements
import json
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog  # Importing simpledialog separately
from PIL import Image, ImageTk
import os
import ctypes # To set the taskbar icon on windows
import uuid # Importing the uuid module for generating unique student Ids

#Code to load student_records  
def load_student_records(self):
        try:
            with open("student_records.json","r") as file:
                self.students = json.load(file)
        except FileNotFoundError:
            #If the file is doesn't exist, initialize an empty list
            self.students = []    
        
        
#Code to save student records    
def save_student_records(self):
        with open("student_records.json","w") as file:
            json.dump(self.students, file , indent=4)                

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
        self.lbl_title = tk.Label(self.master, text="School Management System", font=("Arial", 16), bg=bg_color , fg="#FF5733")
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


#Code to add a new student record
def add_student(self):
        #Gather Student information
        #if it's open, bring it to focus
        if hasattr(self, "add_student_window") and self.add_student_window.winfo_exists():
            self.add_student_records_window.lift()
            
        student_id = str(uuid.uuid4())[:8] # Generate unique student ID
        student_name = simpledialog.askstring("Add Student", "Enter student's name")
        if student_name is not None: #Check if input is None
            student_dob = simpledialog.askstring("Add Student ", "Enter student's date of birth (YYYY-MM-DD)")
            if student_dob is not None:
                student_class = simpledialog.askstring("Add Student ", "Enter students class/grade: ")
                if student_class is not None:
                    student_fees = simpledialog.askinteger("Add Student ", "Enter student's school fees")
                    if student_fees is not None:
                        student_gender = simpledialog.askstring("Add Student "," Enter student gender")
                        if student_gender is not None:
                            student_address = simpledialog.askstring("Add Student ", "Enter student's address")
                            if student_address is not None:
                                student_contact = simpledialog.askstring("Ask Student ", "Enter student's contact info")
                                if student_contact is not None:
                                    student_medical_info = simpledialog.askstring("Ask Student ", "Enter students medical info")
                                    student_email_address = simpledialog.askstring("Ask Student ", "Enter students email address")
                                    if student_email_address is not None:
                                        student_emergency_contact = simpledialog.askstring("Ask Student", "Enter student's emergency contact")
        
        # Create student dictionary
        student = {
            "ID" : student_id,
            "Name" : student_name,
            "DOB" : student_dob,
            "Class" : student_class,
            "Fees" : student_fees,
            "Gender" : student_gender,
            "Address" : student_address,
            "Contact" : student_contact,
            "MedicalInfo" : student_medical_info,
            "Email Address" : student_email_address,
            "Emergency Contact" : student_emergency_contact
        }
        
        #Add student to the list
        self.students.append(student)
        
        #save student records to file
        self.save_student_records()
        
        #show success message
        messagebox.showinfo("Success", f"Student {student_name} added successfully with ID {student_id}.")
        
        pass

#Code to delete a student record
def delete_student(self):
        student_name = simpledialog.askstring("Delete Student", "Enter Student's name to delete:")
        if student_name:
            deleted = False
            for student in self.students[:]:
                if student ["Name"] == student_name:
                    self.students.remove(student)
                    deleted = True
            if deleted:
                messagebox.showinfo("Success", f"All records of student {student_name} have been deleted.")
            else:
                student_id = simpledialog.askstring("Delete Student", "Enter Student's ID to delete:")
                if student_id:
                    deleted = False
                    for student in self.students[:]:
                        if student["ID"] == student_id:
                           self.students.remove(student)
                           deleted = True
                    if deleted :
                        messagebox.showinfo("Success", f"All records of student {student_id} have been deleted.")
                    else:
                        messagebox.showerror("Error", f"Student '{student_name}' not found.")            
    
#Code to modify student records
def modify_student(self):
        student_name = simpledialog.askstring("Modify Student","Enter student's name to modify:")
        if student_name:
           for student in self.students:
               if student["Name"] == student_name:
                #Allow modification of student information
                student["Name"] = simpledialog.askstring("Modify Student", "Enter student's new name:", initialvalue=student["Name"])
                student["DOB"] = simpledialog.askstring("Modify Student", "Enter student's new date of birth (YYYY-MM-DD):", initialvalue=student["DOB"])
                student["Class"] = simpledialog.askstring("Modify Student", "Enter student's new class/grade:", initialvalue=student["Class"])
                student["Fees"] = simpledialog.askinteger("Modify Student", "Enter student's new fees:", initialvalue=student["Fees"])
                student["Gender"] = simpledialog.askstring("Modify Student", "Enter student's new gender:", initialvalue=student["Gender"])
                student["Address"] = simpledialog.askstring("Modify Student", "Enter student's new address:", initialvalue=student["Address"])
                messagebox.showinfo("Success", f"Information of student {student_name} has been modified.")
                return
        messagebox.showerror("Error", f"Student '{student_name}' not found.")    

#Code to view student records
def view_student_records(self):
        # Check if the student records window is already open
        if hasattr(self, "student_records_window") and self.student_records_window.winfo_exists():
            # If it's open, bring it to focus and return
            self.student_records_window.lift()
            return
        
        # Message to display if there's no student record
        if not self.students:
            messagebox.showinfo("No Records " , "No Student Records found")
            return
        
        # Create a new window to display student records
        self.student_records_window = tk.Toplevel(self.master)
        self.student_records_window.title("Student Records")
        self.student_records_window.geometry("1000x800")  # Adjust the window size as needed

        # Create a frame to hold the student records
        records_frame = tk.Frame(self.student_records_window)
        records_frame.pack(fill=tk.BOTH, expand=True)

        # Add a scrollbar to the frame
        scrollbar = tk.Scrollbar(records_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a canvas to scroll the frame
        canvas = tk.Canvas(records_frame, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure the scrollbar to scroll the canvas
        scrollbar.config(command=canvas.yview)

        # Create another frame inside the canvas to hold the student records
        student_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=student_frame, anchor=tk.NW)

        # Function to update the scroll region when the size of the student frame changes
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        student_frame.bind("<Configure>", on_frame_configure)
        
        # Initialize counters
        index = 0 # controls grid row position
        student_num = 1 # controls student numbering

        # Iterate over the students list and display their information
        for student in self.students:
            # Create a label for each student with an orderly number 
            student_label = tk.Label(student_frame, text=f"Student {student_num}:", font=("Arial", 12, "bold"))
            student_label.grid(row=index, column=0, sticky="w")
            index += 1 # Increment index for each new student
            student_num += 1 # Increement student number for the next student

            # Display student information in the next rows
            for key,value in student.items():
                info_label = tk.Label(student_frame, text=f"{key}: {value}" , wraplength=600 , justify="left")
                info_label.grid(row=index, column=1, sticky="w")
                index += 1 # Move to the next row for each key-value pair

            # Update the scroll region to fit the contents of the student frame
            student_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))

