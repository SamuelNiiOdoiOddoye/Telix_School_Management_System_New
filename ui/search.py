
#create widgets for the search module
def search_widgets(self):
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
