# Import statements
import json
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog  # Importing simpledialog separately
from PIL import Image, ImageTk
import os
import ctypes # To set the taskbar icon on windows
import uuid # Importing the uuid module for generating unique student Ids

# Create the main window
root = tk.Tk()

class SchoolManagementSystem:
    def __init__(self, master):
        self.master = master
        self.master.title("School Management System")
        self.master.geometry("600x400")
        
    # Load the .png icon image and convert it to PhotoImage for the title bar
        icon_image = Image.open("C:/Users/addoy/Documents/codes/Python/God's grace system/management system for god/images/Badgeimage.png")
        icon_photo = ImageTk.PhotoImage(icon_image)

    # Set the application icon for the title bar
        self.master.iconphoto(True, icon_photo) 
        
    # Set the icon for the taskbar on windows
        if os.name == 'nt' : #check if running windows
            #Convert the image to .ico format (you can use the actual .ico file here if available)
            icon_path = "C:/Users/addoy/Documents/codes/Python/God's grace system/management system for god/images/Badgeimage.ico"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("telixinc.God'sgraceschmngapp")
        self.master.wm_iconbitmap("C:/Users/addoy/Documents/codes/Python/God's grace system/management system for god/images/Badgeimage.ico")   
        
        self.students = []
        self.teachers = []
        self.total_income = 0
        self.total_expense = 0
        
        #load existing student records from file
        self.load_student_records()
        
       
        self.create_widgets()

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
                   return
        messagebox.showerror("Error", f"Student '{student_name}' not found.")

    #Code to add Student Academic Records
    def add_academic_records(self):
               #Gather Student Academic Information
        #if it's open, bring it to focus
        if hasattr(self, "add_academic_records_window") and self.add_academic_records_window.winfo_exists():
            self.add_academic_records_window.lift()
            
        Mathematics_Score = simpledialog.askinteger("Add Mathematics Score", "Enter student's mathematics score : ")
        if Mathematics_Score is not None: #Check if input is None
            English_Language_Score = simpledialog.askinteger("Add English Score ", "Enter student's English score : ")
            if English_Language_Score is not None:
                Science_Score = simpledialog.askinteger("Add Science Score ", "Enter students science score : ")
                if Science_Score is not None:
                    French_Score = simpledialog.askinteger("Add French Score ", "Enter student's french score")
                    if French_Score is not None:
                        ICT_Score = simpledialog.askinteger("Add ICT Score"," Enter student ICT score")
                        if ICT_Score is not None:
                            Ghanaian_Language_TWI_Score = simpledialog.askinteger("Add TWI Score ", "Enter TWI score")
                            if Ghanaian_Language_TWI_Score is not None:
                                Ghanaian_Language_GA_Score = simpledialog.askinteger("Add GA Score ", "Enter GA Score")
                                if Ghanaian_Language_GA_Score is not None:
                                    RME_Score = simpledialog.askinteger("Add RME Score ", "Enter RME Score")
                                    if RME_Score is not None :
                                        Creative_Arts_Score = simpledialog.askinteger("Add Creative Arts Score ", "Enter creative arts score")
                                        if Creative_Arts_Score is not None :
                                            Language_And_Literacy_Development_Score = simpledialog.askinteger(" Add Language and Literacy Score " ," Enter Language and Literacy Score")
                                            if Language_And_Literacy_Development_Score is not None:
                                                Numeracy_Score = simpledialog.askinteger(" Add Numeracy Score ", "Enter Numeracy Score")
                                                if Numeracy_Score is not None :
                                                    Environmental_Studies_Score = simpledialog.askinteger(" Add Environmental Studies Score ", "Enter Environmental Studies Score")
                                                    if English_Language_Score is not None :
                                                        Physical_Development_Score = simpledialog.askstring("Add Physical Development Score ", "Enter Physical Development Score")
                                                        if Physical_Development_Score is not None :
                                                            Social_And_Emotional_Development = simpledialog.askinteger("Add Social and Emotial Development", "Enter Social and Emotional development score")
                                                            if Social_And_Emotional_Development is not None:
                                                                Physical_Education_Score = simpledialog.askinteger("Add Physical Education Score", "Enter Physical Education Score")
                                                                if Physical_Education_Score is not None :
                                                                    Our_World_Our_People_Score = simpledialog.askinteger("Add the Our World Our people Score", "Enter the Our World Our People Score")
                                                                    if Our_World_Our_People_Score is not None :
                                                                        Social_Studies_Score = simpledialog.askinteger("Add Social Studies Score", "Enter Social Studies Score")
                                                                        if Social_Studies_Score is not None:
                                                                            Basic_Design_and_Technology_Score = simpledialog.askinteger("Add Basic Design and Technology Score","Enter Basic Design and Technology Score")
                                                                            if Basic_Design_and_Technology_Score is not None :
                                                                                Career_Technology_Score = simpledialog.askinteger("Add Career Technology Score", "Enter Career Technology Score")
                                                                                if Career_Technology_Score is not None :
                                                                                    Government_Score =simpledialog.askinteger("Add Government Score" , "Enter Government Score")
                                                                                    if Government_Score is not None :
                                                                                        Economics_Score = simpledialog.askinteger("Add Economics Score","Enter Economics Score")
                                                                                        if Economics_Score is not None :
                                                                                            Elective_Mathematics_Score = simpledialog.askinteger("Add Elective MAthematics Score","Enter Elective Mathematics Score")
                                                                                            if Elective_Mathematics_Score is not None:
                                                                                                Geography_Score = simpledialog.askinteger("Add Geography Score","Enter Geography Score")
                                                                                                if Geography_Score is not None:
                                                                                                    Elective_Physics_Score = simpledialog.askinteger("Add Elective Physics Score", "Enter Elective Physiscs Score")
                                                                                                    if Elective_Physics_Score is not None:
                                                                                                        Elective_Chemistry_Score = simpledialog.askinteger("Add Elective Chemistry Score","Enter Elective Chemistry Score")
                                                                                                        if Elective_Chemistry_Score is not None:
                                                                                                            Elective_Biology_Score = simpledialog.askinteger("Add Elective Biology Score","Enter Elective Biology Score")
                                                                                                            if Elective_Biology_Score is not None :
                                                                                                                Literature_in_English_Score = simpledialog.askinteger("Add Literature in English Score", "Enter Literature in English Score")
                                                                                                                if Literature_in_English_Score is not None:
                                                                                                                    History_Score = simpledialog.askinteger("Add History Score","Enter History Score")
                                                                                                                    if History_Score is not None:
                                                                                                                        Christian_Religious_Studies_Score = simpledialog.askinteger("Add Christian Religious Studies Score","Enter Christian Reigious Studies Score")
                                                                                                                        if Christian_Religious_Studies_Score is not None :
                                                                                                                            Islamic_Religious_Studies_Score = simpledialog.askinteger("Add Islamic Religious Studies Score","Enter Islamic Religious Studies Score")
                                                                                                                            if Islamic_Religious_Studies_Score is not None :
                                                                                                                                Music_Score = simpledialog.askinteger("Add Music Score","Enter Music Score")
                                                                                                                                if Music_Score is not None :
                                                                                                                                    Business_Management_Score = simpledialog.askinteger("Add Business Management Score","Enter Business MAnagement Score")
                                                                                                                                    if Business_Management_Score is not None:
                                                                                                                                        General_Knowledge_In_Art_Score = simpledialog.askinteger("Add General Knowledge In Art Score","Enter General Knowledge In Art Score")
                                                                                                                                        if General_Knowledge_In_Art_Score is not None:
                                                                                                                                            Elective_ICT_Score = simpledialog.askinteger("Add Elective ICT Score","Enter Elective ICT Score")
                                                                                                                                            if Elective_ICT_Score is not None :
                                                                                                                                                Accounting_Score = simpledialog.askinteger("Add Acccounting Score", "Enter Accounting Score")
                                                                                                                                                if Accounting_Score is not None :
                                                                                                                                                    Cost_Accounting_Score = simpledialog.askinteger("Add Cost Accounting Score","Enter Cost Accounting Score")
                                                                                                                                                    if Cost_Accounting_Score is not None :
                                                                                                                                                        Graphic_Design_Score = simpledialog.askinteger("Add Graphic Design Score","Enter Graphic Design Score")
                                                                                                                                                        if Graphic_Design_Score is not None :
                                                                                                                                                            Sculpture_Score = simpledialog.askinteger("Add Sculpture Score","Enter Sculpture Score")
                                                                                                                                                            if Sculpture_Score is not None :
                                                                                                                                                                Picture_Making_Score = simpledialog.askinteger("Add Picture Making Score","Enter Picture Making Score")
                                                                                                                                                                if Picture_Making_Score is not None:
                                                                                                                                                                    Leatherwork_Score = simpledialog.askinteger("Add Leatherwork Score","Enter Leatherwork Score")
                                                                                                                                                                    if Leatherwork_Score is not None :
                                                                                                                                                                        Textiles_Score = simpledialog.askinteger("Add Textiles Score","Enter Textiles Score")
                                                                                                                                                                        if Textiles_Score is not None :
                                                                                                                                                                            Basketry_Score = simpledialog.askinteger("Add Basketry Score","Enter Basketry Score")
                                                                                                                                                                            if Basketry_Score is not None :
                                                                                                                                                                                Ceramics_Score = simpledialog.askinteger("Add Ceramics Score","Enter Ceramics Score")
                                                                                                                                                                                if Ceramics_Score is not None :
                                                                                                                                                                                    Jewelry_Making_Score = simpledialog.askinteger("Add Jewelry Making Score", "Enter Jewelry Making Score")
                                                                                                                                                                                    if Jewelry_Making_Score is not None :
                                                                                                                                                                                        Food_and_Nutrition_Score = simpledialog.askinteger("Add Food and Nutrition Score", "Enter Food and Nutrition Score")
                                                                                                                                                                                        if Food_and_Nutrition_Score is not None :
                                                                                                                                                                                            Clothing_and_Textiles_Score = simpledialog.askinteger("Add Clothing and Textiles Score","Enter Clothing and Textiles Score")
                                                                                                                                                                                            if Clothing_and_Textiles_Score is not None :
                                                                                                                                                                                                Management_in_Living_Score = simpledialog.askinteger("Add Management in Living Score", "Enter Management in Living Score")
                                                                                                                                                                                                if Management_in_Living_Score is not None :
                                                                                                                                                                                                    Applied_Electricity_Score = simpledialog.askinteger("Add Applied Electricity Score","Enter Applied Electricity Score")
                                                                                                                                                                                                    if Applied_Electricity_Score is not None :
                                                                                                                                                                                                        Technical_Drawing_Score = simpledialog.askinteger("Add Technical Drawing Score","Enter Technical Drawing Score")
                                                                                                                                                                                                        if Technical_Drawing_Score is not None :
                                                                                                                                                                                                            Building_Construction_Score = simpledialog.askinteger("Add Building Construction Score","Enter Building Constructuion Score")
                                                                                                                                                                                                            if Building_Construction_Score is not None :
                                                                                                                                                                                                                Woodwork_Score = simpledialog.askinteger("Add woodwork Score","Enter woodwork score")
                                                                                                                                                                                                                if Woodwork_Score is not None :
                                                                                                                                                                                                                    Metalwork_Score = simpledialog.askinteger("Add Metalwork score","Enter metalwork Score")
                                                                                                                                                                                                                    if Metalwork_Score is not None:
                                                                                                                                                                                                                        AutoMechanics_Score = simpledialog.askinteger("Add AutoMechanics Score", "Enter AutoMechanics Score")
                                                                                                                                                                                                                        if AutoMechanics_Score is not None:
                                                                                                                                                                                                                            Electronics_Score = simpledialog.askinteger("Add Electronics Score","Enter Electronics Score")
                                                                                                                
                                                            
                                            
        # Create Scores dictionary
        scores = {
            " Mathematics " : Mathematics_Score,
            " English " : English_Language_Score,
            " Science " : Science_Score,
            " French " : French_Score,
            " ICT " : ICT_Score,
            " TWI " : Ghanaian_Language_TWI_Score,
            " GA " : Ghanaian_Language_GA_Score,
            " Creative_Arts " : Creative_Arts_Score,
            " Language_And_Literacy_Development " : Language_And_Literacy_Development_Score,
            " Numeracy " : Numeracy_Score,
            " Environmental_Studies ": Environmental_Studies_Score,
            " Religious and Moral Education " : RME_Score,
            " BDT " :Basic_Design_and_Technology_Score,
            " Social_Studies " : Social_Studies_Score,
            " Physical_Development " :  Physical_Development_Score,
            " Physical_Education ": Physical_Education_Score ,
            " Social_And_Emotional_Development ": Social_And_Emotional_Development ,
            " Our World Our People " : Our_World_Our_People_Score ,
            
            
        }
        
        #Add score to the list
        self.scores.append(scores)
        
        #save score records to file
        self.save_score_records()
        
        #show success message
        messagebox.showinfo("Success", f" Student scores added successfully ")
        
        pass

    
    #Code to Modify Studennt Academic Records
    def modify_academic_records(self):
        print("Hello Modify Academic Records")
    
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

    #Code to add a new teacher record
    def add_teacher(self):
        #Gather Teacher information
        teacher_id = str(uuid.uuid4())[:8] # Generate unique student ID
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
        # Check if the student records window is already open
        if hasattr(self, "teacher_records_window") and self.teacher_records_window.winfo_exists():
            # If it's open, bring it to focus and return
            self.teacher_records_window.lift()
            return  
        
           # Create a new window to display student records
        self.teacher_records_window = tk.Toplevel(self.master)
        self.teacher_records_window.title("Student Records")
        self.teacher_records_window.geometry("1000x800")  # Adjust the window size as needed

        # Create a frame to hold the student records
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

        # Create another frame inside the canvas to hold the student records
        teacher_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=teacher_frame, anchor=tk.NW)

        # Function to update the scroll region when the size of the student frame changes
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

        # Update the scroll region to fit the contents of the student frame
        teacher_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
    #Code to view General Records    
    def view_records(self):
        # Ensure self.students and self.teachers are lists and not empty
        if not isinstance(self.students, list):
            self.students = []
        if not isinstance(self.teachers, list):
            self.teachers = []

        # Check if the records window is already open
        if hasattr(self, "records_window") and self.records_window.winfo_exists():
            self.records_window.lift()
            return

        # Create a new window to display records
        self.records_window = tk.Toplevel(self.master)
        self.records_window.title("View General Records")
        self.records_window.geometry("1000x800")  # Adjusted size for better visibility

        # Create a canvas widget
        canvas = tk.Canvas(self.records_window)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        scrollbar = tk.Scrollbar(self.records_window, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold the records
        records_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=records_frame, anchor=tk.NW)

        # Function to update the scroll region when the size of the frame changes
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        records_frame.bind("<Configure>", on_frame_configure)

        # Add labels for students and teachers
        self.lbl_students = tk.Label(records_frame, text="Students", font=("Arial", 14, "bold"))
        self.lbl_students.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.lbl_teachers = tk.Label(records_frame, text="Teachers", font=("Arial", 14, "bold"))
        self.lbl_teachers.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Display student records
        row_num = 1
        if self.students:
            for student in self.students:
                student_frame = tk.Frame(records_frame, bd=2, relief=tk.GROOVE)
                student_frame.grid(row=row_num, column=0, pady=5, padx=5, sticky="ew")

                for key, value in student.items():
                    tk.Label(student_frame, text=f"{key}: {value}").pack(anchor="w")

                row_num += 1
        else:
            tk.Label(records_frame, text="No student records found.").grid(row=row_num, column=0, pady=10, padx=10, sticky="w")

        # Display teacher records
        row_num = 1
        if self.teachers:
            for teacher in self.teachers:
                teacher_frame = tk.Frame(records_frame, bd=2, relief=tk.GROOVE)
                teacher_frame.grid(row=row_num, column=1, pady=5, padx=5, sticky="ew")

                for key, value in teacher.items():
                    tk.Label(teacher_frame, text=f"{key}: {value}").pack(anchor="w")

                row_num += 1
        else:
            tk.Label(records_frame, text="No teacher records found.").grid(row=row_num, column=1, pady=10, padx=10, sticky="w")

        # Update the Canvas scroll region to fit the entire frame
        records_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

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

def main():
    app = SchoolManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()
