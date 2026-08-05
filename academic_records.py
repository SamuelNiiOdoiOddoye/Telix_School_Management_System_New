# Import statements
import json
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog  # Importing simpledialog separately
from PIL import Image, ImageTk
import os
import ctypes # To set the taskbar icon on windows
import uuid # Importing the uuid module for generating unique student Ids

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
            " Career_Technology " : Career_Technology_Score,
            " Government " : Government_Score, 
            " Economics " : Economics_Score,
            " Elective_Mathematics " : Elective_Mathematics_Score,
            " Geography " : Geography_Score,
            " Elective_Physics " : Elective_Physics_Score,
            " Elective_Chemistry " : Elective_Chemistry_Score,
            " Elective_Biology " : Elective_Biology_Score,
            " Literature_in_English " : Literature_in_English_Score,
            " History " : History_Score,
            " Christian_Religious_Studies " : Christian_Religious_Studies_Score,
            " Islamic_Religious_Studies " : Islamic_Religious_Studies_Score,
            " Music " : Music_Score,
            " Business_Management " : Business_Management_Score,
            " General_Knowledge_In_Art " : General_Knowledge_In_Art_Score,
            " Elective_ICT " : Elective_ICT_Score,
            " Accounting " : Accounting_Score,
            " Cost_Accounting " : Cost_Accounting_Score,
            " Graphic_Design " : Graphic_Design_Score,
            " Sculpture " : Sculpture_Score,
            " Picture_Making " : Picture_Making_Score,
            " Leatherwork " : Leatherwork_Score,
            " Textiles " : Textiles_Score,
            " Basketry " : Basketry_Score,
            " Ceramics " : Ceramics_Score,
            " Jewelry_Making " : Jewelry_Making_Score,
            " Food_and_Nutrition " : Food_and_Nutrition_Score,
            " Clothing_and_Textiles " : Clothing_and_Textiles_Score,
            " Management_in_Living " : Management_in_Living_Score,
            " Applied_Electricity " : Applied_Electricity_Score,
            " Technical_Drawing " : Technical_Drawing_Score,
            " Building_Construction " : Building_Construction_Score,
            " Woodwork " : Woodwork_Score,
            " Metalwork " : Metalwork_Score,
            " AutoMechanics " : AutoMechanics_Score,
            " Electronics " : Electronics_Score
            
            
            
            
        }
        
        #Add score to the list
        self.scores.append(scores)
        
        #save score records to file
        self.save_score_records()
        
        #show success message
        messagebox.showinfo("Success", f" Student scores added successfully ")
        
        pass

#Code to Modify Student Academic Records
def modify_academic_records(self):
        print("Hello Modify Academic Records")
    
#code to view student academic records
def view_academic_records(self):
    # Check if the student academic records window is already open
            if hasattr(self, "academic_records_window") and self.academic_records_window.winfo_exists():
                # If it's open, bring it to focus and return
                self.academic_records_window.lift()
                return
            
            # Message to display if there's no student record
            if not self.students:
                messagebox.showinfo("No Records " , "No Academic Records found")
                return
            
            # Create a new window to display student records
            self.academic_records_window = tk.Toplevel(self.master)
            self.academic_records_window.title("Academic Records")
            self.academic_records_window.geometry("1000x800")  # Adjust the window size as needed
    
            # Create a frame to hold the student records
            records_frame = tk.Frame(self.academic_records_window)
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
            academic_frame = tk.Frame(canvas)
            canvas.create_window((0, 0), window=academic_frame, anchor=tk.NW)
    
            # Function to update the scroll region when the size of the student frame changes
            def on_frame_configure(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
    
            academic_frame.bind("<Configure>", on_frame_configure)
            
            # Initialize counters
            index = 0 # controls grid row position
            student_num = 1 # controls student numbering
    
            # Iterate over the academic records list and display their information
            for student in self.students:
                # Create a label for each student with an orderly number 
                student_label = tk.Label(academic_frame, text=f"Student {student_num}:", font=("Arial", 12, "bold"))
                student_label.grid(row=index, column=0, sticky="w")
                index += 1 # Increment index for each new student
                student_num += 1 # Increement student number for the next student
    
                # Display student information in the next rows
                for key,value in student.items():
                    info_label = tk.Label(academic_frame, text=f"{key}: {value}" , wraplength=600 , justify="left")
                    info_label.grid(row=index, column=1, sticky="w")
                    index += 1 # Move to the next row for each key-value pair
    
                # Update the scroll region to fit the contents of the student frame
                academic_frame.update_idletasks()
                canvas.config(scrollregion=canvas.bbox("all"))
    
#code for academic_records_widgets
def academic_records_widgets(self):
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
        