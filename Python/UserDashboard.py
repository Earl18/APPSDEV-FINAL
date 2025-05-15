import hashlib
import os
import re
import shutil
import json
from typing import Optional
import tkinter as tk
from tkcalendar import Calendar
from datetime import datetime, date
import customtkinter as ctk
from PIL import Image
from tkinter import messagebox, filedialog

def create_account():
    bannerImg.pack_forget()
    loginMainFrame.pack_forget()
    signupMainFrame.pack(expand=True)

def email_exists(email):
    for directory in [user_dir, admin_dir]:
        for file in os.listdir(directory):
            if file.lower() == f"{email}.json":
                return True

    for folder in os.listdir(doctor_dir):
        folder_path = os.path.join(doctor_dir, folder)
        if os.path.isdir(folder_path):
            profile_path = os.path.join(folder_path, 'profile.json')
            if os.path.exists(profile_path):
                try:
                    with open(profile_path, 'r') as f:
                        data = json.load(f)
                        if data.get("Email", "").lower() == email:
                            return True
                except json.JSONDecodeError:
                    continue
    return False

def signup_account():
    name = nameEntry.get()
    email = emailEntry.get().lower()
    contact = contactEntry.get()
    password = passwordEntry.get()
    role = roleVar.get()

    if not all([name, email, contact, password, role]):
        messagebox.showerror("Input Error", "All fields are required.")
        return

    if not is_valid_email(email):
        messagebox.showerror("Invalid Email", "Please enter a valid email address.")
        return

    if not is_strong_password(password):
        messagebox.showerror(
            "Weak Password","Password must include at least one uppercase letter, one number, and one special character.")
        return

    if email_exists(email):
        messagebox.showwarning("Duplicate", "This email is already registered, Please use another one.")
        return

    if role == "User":
        filepath = os.path.join(user_dir, f"{email}.json")
    elif role == "Admin":
        filepath = os.path.join(admin_dir, f"{email}.json")
    elif role == "Doctor":
        folder = os.path.join(doctor_dir, email)
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, 'profile.json')
    else:
        messagebox.showerror("Role Error", "Unknown account type.")
        return

    account_data = {
        "Full Name": name,
        "Email": email,
        "Contact": contact,
        "Password": hash_password(password),
        "Account Type": role
    }

    with open(filepath, 'w') as file:
        json.dump(account_data, file, indent=4)

    for entry in [nameEntry, emailEntry, contactEntry, passwordEntry]:
        entry.delete(0, 'end')
    roleVar.set("User")

    print(f"{role} account successfully saved.")
    messagebox.showinfo("Registration Successful", "Account created successfully. Please log in.")

    signupMainFrame.pack_forget()
    loginMainFrame.pack(expand=True)

def is_strong_password(password):
    return (
        any(c.isupper() for c in password) and
        any(c.isdigit() for c in password) and
        any(c in "!@#$%^&*()-_=+[]{};:,<.>/?\\" for c in password)
    )

def is_valid_email(email):
    return "@" in email and "." in email

def validate_contact(p):
    return (p.isdigit() and len(p) <= 11) or p == ""

def signup_entry(row, label_text, var_name):
    ctk.CTkLabel(
        signupFrame, text=label_text, font=('Bahnschrift', 14, 'bold'),
        text_color=color2, fg_color='white'
    ).grid(row=row, column=0, sticky='w', padx=40)

    entry = ctk.CTkEntry(
        signupFrame, font=('Bahnschrift', 13), border_width=2,
        width=300, fg_color='white', text_color='black'
    )

    if "contact" in var_name.lower():
        vcmd = signupFrame.register(validate_contact)
        entry.configure(validate="key", validatecommand=(vcmd, '%P'))

    entry.grid(row=row + 1, column=0, sticky='w', padx=40, pady=(0, 10))
    return entry

def login_button_press(event):
    loginButtonHeader.configure(fg_color=color2, text_color='white',hover_color=color2)

def login_button_release(event):
    loginButtonHeader.configure(fg_color='white', text_color=color2,hover_color='white')

def login_account():
    bannerImg.pack_forget()
    signupMainFrame.pack_forget()
    loginMainFrame.pack(expand=True)
    #userMainFrame.pack(fill='both', expand=True)
    #adminLabel.pack(side='left', padx=(10, 0), pady=10)
    #adminMainFrame.pack(fill='both', expand=True)
    #doctorLabel.pack(side='left', padx=(10, 0), pady=10)
    #doctorMainFrame.pack(fill='both', expand=True)

def verify_login():
    email = emailLogin.get().lower()
    password = passwordLogin.get()

    if not all([email, password]):
        messagebox.showerror("Input Error", "Both fields are required.")
        return

    for role, directory in [("User", user_dir), ("Admin", admin_dir), ("Doctor", doctor_dir)]:
        filepath = os.path.join(directory, f"{email}.json") if role != "Doctor" else os.path.join(directory, email, 'profile.json')
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                data = json.load(file)
            if check_password(data["Password"], password):
                messagebox.showinfo("Login Successful", f"Welcome back, {data['Full Name']}!")

                current_user["email"] = email
                current_user["role"] = role
                if role == "Doctor":
                    current_user["name"] = data.get("Full Name")
                loginMainFrame.pack_forget()
                createButton.pack_forget()
                loginButtonHeader.pack_forget()

                if role == "User":
                    userMainFrame.pack(fill='both', expand=True)
                    load_user_appointments()
                    load_user_bookings()
                elif role == "Admin":
                    adminLabel.pack(side='left', padx=(10, 0), pady=10)
                    adminMainFrame.pack(fill='both', expand=True)
                    load_admin_appointments()
                    load_admin_bookings()
                elif role == "Doctor":
                    doctorLabel.pack(side='left', padx=(10, 0), pady=10)
                    doctorMainFrame.pack(fill='both', expand=True)
                    load_doctor_appointments()
                    load_doctor_dashboard()


                logoutButton.pack(side="right")
                emailLogin.delete(0, 'end')
                passwordLogin.delete(0, 'end')
                return
            else:
                messagebox.showerror("Login Failed", "Incorrect password.")
                return

    if messagebox.askyesno("Account Not Found", "Email not found. Would you like to register?"):
        loginFrame.pack_forget()
        create_account()

def show_dashboard(event):
    userAppointmentFrame.pack_forget()
    userMakeAppointmentFrame.pack_forget()
    adminAppointmentFrame.pack_forget()
    adminAddDoctorFrame.pack_forget()
    adminDoctorListFrame.pack_forget()
    doctorAppointmentFrame.pack_forget()
    userDashboardFrame.pack(side='left', fill='both', expand=True)
    adminDashboardFrame.pack(side='left', fill='both', expand=True)
    doctorDashboardFrame.pack(side='left', fill='both', expand=True)


def show_appointment(event):
    userDashboardFrame.pack_forget()
    userMakeAppointmentFrame.pack_forget()
    adminDashboardFrame.pack_forget()
    adminAddDoctorFrame.pack_forget()
    adminDoctorListFrame.pack_forget()
    doctorDashboardFrame.pack_forget()
    userAppointmentFrame.pack(side='left', fill='both', expand=True)
    adminAppointmentFrame.pack(side='left', fill='both', expand=True)
    doctorAppointmentFrame.pack(side='left', fill='both', expand=True)

def show_make_appointment(event):
    userDashboardFrame.pack_forget()
    userAppointmentFrame.pack_forget()
    adminDashboardFrame.pack_forget()
    adminAppointmentFrame.pack_forget()
    adminDoctorListFrame.pack_forget()
    userMakeAppointmentFrame.pack(side='left', fill='both', expand=True)
    adminAddDoctorFrame.pack(side='left', fill='both', expand=True)

def show_doctors_list(event):
    adminDashboardFrame.pack_forget()
    adminAddDoctorFrame.pack_forget()
    adminAppointmentFrame.pack_forget()
    adminDoctorListFrame.pack(side='left', fill='both', expand=True)


def show_frame(name):
    for frame in doctor_frames.values():
        frame.pack_forget()
    doctor_frames[name].pack(side='top', anchor='w', padx=20, pady=20)

def select_image():
    global uploaded_image_path, current_image

    file_path = filedialog.askopenfilename(filetypes=[("Image Files", ("*.png", "*.jpg", "*.jpeg"))])
    if not file_path:
        return

    email = entries["Email"].get().strip().lower()
    if not email:
        messagebox.showerror("Missing Email", "Enter doctor's email first.")
        return

    try:
        img = Image.open(file_path).resize((230, 300))
        new_ctk_image = ctk.CTkImage(dark_image=img, light_image=img, size=(230, 300))

        image_label.configure(image=new_ctk_image, text="")
        image_label.image = new_ctk_image
        current_image = new_ctk_image

        uploaded_image_path = file_path

    except Exception as e:
        uploaded_image_path = None
        image_label.configure(image=None, text="Click to upload image")
        image_label.image = None
        messagebox.showerror("Image Error", f"Failed to load image:\n{e}")



def save_doctor():
    global uploaded_image_path, current_image

    name = entries["Full Name"].get().strip()
    email = entries["Email"].get().strip().lower()
    password = entries["Password"].get().strip()
    experience = entries["Experience"].get().strip()
    fee = entries["Fee"].get().strip()
    specialty = entries["Specialty"].get().strip()
    address = entries["Address"].get().strip()
    about = about_textbox.get("1.0", "end").strip()

    if specialty == "Select specialty":
        specialty = ""

    if not all([name, email, password, experience, fee, specialty, address, about]):
        messagebox.showerror("Input Error", "All fields are required.")
        return

    if not is_valid_email(email):
        messagebox.showerror("Invalid Email", "Enter a valid email.")
        return

    if not is_strong_password(password):
        messagebox.showerror(
            "Weak Password", "Password must include at least one uppercase letter, one number, and one special character."
        )
        return

    for existing_folder in os.listdir(doctor_dir):
        existing_path = os.path.join(doctor_dir, existing_folder, 'profile.json')
        if os.path.exists(existing_path):
            with open(existing_path, 'r') as file:
                existing_data = json.load(file)
                if existing_data.get("Full Name") == name or existing_data.get("Email") == email:
                    messagebox.showwarning("Duplicate", "This name or email is already registered.")
                    return

    doctor_folder = os.path.join(doctor_dir, email)
    os.makedirs(doctor_folder, exist_ok=True)
    profile_path = os.path.join(doctor_folder, 'profile.json')

    image_name = ""
    if uploaded_image_path:
        image_name = os.path.basename(uploaded_image_path)

    doctor_data = {
        "Full Name": name,
        "Email": email,
        "Password": hash_password(password),
        "Experience": experience,
        "Fee": fee,
        "Specialty": specialty,
        "Address": address,
        "About": about,
        "Availability": "Available",
        "Image": image_name
    }

    with open(profile_path, 'w') as file:
        json.dump(doctor_data, file, indent=4)

    if uploaded_image_path:
        try:
            doctor_image_path = os.path.join(doctor_folder, image_name)
            shutil.copy(uploaded_image_path, doctor_image_path)
            messagebox.showinfo("Success", "Doctor added successfully with image.")
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to save the image: {e}")

    for key, entry in entries.items():
        if key == "Specialty":
            entry.set("Select specialty")
        else:
            entry.delete(0, 'end')

    about_textbox.delete("1.0", "end")
    image_label.configure(image=default_ctk_image, text="Click to upload image")
    image_label.image = default_ctk_image
    uploaded_image_path = None
    current_image = None

def compute_doctor_hash():
    doctor_folders = sorted([f for f in os.listdir(doctor_dir) if os.path.isdir(os.path.join(doctor_dir, f))])
    return hashlib.md5("".join(doctor_folders).encode()).hexdigest(), doctor_folders


def load_doctors(scrollable,force_refresh=False):
    global last_doctor_hash

    current_hash, doctor_folders = compute_doctor_hash()

    if not force_refresh and current_hash == last_doctor_hash:
        scrollable.after(1000, lambda: load_doctors(scrollable))
        return

    last_doctor_hash = current_hash

    existing_cards = scrollable.winfo_children()

    for widget in existing_cards:
        widget.destroy()

    if not doctor_folders:
        ctk.CTkLabel(scrollable, text="No doctors found.", font=('Bahnschrift', 16, 'italic')).pack(pady=20)
        return

    window_width = scrollable.winfo_screenwidth()
    max_columns = max(1, window_width // 350)

    for i, folder in enumerate(doctor_folders):
        folder_path = os.path.join(doctor_dir, folder)
        profile_path = os.path.join(folder_path, 'profile.json')

        if not os.path.exists(profile_path):
            continue

        with open(profile_path, 'r') as file:
            profile = json.load(file)

        doctor_name = profile.get("Full Name", "Unknown")
        doctor_specialty = profile.get("Specialty", "Not Specified")
        availability = profile.get("Availability", "Unknown")

        img_path = next((os.path.join(folder_path, f) for f in os.listdir(folder_path)
                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))), None)

        try:
            img = Image.open(img_path).resize((230, 220)) if img_path else Image.new('RGB', (230, 220), color='gray')
        except:
            img = Image.new('RGB', (230, 220), color='gray')

        photo = ctk.CTkImage(light_image=img, size=(230, 220))

        card = ctk.CTkFrame(scrollable, width=300, height=330, fg_color='#f6f6f6', corner_radius=12)
        card.pack_propagate(False)
        card.grid(row=i // max_columns, column=i % max_columns, padx=10, pady=10, sticky='nsew')

        ctk.CTkLabel(card, image=photo, text="").pack(pady=(10, 5))
        text_wrapper = ctk.CTkFrame(card, fg_color=color2, corner_radius=8)
        text_wrapper.pack(fill='both', expand=True)

        ctk.CTkLabel(text_wrapper, text=doctor_name, font=('Bahnschrift', 18, 'bold'),
                     text_color='white', anchor='w', wraplength=200).pack(fill='x', padx=13, pady=(5, 0))
        ctk.CTkLabel(text_wrapper, text=doctor_specialty, font=('Bahnschrift', 13),
                     text_color='white', anchor='w', wraplength=140).pack(fill='x', padx=13)
        ctk.CTkLabel(text_wrapper, text=f"Status: {availability}", font=('Bahnschrift', 14),
                     text_color="#4CAF50" if availability.lower() == "available" else "white",
                     anchor='w', wraplength=140).pack(fill='x', padx=13)

        var = ctk.BooleanVar()
        check = ctk.CTkCheckBox(card, text="", variable=var)
        check.place(relx=0.88, rely=0.02)
        checkboxes.append((check, folder))

    for col in range(max_columns):
        scrollable.grid_columnconfigure(col, weight=1)

    scrollable.after(5000, lambda: load_doctors(scrollable))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(stored_hash, entered_password):
    return stored_hash == hash_password(entered_password)

def is_numeric(value):
    return value.isdigit() or value == ""

def logout_account():
    current_user["email"] = None
    current_user["role"] = None

    userMainFrame.pack_forget()
    adminMainFrame.pack_forget()
    doctorMainFrame.pack_forget()
    adminLabel.pack_forget()
    doctorLabel.pack_forget()

    loginMainFrame.pack(expand=True)
    createButton.pack(side="right", padx=(15,0))
    loginButtonHeader.pack(side="right")
    logoutButton.pack_forget()

    messagebox.showinfo("Logged Out", "You have been successfully logged out.")

class TimeButton(ctk.CTkButton):
    def __init__(self, master, time_text, *args, **kwargs):
        super().__init__(
            master, text=time_text, *args,
            width=85, height=35,
            font=('Bahnschrift', 13),
            border_width=5, border_color=background,
            hover_color="#E0E0E0", fg_color="#F8F8F8", corner_radius=10,
            text_color="black", **kwargs
        )
        self.selected = False
        self.default_colors = {"fg": "white", "text": color2}
        self.selected_colors = {"fg": color2, "text": "white"}
        self.configure(command=self.toggle)

    def toggle(self):
        self.selected = not self.selected
        colors = self.selected_colors if self.selected else self.default_colors
        self.configure(fg_color=colors["fg"], text_color=colors["text"])

def create_booking_frame(parent, profile, image):
    frame = ctk.CTkScrollableFrame(parent, fg_color=color2)

    topContentFrame = ctk.CTkFrame(frame, fg_color='transparent')
    topContentFrame.pack(fill='x', pady=10)

    doctor_img = ctk.CTkLabel(topContentFrame, width=230, height=300,
                              image=ctk.CTkImage(light_image=image, size=(230, 300)),
                              text="", corner_radius=10, fg_color='white')
    doctor_img.pack(side='left', padx=20)

    doctorDetails = ctk.CTkFrame(topContentFrame, fg_color='white', corner_radius=10)
    doctorDetails.pack(side='left', fill='both', expand=True, padx=10, pady=(50, 0))

    nameFrame = ctk.CTkFrame(doctorDetails, fg_color='white')
    nameFrame.pack(anchor='w', padx=10, pady=(25, 0), fill='x')

    ctk.CTkLabel(nameFrame, text=profile.get("Full Name", "N/A"),
                 font=('Bahnschrift', 28, 'bold'), text_color='black').pack(side='left')

    specialtyFrame = ctk.CTkFrame(doctorDetails, fg_color='white')
    specialtyFrame.pack(anchor='w', padx=10, pady=(0, 10), fill='x')

    ctk.CTkLabel(specialtyFrame, text=profile.get("Specialty", "Not Specified"),
                 font=('Bahnschrift', 18), text_color='gray').pack(side='left')

    aboutFrame = ctk.CTkFrame(doctorDetails, fg_color='white')
    aboutFrame.pack(anchor='w', padx=10, pady=(0, 20), fill='both')

    ctk.CTkLabel(aboutFrame, text="About", font=('Bahnschrift', 18, 'bold'), text_color='black').pack(anchor='w',
                                                                                                      pady=(10, 5))

    about_text = profile.get("About", "No description available.")

    ctk.CTkLabel(
        aboutFrame,
        text=about_text,
        font=('Bahnschrift', 14),
        text_color='gray',
        wraplength=500,
        justify='left'
    ).pack(anchor='w')

    exp_raw = profile.get("Experience", "4")
    exp_match = re.search(r'\d+', str(exp_raw))
    exp = f"{exp_match.group()} Years" if exp_match else "N/A"
    expTag = ctk.CTkFrame(specialtyFrame, fg_color=color2, corner_radius=10)
    expTag.pack(side='left', padx=10)
    ctk.CTkLabel(expTag, text=exp, font=('Bahnschrift', 14), text_color='white').pack(padx=6, pady=2)

    feeRow = ctk.CTkFrame(doctorDetails, fg_color='white')
    feeRow.pack(anchor='w', padx=10, pady=(10, 10), fill='x')
    ctk.CTkLabel(feeRow, text='Appointment Fee:', font=('Bahnschrift', 18, 'bold'), text_color='black').pack(
        side='left')
    fee_value = profile.get("Fee", "0")
    if not str(fee_value).strip().startswith("₱"):
        fee_value = f"₱{fee_value}"
    ctk.CTkLabel(feeRow, text=fee_value, font=('Bahnschrift', 18), text_color='black').pack(side='left', padx=10)

    datetimeFrame = ctk.CTkFrame(frame, fg_color='white', corner_radius=10)
    datetimeFrame.pack(fill='x', pady=20, padx=(300, 10))

    calendarFrame = ctk.CTkFrame(datetimeFrame, fg_color='white', corner_radius=15)
    calendarFrame.pack(side='left', padx=10, pady=10, fill='both', expand=True)

    ctk.CTkLabel(calendarFrame, text="Select Date", font=('Bahnschrift', 18, 'bold'), text_color='black').pack(pady=(10, 5))

    calendar_container = tk.Frame(calendarFrame, bg=color2, bd=2, relief='solid', highlightbackground='gray', highlightthickness=1, padx=5, pady=5)
    calendar_container.pack(padx=10, pady=5)

    calendar_widget = Calendar(calendar_container, selectmode='day', date_pattern='yyyy-mm-dd', font=('Bahnschrift', 12),
                               borderwidth=1, selectbackground=color2, selectforeground='white',
                               normalbackground='#ffffff', normalforeground='black',
                               background='white', foreground=color2, showweeknumbers=False)
    calendar_widget.pack()

    timeBoxFrame = ctk.CTkFrame(datetimeFrame, fg_color='white')
    timeBoxFrame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

    gridFrame = ctk.CTkFrame(timeBoxFrame, fg_color='white', corner_radius=10)
    gridFrame.pack(padx=10, pady=10)

    ctk.CTkLabel(gridFrame, text="Select Time", font=('Bahnschrift', 18, 'bold'), text_color='black').grid(row=0, column=0, columnspan=4, sticky='w', pady=(0, 10))

    time_buttons = []

    def refresh_time_buttons(selected_date):
        nonlocal time_buttons
        for child in gridFrame.winfo_children():
            if isinstance(child, TimeButton):
                child.destroy()
        time_buttons.clear()

        booked = get_booked_times(profile.get("Full Name", "Unknown"), selected_date)

        selected_is_today = selected_date == date.today().strftime('%Y-%m-%d')
        current_hour = datetime.now().hour
        current_minute = datetime.now().minute

        for i, hour in enumerate(range(8, 23)):
            label = f"{hour % 12 or 12}:00 {'AM' if hour < 12 else 'PM'}"
            btn = TimeButton(gridFrame, time_text=label)

            if label in booked:
                btn.configure(state="disabled")
            elif selected_is_today:
                if hour < current_hour or (hour == current_hour and 0 < current_minute):
                    btn.configure(state="disabled")

            btn.grid(row=1 + i // 4, column=i % 4, padx=5, pady=5)
            time_buttons.append(btn)

    def on_date_change(event=None):
        selected_date = calendar_widget.get_date()
        today_str = date.today().strftime('%Y-%m-%d')
        if selected_date < today_str:
            messagebox.showwarning("Invalid Date", "You cannot select a past date.")
            calendar_widget.selection_set(today_str)
            return
        refresh_time_buttons(selected_date)

    calendar_widget.bind("<<CalendarSelected>>", on_date_change)
    on_date_change()

    # Booking logic...
    def book_appointment():
        selected_date = calendar_widget.get_date()
        selected_times = [btn.cget("text") for btn in time_buttons if btn.selected]

        if not selected_times:
            messagebox.showerror("No Time", "Please select a time slot.")
            return

        existing_files = [f for f in os.listdir(appointment_dir) if f.startswith("appointment") and f.endswith(".json")]
        existing_numbers = []

        for f in existing_files:
            match = re.search(r'appointment(\d+)\.json', f)
            if match:
                existing_numbers.append(int(match.group(1)))

        next_number = max(existing_numbers, default=0) + 1
        filename = f"appointment{next_number}.json"
        file_path = os.path.join(appointment_dir, filename)

        doctor_fee = profile.get('Fee', 'Not Available')

        appointment_data = {
            "doctor": profile.get("Full Name", "Unknown"),
            "user": current_user["email"],
            "date": selected_date,
            "time": selected_times,
            "fee": doctor_fee,
            "status": "Ongoing"
        }

        with open(file_path, 'w') as f:
            json.dump(appointment_data, f, indent=4)

        messagebox.showinfo("Appointment Booked", "Your appointment has been successfully booked.")
        load_user_appointments()
        load_user_bookings()
        load_admin_bookings()
        load_admin_appointments()

        userMakeAppointmentLabelFrame.pack(side='top', fill='x', padx=20, pady=(25, 0))
        show_frame("General Physician")

        frame.pack_forget()

    def cancel_booking():
        userMakeAppointmentLabelFrame.pack(side='top', fill='x', padx=20, pady=(25, 0))
        show_frame("General Physician")
        frame.pack_forget()

    buttonFrame = ctk.CTkFrame(frame, fg_color='transparent')
    buttonFrame.pack(pady=15)

    ctk.CTkButton(buttonFrame, text="Book Appointment", fg_color='white', hover_color='#E0E0E0',
                  text_color=color2, width=420, height=50, font=('Bahnschrift', 18, 'bold'),
                  command=book_appointment).pack(side='left', padx=10)

    ctk.CTkButton(buttonFrame, text="Cancel", fg_color='white', hover_color='#E0E0E0',
                  text_color=color2, width=420, height=50, font=('Bahnschrift', 18, 'bold'),
                  command=cancel_booking).pack(side='left', padx=10)

    return frame

def open_doctor_booking(profile, image):
    for f in doctor_frames.values():
        f.pack_forget()
    for widget in userMakeAppointmentFrame.winfo_children():
        if widget not in doctor_frames.values() and widget != userMakeAppointmentLabelFrame:
            widget.destroy()
    userMakeAppointmentLabelFrame.pack_forget()
    booking_frame = create_booking_frame(userMakeAppointmentFrame, profile, image)
    booking_frame.pack(fill='both', expand=True,padx=20,pady=20)

def load_doctors_to_categories():
    for frame in doctor_frames.values():
        for widget in frame.winfo_children()[1:]:
            widget.destroy()

    _, doctor_folders = compute_doctor_hash()

    for folder in doctor_folders:
        folder_path = os.path.join(doctor_dir, folder)
        profile_path = os.path.join(folder_path, 'profile.json')
        if not os.path.exists(profile_path):
            continue

        with open(profile_path, 'r') as file:
            profile = json.load(file)

        name = profile.get("Full Name", "Unknown")
        specialty = profile.get("Specialty", "General Physician")
        availability = profile.get("Availability", "Unknown")
        about = profile.get("About", "No description provided.")
        fee = profile.get("Fee", "P1000")

        if availability.lower() == "unavailable":
            continue

        img_path = next((os.path.join(folder_path, f) for f in os.listdir(folder_path)
                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))), None)
        if img_path:
            try:
                img = Image.open(img_path).resize((230, 220))
            except:
                img = Image.new('RGB', (230, 220), color='gray')
        else:
            img = Image.new('RGB', (230, 220), color='gray')

        photo = ctk.CTkImage(light_image=img, size=(230, 220))

        frame = doctor_frames.get(specialty)
        if not frame:
            continue

        doctor_wrapper = ctk.CTkFrame(
            frame,
            width=300,
            height=330,
            corner_radius=12,
            fg_color="#f6f6f6"
        )
        doctor_wrapper.pack(side='left', anchor='n', padx=10, pady=10)
        doctor_wrapper.pack_propagate(False)

        def on_click(event, p=profile, i=img):
            open_doctor_booking(p, i)

        doctor_wrapper.bind("<Button-1>", on_click)

        img_label = ctk.CTkLabel(doctor_wrapper, image=photo, text="")
        img_label.pack(pady=(10, 5))
        img_label.bind("<Button-1>", on_click)

        text_wrapper = ctk.CTkFrame(doctor_wrapper, fg_color=color2, corner_radius=8)
        text_wrapper.pack(fill='both', expand=True)
        text_wrapper.bind("<Button-1>", on_click)

        for text, font, color in [
            (name, ('Bahnschrift', 18, 'bold'), 'white'),
            (specialty, ('Bahnschrift', 13), 'white'),
            (f"Status: {availability}", ('Bahnschrift', 14),
             "#4CAF50" if availability.lower() == "available" else "white")
        ]:
            lbl = ctk.CTkLabel(text_wrapper, text=text, font=font, text_color=color, anchor='w', wraplength=200)
            lbl.pack(fill='x', padx=13, pady=(5 if font[1] == 18 else 0, 0))
            lbl.bind("<Button-1>", on_click)

def get_booked_times(doctor_name, date_str):
    booked_times = []
    for file in os.listdir(appointment_dir):
        if file.endswith(".json"):
            with open(os.path.join(appointment_dir, file), 'r') as f:
                data = json.load(f)
            if (data.get("doctor") == doctor_name and
                data.get("date") == date_str and
                data.get("status") != "Cancelled"):
                booked_times.extend(data.get("time", []))
    return booked_times

def get_status(date_str, time_list):
    try:
        appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        current_date = datetime.now().date()

        if appointment_date < current_date:
            return "Completed"
        elif appointment_date == current_date:
            now = datetime.now()
            all_past = True

            for t in time_list:
                time_obj = datetime.strptime(t, "%I:%M %p").time()
                appointment_datetime = datetime.combine(appointment_date, time_obj)
                if appointment_datetime > now:
                    all_past = False
                    break

            if all_past:
                return "Completed"
            else:
                return "Ongoing"
        else:
            return "Ongoing"
    except:
        return "Ongoing"

def load_user_bookings():
    for widget in bookingsFrame.winfo_children():
        if widget != bookingHeader:
            widget.destroy()

    completed_count = 0
    cancelled_count = 0
    ongoing_count = 0

    for file in os.listdir(appointment_dir):
        if file.endswith(".json"):
            file_path = os.path.join(appointment_dir, file)
            with open(file_path, 'r') as f:
                data = json.load(f)

            if data.get("user") == current_user["email"]:
                doctor = data.get("doctor", "Unknown")
                date_str = data.get("date", "")
                times = data.get("time", [])
                status = get_status(date_str, times)

                if status == "Completed" and data.get("status") != "Completed":
                    data["status"] = "Completed"
                    with open(file_path, 'w') as f:
                        json.dump(data, f, indent=4)

                if data.get("status") == "Completed":
                    completed_count += 1
                    continue
                elif data.get("status") == "Cancelled":
                    cancelled_count += 1
                    continue
                else:
                    ongoing_count += 1

                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%A %d %B %Y")
                except:
                    formatted_date = date_str

                timeslots = ", ".join(times)
                date_time_text = f"Booking on {formatted_date} at {timeslots}"

                status_text = data.get("status", "Ongoing")
                status_color = {
                    'Completed': 'green',
                    'Ongoing': 'orange',
                    'Cancelled': 'red'
                }.get(status_text, 'gray')

                card = ctk.CTkFrame(bookingsFrame, fg_color="#f5f5f5", corner_radius=10)
                card.pack(fill='x', padx=15, pady=10)

                row_frame = ctk.CTkFrame(card, fg_color="transparent")
                row_frame.pack(fill='x', padx=15, pady=10)

                ctk.CTkLabel(
                    row_frame,
                    text=f"{doctor}",
                    font=('Bahnschrift', 17),
                    text_color='black',
                    anchor='w'
                ).pack(side='left', padx=5)

                ctk.CTkLabel(
                    row_frame,
                    text=date_time_text,
                    font=('Bahnschrift', 17),
                    text_color='black',
                    anchor='center',
                    wraplength=450
                ).pack(side='left', expand=True)

                status_label = ctk.CTkLabel(
                    row_frame,
                    text=status_text,
                    font=('Bahnschrift', 17),
                    text_color=status_color,
                    anchor='e'
                )
                status_label.pack(side='right', padx=5)

                if status_text == "Ongoing":
                    def cancel_appointment(file_path=file_path, label=status_label):
                        try:
                            with open(file_path, 'r') as f:
                                data = json.load(f)
                            data["status"] = "Cancelled"
                            with open(file_path, 'w') as f:
                                json.dump(data, f, indent=4)

                            label.configure(text="Cancelled", text_color="red")
                            load_user_bookings()
                            load_user_appointments()
                            load_admin_bookings()
                            load_admin_appointments()
                            load_doctor_appointments()
                            load_doctor_dashboard()
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to cancel appointment:\n{e}")

                    cancel_btn = ctk.CTkButton(
                        row_frame,
                        text="Cancel",
                        font=('Bahnschrift', 14),
                        text_color='white',
                        fg_color='red',
                        hover_color='#cc0000',
                        width=80,
                        command=cancel_appointment
                    )
                    cancel_btn.pack(side='right', padx=5)

    completed_label.configure(text=f"Completed: {completed_count}")
    cancelled_label.configure(text=f"Cancelled: {cancelled_count}")
    ongoing_label.configure(text=f"Ongoing: {ongoing_count}")

    completed_label.configure(text=f"Completed: {completed_count}")
    cancelled_label.configure(text=f"Cancelled: {cancelled_count}")
    ongoing_label.configure(text=f"Ongoing: {ongoing_count}")


def load_user_appointments():
    for widget in historyContent.winfo_children():
        widget.destroy()

    if not os.path.exists(appointment_dir):
        messagebox.showerror("Error", "Appointment directory not found.")
        return

    appointment_files = [f for f in os.listdir(appointment_dir) if f.endswith('.json')]
    user_appointments = []

    for file_name in appointment_files:
        file_path = os.path.join(appointment_dir, file_name)

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            if isinstance(data, list):
                for appointment in data:
                    if appointment.get('user') == current_user["email"]:
                        user_appointments.append(appointment)

            elif isinstance(data, dict):
                if data.get('user') == current_user["email"]:
                    user_appointments.append(data)

        except Exception as e:
            print(f"Failed to read {file_name}: {e}")
            continue

    for i, appointment_data in enumerate(user_appointments):
        doctor_name = appointment_data.get('doctor', 'Unknown Doctor')
        date = appointment_data.get('date', 'Unknown Date')
        time_slots = appointment_data.get('time', [])
        lines = []

        for j in range(0, len(time_slots), 2):
            line = ", ".join(time_slots[j:j + 2])
            lines.append(line)

        while len(lines) < 2:
            lines.append("")

        times = f"{date}\n" + "\n".join(lines)
        status = appointment_data.get('status', "Ongoing")

        doctor_fee = appointment_data.get('fee', "₱0")
        doctor_fee = f"₱{doctor_fee}"

        row = i + 1

        ctk.CTkLabel(historyContent, text=str(i + 1), font=('Bahnschrift', 14), text_color='black', fg_color='white').grid(row=row, column=0, sticky='w', padx=10, pady=5)
        ctk.CTkLabel(historyContent, text=times, font=('Bahnschrift', 14), text_color='black', fg_color='white', anchor='w', justify='left').grid(row=row, column=1, sticky='w', padx=10, pady=5)
        ctk.CTkLabel(historyContent, text=doctor_name, font=('Bahnschrift', 14), text_color='black', fg_color='white').grid(row=row, column=2, sticky='w', padx=10, pady=5)
        ctk.CTkLabel(historyContent, text=doctor_fee, font=('Bahnschrift', 14), text_color='black', fg_color='white').grid(row=row, column=3, sticky='w', padx=10, pady=5)

        status_color = {
            'Completed': 'green',
            'Ongoing': 'orange',
            'Cancelled': 'red'
        }.get(status, 'gray')

        ctk.CTkLabel(historyContent, text=status, font=('Bahnschrift', 14), text_color=status_color, fg_color='white').grid(row=row, column=4, sticky='w', padx=10, pady=5)

def load_admin_appointments():
    for widget in adminHistoryContent.winfo_children():
        widget.destroy()

    if not os.path.exists(appointment_dir):
        messagebox.showerror("Error", "Appointment directory not found.")
        return

    appointment_files = [f for f in os.listdir(appointment_dir) if f.endswith('.json')]
    all_appointments = []

    for file_name in appointment_files:
        file_path = os.path.join(appointment_dir, file_name)

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            if isinstance(data, list):
                all_appointments.extend(data)
            elif isinstance(data, dict):
                all_appointments.append(data)

        except Exception as e:
            print(f"Failed to read {file_name}: {e}")
            continue

    for i, appointment_data in enumerate(all_appointments):
        user_email = appointment_data.get('user', 'Unknown')
        doctor_name = appointment_data.get('doctor', 'Unknown Doctor')
        date = appointment_data.get('date', 'Unknown Date')
        time_slots = appointment_data.get('time', [])
        doctor_fee = appointment_data.get('fee', "₱0")
        status = appointment_data.get('status', "Ongoing")

        lines = []
        for j in range(0, len(time_slots), 2):
            line = ", ".join(time_slots[j:j + 2])
            lines.append(line)

        while len(lines) < 2:
            lines.append("")

        times = f"{date}\n" + "\n".join(lines)

        doctor_fee = f"₱{doctor_fee}"

        row = i + 1

        ctk.CTkLabel(adminHistoryContent, text=str(i + 1), font=('Bahnschrift', 14), text_color='black', fg_color='white').grid(row=row, column=0, sticky='w', padx=10, pady=5)
        ctk.CTkLabel(adminHistoryContent, text=user_email, font=('Bahnschrift', 14), text_color='black', fg_color='white', anchor='w').grid(row=row, column=1, sticky='w', padx=10, pady=5)
        ctk.CTkLabel(adminHistoryContent, text=times, font=('Bahnschrift', 14), text_color='black', fg_color='white', anchor='w', justify='left').grid(row=row, column=2, sticky='w', padx=10, pady=5)
        ctk.CTkLabel(adminHistoryContent, text=doctor_name, font=('Bahnschrift', 14), text_color='black', fg_color='white').grid(row=row, column=3, sticky='w', padx=10, pady=5)
        ctk.CTkLabel(adminHistoryContent, text=doctor_fee, font=('Bahnschrift', 14), text_color='black', fg_color='white').grid(row=row, column=4, sticky='w', padx=10, pady=5)

        status_color = {
            'Completed': 'green',
            'Ongoing': 'orange',
            'Cancelled': 'red'
        }.get(status, 'gray')

        ctk.CTkLabel(adminHistoryContent, text=status, font=('Bahnschrift', 14), text_color=status_color, fg_color='white').grid(row=row, column=5, sticky='w', padx=10, pady=5)

def load_admin_bookings():
    for widget in adminBookingsFrame.winfo_children():
        if widget != adminBookingHeader:
            widget.destroy()

    doctor_count = len([f for f in os.listdir(doctor_dir) if os.path.isdir(os.path.join(doctor_dir, f))])
    patient_count = len([f for f in os.listdir(user_dir) if f.endswith(".json")])
    ongoing_count = 0

    for file in os.listdir(appointment_dir):
        if file.endswith(".json"):
            file_path = os.path.join(appointment_dir, file)
            with open(os.path.join(appointment_dir, file), 'r') as f:
                data = json.load(f)

            status = get_status(data.get("date", ""), data.get("time", []))

            if status == "Completed" and data.get("status") != "Completed":
                data["status"] = "Completed"
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)

            if data.get("status") in ["Cancelled", "Completed"]:
                continue

            ongoing_count += 1

            doctor = data.get("doctor", "Unknown")
            user = data.get("user", "Unknown")
            date_str = data.get("date", "")
            times = ", ".join(data.get("time", []))

            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%A %d %B %Y")
            except:
                formatted_date = date_str

            status_text = data.get("status", "Ongoing")
            status_color = {
                'Completed': 'green',
                'Ongoing': 'orange',
                'Cancelled': 'red'
            }.get(status_text, 'gray')

            card = ctk.CTkFrame(adminBookingsFrame, fg_color="#f5f5f5", corner_radius=10)
            card.pack(fill='x', padx=15, pady=10)

            row_frame = ctk.CTkFrame(card, fg_color="transparent")
            row_frame.pack(fill='x', padx=15, pady=10)

            ctk.CTkLabel(
                row_frame,
                text=f"{doctor}",
                font=('Bahnschrift', 17),
                text_color='black'
            ).pack(side='left', padx=5)

            ctk.CTkLabel(
                row_frame,
                text=f"{user} — {formatted_date} at {times}",
                font=('Bahnschrift', 17),
                text_color='black',
                wraplength=450
            ).pack(side='left', expand=True)

            status_label = ctk.CTkLabel(
                row_frame,
                text=status_text,
                font=('Bahnschrift', 17),
                text_color=status_color
            )
            status_label.pack(side='right', padx=5)

            def cancel_appointment(fp=file_path, label=status_label):
                try:
                    with open(fp, 'r') as f:
                        data = json.load(f)
                    data["status"] = "Cancelled"
                    with open(fp, 'w') as f:
                        json.dump(data, f, indent=4)

                    label.configure(text="Cancelled", text_color="red")
                    load_admin_bookings()
                    load_admin_appointments()
                    load_user_appointments()
                    load_user_bookings()
                    load_doctor_appointments()
                    load_doctor_dashboard()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to cancel:\n{e}")

            cancel_btn = ctk.CTkButton(
                row_frame,
                text="Cancel",
                font=('Bahnschrift', 14),
                text_color='white',
                fg_color='red',
                hover_color='#cc0000',
                width=80,
                command=cancel_appointment
            )
            cancel_btn.pack(side='right', padx=5)

            def complete_appointment(fp=file_path, label=status_label):
                try:
                    with open(fp, 'r') as f:
                        data = json.load(f)
                    data["status"] = "Completed"
                    with open(fp, 'w') as f:
                        json.dump(data, f, indent=4)

                    label.configure(text="Completed", text_color="green")
                    load_admin_bookings()
                    load_admin_appointments()
                    load_user_appointments()
                    load_user_bookings()
                    load_doctor_appointments()
                    load_doctor_dashboard()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to complete:\n{e}")

            complete_btn = ctk.CTkButton(
                row_frame,
                text="Complete",
                font=('Bahnschrift', 14),
                text_color='white',
                fg_color='green',
                hover_color='#009933',
                width=90,
                command=complete_appointment
            )
            complete_btn.pack(side='right', padx=5)

    doctor_count_label.configure(text=f"Doctors: {doctor_count}")
    patient_count_label.configure(text=f"Patients: {patient_count}")
    admin_ongoing_label.configure(text=f"Appointments: {ongoing_count}")

def load_doctor_appointments():
    for widget in doctorHistoryContent.winfo_children():
        widget.destroy()

    if not os.path.exists(appointment_dir):
        messagebox.showerror("Error", "Appointment directory not found.")
        return

    appointment_files = [f for f in os.listdir(appointment_dir) if f.endswith('.json')]
    doctor_appointments = []

    for file_name in appointment_files:
        file_path = os.path.join(appointment_dir, file_name)

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            if isinstance(data, list):
                for appointment in data:
                    if appointment.get('doctor') == current_user["name"]:
                        doctor_appointments.append(appointment)

            elif isinstance(data, dict):
                if data.get('doctor') == current_user["name"]:
                    doctor_appointments.append(data)

        except Exception as e:
            print(f"Failed to read {file_name}: {e}")
            continue

    for i, appointment_data in enumerate(doctor_appointments):
        patient_email = appointment_data.get('user', 'Unknown')
        date = appointment_data.get('date', 'Unknown Date')
        time_slots = appointment_data.get('time', [])
        status = appointment_data.get('status', 'Ongoing')
        doctor_fee = appointment_data.get('fee', "₱0")
        doctor_fee = f"₱{doctor_fee}"

        lines = []
        for j in range(0, len(time_slots), 2):
            lines.append(", ".join(time_slots[j:j + 2]))
        while len(lines) < 2:
            lines.append("")
        times = f"{date}\n" + "\n".join(lines)

        status_color = {
            'Completed': 'green',
            'Ongoing': 'orange',
            'Cancelled': 'red'
        }.get(status, 'gray')

        row = i + 1

        ctk.CTkLabel(doctorHistoryContent, text=str(row), font=('Bahnschrift', 14), text_color='black', fg_color='white').grid(row=row, column=0, sticky='w', padx=10, pady=5)
        ctk.CTkLabel(doctorHistoryContent, text=patient_email, font=('Bahnschrift', 14), text_color='black', fg_color='white').grid(row=row, column=1, sticky='w', padx=10, pady=5)
        ctk.CTkLabel(doctorHistoryContent, text=times, font=('Bahnschrift', 14), text_color='black', fg_color='white', justify='left').grid(row=row, column=2, sticky='w', padx=10, pady=5)
        ctk.CTkLabel(doctorHistoryContent, text=doctor_fee, font=('Bahnschrift', 14), text_color='black', fg_color='white').grid(row=row, column=3, sticky='w', padx=10, pady=5)
        ctk.CTkLabel(doctorHistoryContent, text=status, font=('Bahnschrift', 14), text_color=status_color, fg_color='white').grid(row=row, column=4, sticky='w', padx=10, pady=5)

def load_doctor_dashboard():
    for widget in doctorBookingsFrame.winfo_children():
        if widget != doctorBookingHeader:
            widget.destroy()

    doctor_name = current_user.get("name")
    income_total = 0
    ongoing_count = 0
    unique_patients = set()

    for file in os.listdir(appointment_dir):
        if file.endswith(".json"):
            file_path = os.path.join(appointment_dir, file)
            with open(file_path, 'r') as f:
                data = json.load(f)

            if data.get("doctor") != doctor_name:
                continue

            status = get_status(data.get("date", ""), data.get("time", []))

            if status == "Completed" and data.get("status") != "Completed":
                data["status"] = "Completed"
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)

            if data.get("status") == "Completed":
                try:
                    income_total += int(data.get("fee", "0"))
                except ValueError:
                    pass
                unique_patients.add(data.get("user", "Unknown"))
                continue

            if data.get("status") == "Cancelled":
                continue

            ongoing_count += 1
            unique_patients.add(data.get("user", "Unknown"))

            doctor = data.get("doctor", "Unknown")
            user = data.get("user", "Unknown")
            date_str = data.get("date", "")
            times = ", ".join(data.get("time", []))

            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%A %d %B %Y")
            except:
                formatted_date = date_str

            status_text = data.get("status", "Ongoing")
            status_color = {
                'Completed': 'green',
                'Ongoing': 'orange',
                'Cancelled': 'red'
            }.get(status_text, 'gray')

            card = ctk.CTkFrame(doctorBookingsFrame, fg_color="#f5f5f5", corner_radius=10)
            card.pack(fill='x', padx=15, pady=10)

            row_frame = ctk.CTkFrame(card, fg_color="transparent")
            row_frame.pack(fill='x', padx=15, pady=10)

            ctk.CTkLabel(
                row_frame,
                text=f"{user}",
                font=('Bahnschrift', 17),
                text_color='black'
            ).pack(side='left', padx=5)

            ctk.CTkLabel(
                row_frame,
                text=f"{formatted_date} at {times}",
                font=('Bahnschrift', 17),
                text_color='black',
                wraplength=450
            ).pack(side='left', expand=True)

            status_label = ctk.CTkLabel(
                row_frame,
                text=status_text,
                font=('Bahnschrift', 17),
                text_color=status_color
            )
            status_label.pack(side='right', padx=5)

            def complete_appointment(fp=file_path, label=status_label):
                try:
                    with open(fp, 'r') as f:
                        data = json.load(f)
                    data["status"] = "Completed"
                    with open(fp, 'w') as f:
                        json.dump(data, f, indent=4)

                    label.configure(text="Completed", text_color="green")
                    load_doctor_dashboard()
                    load_doctor_appointments()
                    load_admin_bookings()
                    load_admin_appointments()
                    load_user_appointments()
                    load_user_bookings()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to complete:\n{e}")

            complete_btn = ctk.CTkButton(
                row_frame,
                text="Complete",
                font=('Bahnschrift', 14),
                text_color='white',
                fg_color='green',
                hover_color='#009933',
                width=90,
                command=complete_appointment
            )
            complete_btn.pack(side='right', padx=5)

    doctor_income_label.configure(text=f"Income: ₱{income_total}")
    doctor_patient_label.configure(text=f"Patients: {len(unique_patients)}")
    doctor_appointments_label.configure(text=f"Appointments: {ongoing_count}")

def update_doctor_status(new_status):
    selected = [folder for check, folder in checkboxes if check.get()]
    if not selected:
        messagebox.showwarning("No Selection", "Please select at least one doctor to update.")
        return

    for folder in selected:
        profile_path = os.path.join(doctor_dir, folder, 'profile.json')
        if os.path.exists(profile_path):
            with open(profile_path, 'r+') as file:
                data = json.load(file)
                data['Availability'] = new_status
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()

    load_doctors(adminDoctorFrame, force_refresh=True)

def remove_selected_doctor():
    selected = [folder for check, folder in checkboxes if check.get()]
    if not selected:
        messagebox.showwarning("No Selection", "Please select at least one doctor to remove.")
        return

    blocked_doctors = []

    for folder in selected:
        folder_path = os.path.join(doctor_dir, folder)
        profile_path = os.path.join(folder_path, 'profile.json')

        if not os.path.exists(profile_path):
            continue

        try:
            with open(profile_path, 'r') as file:
                profile = json.load(file)
                doctor_full_name = profile.get("Full Name")
        except:
            continue

        if not doctor_full_name:
            continue

        has_ongoing = False
        for filename in os.listdir(appointment_dir):
            file_path = os.path.join(appointment_dir, filename)
            if filename.endswith('.json') and os.path.isfile(file_path):
                try:
                    with open(file_path, 'r') as appt_file:
                        appt = json.load(appt_file)
                        if appt.get("doctor") == doctor_full_name and appt.get("status") == "Ongoing":
                            has_ongoing = True
                            break
                except:
                    continue

        if has_ongoing:
            if doctor_full_name not in blocked_doctors:
                blocked_doctors.append(doctor_full_name)
            continue

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to remove {doctor_full_name}?")
        if confirm:
            import shutil
            shutil.rmtree(folder_path)

    if blocked_doctors:
        unique_names = sorted(set(blocked_doctors))
        names = "\n- ".join(unique_names)
        messagebox.showwarning(
            "Cannot Remove Doctors",
            f"The following doctors have ongoing appointments and cannot be removed:\n\n- {names}"
        )

    load_doctors(adminDoctorFrame, force_refresh=True)

#Main Window
window = ctk.CTk()
width = window.winfo_screenwidth()
height = window.winfo_screenheight()
color2 = '#08395f'
background = '#e1f3fc'
window.attributes('-fullscreen',True)
window.state('zoomed')
window.bind("<Escape>", lambda e: window.attributes("-fullscreen", False))
window.bind("<F12>", lambda e: window.attributes("-fullscreen", True))
window.configure(fg_color=background)
window.tk.call("tk", "scaling", 1.0)
window.minsize(1400,950)
last_doctor_hash = None
selected_doctor_var = ctk.StringVar(value="")
checkboxes = []
blank_pil_image = Image.new("RGB", (230, 300), color="#E0E0E0")
default_ctk_image = ctk.CTkImage(dark_image=blank_pil_image, light_image=blank_pil_image, size=(230, 300))
current_user: dict[str, Optional[str]] = {
    "email": None,
    "role": None,
    "name": None
}

#Data
base_dir = 'Data'
user_dir = os.path.join(base_dir, 'Users')
doctor_dir = os.path.join(base_dir, 'Doctors')
admin_dir = os.path.join(base_dir, 'Admins')
appointment_dir = os.path.join(base_dir, 'Appointments')
for path in [user_dir, doctor_dir, admin_dir, appointment_dir]:
    os.makedirs(path, exist_ok=True)

#Images
img1 = Image.open('Images/Logo.png')
logo = ctk.CTkImage(img1, size=img1.size)
img2 = Image.open('Images/Banner.png')
banner = ctk.CTkImage(img2, size=img2.size)
img3 = Image.open('Images/home.png')
home = ctk.CTkImage(img3, size=img3.size)
img4 = Image.open('Images/calendar.png')
calendar = ctk.CTkImage(img4, size=img4.size)
img5 = Image.open('Images/user-add.png')
add_doctor = ctk.CTkImage(img5, size=img5.size)
img6 = Image.open('Images/users.png')
users = ctk.CTkImage(img6, size=img6.size)
img7 = Image.open('Images/square-plus.png')
add = ctk.CTkImage(img7, size=img7.size)
img8 = Image.open('Images/check.png')
completed = ctk.CTkImage(img8, size=img8.size)
img9 = Image.open('Images/cancel.png')
cancelled = ctk.CTkImage(img9, size=img9.size)
img10 = Image.open('Images/add.png')
pending = ctk.CTkImage(img10, size=img10.size)
img11 = Image.open('Images/latest.png')
booking = ctk.CTkImage(img11, size=img11.size)
img12 = Image.open('Images/doctor.png')
doctor = ctk.CTkImage(img12, size=img12.size)
img13 = Image.open('Images/admin appointment.png')
adminAppointment = ctk.CTkImage(img13, size=img13.size)
img14 = Image.open('Images/medical.png')
adminPatients = ctk.CTkImage(img14, size=img14.size)
img15 = Image.open('Images/admin calendar.png')
adminCalendar = ctk.CTkImage(img15, size=img15.size)
img16 = Image.open('Images/navigation doctor.png')
navigationDoctor = ctk.CTkImage(img16, size=img16.size)
img17 = Image.open('Images/Income.png')
income = ctk.CTkImage(img17, size=img17.size)
img18 = Image.open('Images/first-aid-kit.png')
img19 = Image.open('Images/checklist.png')
verify = ctk.CTkImage(img19, size=img19.size)
img20 = Image.open('Images/close.png')
xmark = ctk.CTkImage(img20, size=img20.size)
dashDoctor = ctk.CTkImage(img18, size=img18.size)
signup = ctk.CTkImage(light_image=Image.open("Images/createAccount.png"), size=(400, 550))


#Header
header = ctk.CTkFrame(window,fg_color='white',height=100,width=width,corner_radius=0)
header.pack(side='top')
header.pack_propagate(False)
ctk.CTkLabel(header,image=logo,text='',bg_color='white').pack(side='left',padx=(50,0))
adminLabel = ctk.CTkLabel(header, text='Admin', text_color='white',fg_color=color2, font=('Bahnschrift', 18, 'bold'),width=80,pady=10, corner_radius=5)
doctorLabel = ctk.CTkLabel(header, text='Doctor', text_color='white',fg_color=color2, font=('Bahnschrift', 18, 'bold'),width=80,pady=10, corner_radius=5)

#Home
bannerImg = ctk.CTkLabel(window,text='', image=banner,bg_color=background)
bannerImg.pack(pady='65')
closeButton = ctk.CTkButton(
    header,
    text='',
    image=xmark,
    width=60,
    height=60,
    fg_color='white',
    corner_radius=10,
    hover_color='#cc0000',
    command=window.destroy
)
closeButton.pack(side='right', padx=(15,30))

createButton = ctk.CTkButton(
    header,
    text='Create Account',
    fg_color=color2,
    text_color='white',
    corner_radius=10,
    width=150,
    height=60,
    font=('Bahnschrift', 17, 'bold'),
    command=create_account
)
createButton.pack(side="right",padx=(15,0))

loginButtonHeader = ctk.CTkButton(
    header,
    text='Login Account',
    fg_color='white',
    text_color=color2,
    corner_radius=10,
    width=150,
    height=60,
    hover_color='white',
    font=('Bahnschrift', 17, 'bold'),
    command=login_account
)
loginButtonHeader.pack(side="right")
loginButtonHeader.bind("<ButtonPress-1>", login_button_press)
loginButtonHeader.bind("<ButtonRelease-1>", login_button_release)

logoutButton = ctk.CTkButton(
    header,
    text='Logout Account',
    fg_color=color2,
    text_color='white',
    corner_radius=10,
    width=150,
    height=60,
    font=('Bahnschrift', 17, 'bold'),
    command=logout_account
)

#Signup
signupMainFrame = ctk.CTkFrame(window, fg_color='transparent')
signupFrame = ctk.CTkFrame(signupMainFrame, height=550, width=470, fg_color='white', corner_radius=20)
signupFrame.pack(side='left', padx=(0, 20), pady=40)
signupFrame.pack_propagate(False)
signupImgFrame = ctk.CTkFrame(signupMainFrame, fg_color='black', width=400, height=520, corner_radius=20)
signupImgFrame.pack(side='left', padx=(20, 0), pady=40)
signupImgFrame.pack_propagate(False)
ctk.CTkLabel(signupImgFrame, text='', image=signup).pack(expand=True)
ctk.CTkLabel(signupFrame, text='Create Account', font=('Bahnschrift', 30, 'bold'), text_color=color2, fg_color='white').grid(row=0, column=0, sticky='w', padx=40, pady=(20, 10))
ctk.CTkLabel(signupFrame, text='Please sign up to book appointment', font=('Bahnschrift', 14), text_color=color2, fg_color='white').grid(row=1, column=0, sticky='w', padx=40, pady=(0, 15))
nameEntry = signup_entry(2, "Full Name", "name")
emailEntry = signup_entry(4, "Email", "email")
contactEntry = signup_entry(6, "Contact #", "contact")
passwordEntry = signup_entry(8, "Password", "password")
roleVar = ctk.StringVar(value="User")
ctk.CTkLabel(signupFrame, text="Account Type", font=('Bahnschrift', 14, 'bold'), text_color=color2, fg_color='white')\
    .grid(row=10, column=0, sticky='w', padx=40)
roleMenu = ctk.CTkOptionMenu(
    signupFrame,
    values=["User", "Admin"],
    variable=roleVar,
    fg_color=color2,
    button_color=color2,
    button_hover_color=color2,
    text_color='white',
    width=300
)
roleMenu.grid(row=11, column=0, sticky='w', padx=40, pady=(0, 10))

signupButton = ctk.CTkButton(
    signupFrame,
    text='Create Account',
    fg_color=color2,
    hover_color=color2,
    text_color='white',
    width=300,
    height=40,
    font=('Bahnschrift', 16, 'bold'),
    command=signup_account
)
signupButton.grid(row=12, column=0, sticky='w', padx=40, pady=(0, 10))

ctk.CTkLabel(signupFrame, text='Already have an account?', font=('Bahnschrift', 14), text_color=color2, fg_color='white').grid(row=13, column=0, sticky='w', padx=40,pady=(0,20))
loginButton = ctk.CTkButton(
    signupFrame,
    text='Login Here',
    fg_color='white',
    text_color=color2,
    hover_color='#f0f0f0',
    border_width=1,
    font=('Bahnschrift', 14),
    command=login_account,
    width=100,
    height=30
)
loginButton.grid(row=13, column=0, sticky='e',padx=(0,50),pady=(0,20))

#Login
loginMainFrame = ctk.CTkFrame(window, fg_color='transparent')
loginFrame = ctk.CTkFrame(loginMainFrame, height=390, width=380, fg_color='white', corner_radius=20)
loginFrame.pack(side='left', padx=(0, 20), pady=40)
loginFrame.grid_propagate(False)
loginImgFrame = ctk.CTkFrame(loginMainFrame, fg_color='black', width=400, height=520, corner_radius=20)
loginImgFrame.pack(side='left', padx=(20, 0), pady=40)
loginImgFrame.pack_propagate(False)
ctk.CTkLabel(loginImgFrame, text='', image=signup).pack(expand=True)
ctk.CTkLabel(loginFrame, text='Login', font=('Bahnschrift', 30, 'bold'), text_color=color2, fg_color='white').grid(row=0, column=0, sticky='w', padx=40, pady=(20, 10))
ctk.CTkLabel(loginFrame, text='Please log in to book appointment', font=('Bahnschrift', 14), text_color=color2, fg_color='white').grid(row=1, column=0, sticky='w', padx=40, pady=(0, 15))
ctk.CTkLabel(loginFrame, text='Email', font=('Bahnschrift', 14,'bold'), text_color=color2, fg_color='white').grid(row=2, column=0, sticky='w', padx=40)
emailLogin = ctk.CTkEntry(loginFrame, font=('Bahnschrift', 13), border_width=2, width=300, fg_color='white',text_color='black')
emailLogin.grid(row=3, column=0, sticky='w', padx=40, pady=(0, 15))
ctk.CTkLabel(loginFrame, text='Password', font=('Bahnschrift', 14,'bold'), text_color=color2, fg_color='white').grid(row=4, column=0, sticky='w', padx=40)
passwordLogin = ctk.CTkEntry(loginFrame, font=('Bahnschrift', 13), border_width=2, width=300, fg_color='white', show='*',text_color='black')
passwordLogin.grid(row=5, column=0, sticky='w', padx=40, pady=(0, 20))
LoginButton = ctk.CTkButton(
    loginFrame,
    text='Login',
    fg_color=color2,
    hover_color=color2,
    text_color='white',
    width=300,
    height=40,
    font=('Bahnschrift', 16, 'bold'),
    command=verify_login
)
LoginButton.grid(row=6, column=0, sticky='w', padx=40, pady=(0, 15))

ctk.CTkLabel(loginFrame, text='Create a new account?', font=('Bahnschrift', 14), text_color=color2, fg_color='white').grid(row=7, column=0, sticky='w', padx=40)
signupButton2 = ctk.CTkButton(
    loginFrame,
    text='Click Here',
    fg_color='white',
    text_color=color2,
    hover_color='#f0f0f0',
    border_width=1,
    font=('Bahnschrift', 14),
    command=create_account,
    width=100,
    height=30
)
signupButton2.grid(row=7, column=0, sticky='e', padx=40)

#User Navigation
userMainFrame = ctk.CTkFrame(window, fg_color=background)
userFrame = ctk.CTkFrame(userMainFrame,height=height,width=300,fg_color=color2,corner_radius=0)
userFrame.pack(side='left', fill='y')
userFrame.pack_propagate(False)
userDashboardButton = ctk.CTkButton(
    userFrame,
    image=home,
    text='Dashboard',
    font=('Bahnschrift', 20, 'bold'),
    compound='left',
    anchor='w',
    fg_color='white',
    text_color='black',
    corner_radius=5,
    hover_color="#e0e0e0",
    command=lambda: show_dashboard(None)
)
userDashboardButton.pack(side='top', fill='x', pady=(40, 15), padx=10)

userAppointmentButton = ctk.CTkButton(
    userFrame,
    image=calendar,
    text='Appointments',
    font=('Bahnschrift', 20, 'bold'),
    compound='left',
    anchor='w',
    fg_color='white',
    text_color='black',
    corner_radius=5,
    hover_color="#e0e0e0",
    command=lambda: show_appointment(None)
)
userAppointmentButton.pack(side='top', fill='x', pady=(0, 15), padx=10)

userMakeAppointmentButton = ctk.CTkButton(
    userFrame,
    image=add,
    text='Make an appointment',
    font=('Bahnschrift', 20, 'bold'),
    compound='left',
    anchor='w',
    fg_color='white',
    text_color='black',
    corner_radius=5,
    hover_color="#e0e0e0",
    command=lambda: show_make_appointment(None)
)
userMakeAppointmentButton.pack(side='top', fill='x', pady=(0, 15), padx=10)


#User Dashboard
userDashboardFrame = ctk.CTkFrame(userMainFrame, fg_color=background)
userDashboardFrame.pack(side='left', fill='both', expand=True)
statusFrame = ctk.CTkFrame(userDashboardFrame, fg_color=background)
statusFrame.pack(side='top', fill='x', padx=20, pady=25)
statusFrame.grid_columnconfigure((0, 1, 2), weight=1)
completed_label = ctk.CTkLabel(statusFrame, image=completed, text='Completed: 0', font=('Bahnschrift', 16),
                               compound='left', padx=15, pady=10, fg_color='white',
                               text_color='black', corner_radius=10)
completed_label.grid(row=0, column=0, padx=20, pady=5, sticky='ew')

cancelled_label = ctk.CTkLabel(statusFrame, image=cancelled, text='Cancelled: 0', font=('Bahnschrift', 16),
                               compound='left', padx=15, pady=10, fg_color='white',
                               text_color='black', corner_radius=10)
cancelled_label.grid(row=0, column=1, padx=20, pady=5, sticky='ew')

ongoing_label = ctk.CTkLabel(statusFrame, image=pending, text='Ongoing: 0', font=('Bahnschrift', 16),
                             compound='left', padx=15, pady=10, fg_color='white',
                             text_color='black', corner_radius=10)
ongoing_label.grid(row=0, column=2, padx=20, pady=5, sticky='ew')
bookingMainFrame = ctk.CTkFrame(userDashboardFrame, fg_color='white',corner_radius=7)
bookingMainFrame.pack(side='top', fill='both', expand=True, padx=20, pady=20)
bookingMainFrame.pack_propagate(True)
bookingHeader = ctk.CTkFrame(bookingMainFrame, height=100, fg_color=color2)
bookingHeader.pack(side='top', fill='x')
bookingHeader.pack_propagate(False)
ctk.CTkLabel(bookingHeader,image=booking,text='Latest Bookings',fg_color=color2,text_color='white',font=('Bahnschrift',19,'bold'),compound='left',padx=10).pack(side='left',padx=45)
bookingsFrame = ctk.CTkScrollableFrame(bookingMainFrame, fg_color='white',corner_radius=7)
bookingsFrame.pack(side='top', fill='both', expand=True, padx=20, pady=20)
bookingsFrame.pack_propagate(True)

#User Appointment
userAppointmentFrame = ctk.CTkFrame(userMainFrame,height=height,width=width,fg_color=background)
userAppointmentLabelFrame = ctk.CTkFrame(userAppointmentFrame, fg_color=background)
userAppointmentLabelFrame.pack(side='top', fill='x', padx=20, pady=(25, 0))
ctk.CTkLabel(userAppointmentLabelFrame, text='All Appointments', font=('Bahnschrift', 20, 'bold'), pady=10, fg_color=background,text_color='black').pack(side='left')
historyFrame = ctk.CTkFrame(userAppointmentFrame, fg_color='white',corner_radius=7)
historyFrame.pack(side='top', fill='both', expand=True, padx=20, pady=(0, 20))
historyFrame.pack_propagate(True)
historyHeader = ctk.CTkFrame(historyFrame, height=40, fg_color=color2)
historyHeader.pack(side='top', fill='x')
historyHeader.pack_propagate(False)
historyHeader.grid_columnconfigure(0, weight=1)
historyHeader.grid_columnconfigure(1, weight=2)
historyHeader.grid_columnconfigure(2, weight=3)
historyHeader.grid_columnconfigure(3, weight=2)
historyHeader.grid_columnconfigure(4, weight=2)
ctk.CTkLabel(historyHeader, text='#', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=0, sticky='w', padx=10)
ctk.CTkLabel(historyHeader, text='Date & Time', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=1, sticky='w', padx=(10,35))
ctk.CTkLabel(historyHeader, text='Doctor', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=2, sticky='w', padx=10)
ctk.CTkLabel(historyHeader, text='Fees', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=3, sticky='w', padx=(37,10))
ctk.CTkLabel(historyHeader, text='Status', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=4, sticky='w', padx=(10,15))
historyContent = ctk.CTkScrollableFrame(historyFrame, fg_color='white')
historyContent.pack(fill='both', expand=True)
historyContent.grid_columnconfigure(0, weight=1)
historyContent.grid_columnconfigure(1, weight=2)
historyContent.grid_columnconfigure(2, weight=3)
historyContent.grid_columnconfigure(3, weight=2)
historyContent.grid_columnconfigure(4, weight=2)

#User Make an Appointment
userMakeAppointmentFrame = ctk.CTkFrame(userMainFrame,height=height,width=width,fg_color=background)
userMakeAppointmentLabelFrame = ctk.CTkFrame(userMakeAppointmentFrame, fg_color=background)
userMakeAppointmentLabelFrame.pack(side='top', fill='x', padx=20, pady=(25, 0))
doctor_labels = [
    "General Physician",
    "Gynecologist",
    "Dermatologist",
    "Pediatrician",
    "Neurologist",
    "Dentist"
]
doctor_frames = {}
for i, label in enumerate(doctor_labels):
    userMakeAppointmentLabelFrame.grid_columnconfigure(i, weight=1)
    btn = ctk.CTkButton(
        userMakeAppointmentLabelFrame,
        text=label,
        font=('Bahnschrift', 18, 'bold'),
        fg_color='white',
        text_color=color2,
        hover_color="#e0e0e0",
        command=lambda l=label: show_frame(l)
    )
    btn.grid(row=0, column=i, padx=5, pady=5, sticky='ew')
specialties = {
    "General Physician": "General Physicians",
    "Gynecologist": "Gynecologists",
    "Dermatologist": "Dermatologists",
    "Pediatrician": "Pediatricians",
    "Neurologist": "Neurologists",
    "Dentist": "Dentist"
}

for key, label_text in specialties.items():
    frame = ctk.CTkFrame(userMakeAppointmentFrame, fg_color='white', height=height, width=width)
    frame.pack_propagate(False)
    header = ctk.CTkFrame(frame, height=50, fg_color=color2)
    header.pack(side='top', fill='x')
    header.pack_propagate(False)
    ctk.CTkLabel(
        header,
        text=label_text,
        font=('Bahnschrift', 20, 'bold'),
        pady=10,
        fg_color='transparent',
        text_color='white'
    ).pack(side='left', padx=50)
    doctor_frames[key] = frame
load_doctors_to_categories()
show_frame("General Physician")

#Admin Navigation
adminMainFrame = ctk.CTkFrame(window, fg_color=background)
adminFrame = ctk.CTkFrame(adminMainFrame,height=height,width=300,fg_color=color2,corner_radius=0)
adminFrame.pack(side='left', fill='y')
adminFrame.pack_propagate(False)
adminDashboardButton = ctk.CTkButton(
    adminFrame,
    image=home,
    text='Dashboard',
    font=('Bahnschrift', 20, 'bold'),
    compound='left',
    anchor='w',
    fg_color='white',
    text_color='black',
    corner_radius=5,
    hover_color="#e0e0e0",
    command=lambda: show_dashboard(None)
)
adminDashboardButton.pack(side='top', fill='x', pady=(40, 15), padx=10)

adminAppointmentButton = ctk.CTkButton(
    adminFrame,
    image=calendar,
    text='Appointments',
    font=('Bahnschrift', 20, 'bold'),
    compound='left',
    anchor='w',
    fg_color='white',
    text_color='black',
    corner_radius=5,
    hover_color="#e0e0e0",
    command=lambda: show_appointment(None)
)
adminAppointmentButton.pack(side='top', fill='x', pady=(0, 15), padx=10)

adminMakeAppointmentButton = ctk.CTkButton(
    adminFrame,
    image=add,
    text='Add Doctor',
    font=('Bahnschrift', 20, 'bold'),
    compound='left',
    anchor='w',
    fg_color='white',
    text_color='black',
    corner_radius=5,
    hover_color="#e0e0e0",
    command=lambda: show_make_appointment(None)
)
adminMakeAppointmentButton.pack(side='top', fill='x', pady=(0, 15), padx=10)

adminMakeAppointmentButton = ctk.CTkButton(
    adminFrame,
    image=navigationDoctor,
    text='Doctors List',
    font=('Bahnschrift', 20, 'bold'),
    compound='left',
    anchor='w',
    fg_color='white',
    text_color='black',
    corner_radius=5,
    hover_color="#e0e0e0",
    command=lambda: show_doctors_list(None)
)
adminMakeAppointmentButton.pack(side='top', fill='x', pady=(0, 15), padx=10)

#Admin Dashboard
adminDashboardFrame = ctk.CTkFrame(adminMainFrame, fg_color=background)
adminDashboardFrame.pack(side='left', fill='both', expand=True)
adminStatusFrame = ctk.CTkFrame(adminDashboardFrame, fg_color=background)
adminStatusFrame.pack(side='top', fill='x', padx=20, pady=25)
adminStatusFrame.grid_columnconfigure((0, 1, 2), weight=1)
doctor_count_label = ctk.CTkLabel(adminStatusFrame, image=doctor, text='Doctors: 0', font=('Bahnschrift', 16),
                                  compound='left', padx=15, pady=10, fg_color='white',
                                  text_color='black', corner_radius=10)
doctor_count_label.grid(row=0, column=0, padx=20, pady=5, sticky='ew')

admin_ongoing_label = ctk.CTkLabel(adminStatusFrame, image=adminAppointment, text='Appointments: 0', font=('Bahnschrift', 16),
                                   compound='left', padx=15, pady=10, fg_color='white',
                                   text_color='black', corner_radius=10)
admin_ongoing_label.grid(row=0, column=2, padx=20, pady=5, sticky='ew')

patient_count_label = ctk.CTkLabel(adminStatusFrame, image=adminPatients, text='Patients: 0', font=('Bahnschrift', 16),
                                   compound='left', padx=15, pady=10, fg_color='white',
                                   text_color='black', corner_radius=10)
patient_count_label.grid(row=0, column=1, padx=20, pady=5, sticky='ew')

adminBookingMainFrame = ctk.CTkFrame(adminDashboardFrame, fg_color='white',corner_radius=7)
adminBookingMainFrame.pack(side='top', fill='both', expand=True, padx=20, pady=20)
adminBookingMainFrame.pack_propagate(True)
adminBookingHeader = ctk.CTkFrame(adminBookingMainFrame, height=100, fg_color=color2)
adminBookingHeader.pack(side='top', fill='x')
adminBookingHeader.pack_propagate(False)
ctk.CTkLabel(adminBookingHeader,image=adminCalendar,text='Latest Bookings',fg_color=color2,text_color='white',font=('Bahnschrift',19,'bold'),compound='left',padx=10).pack(side='left',padx=45)
adminBookingsFrame = ctk.CTkScrollableFrame(adminBookingMainFrame, fg_color='white',corner_radius=7)
adminBookingsFrame.pack(side='top', fill='both', expand=True, padx=20, pady=20)
adminBookingsFrame.pack_propagate(True)


#Admin Appointment
adminAppointmentFrame = ctk.CTkFrame(adminMainFrame,height=height,width=width,fg_color=background)
adminAppointmentLabelFrame = ctk.CTkFrame(adminAppointmentFrame, fg_color=background)
adminAppointmentLabelFrame.pack(side='top', fill='x', padx=20, pady=(25, 0))
ctk.CTkLabel(adminAppointmentLabelFrame, text='All Appointments', font=('Bahnschrift', 20, 'bold'), pady=10, fg_color=background,text_color='black').pack(side='left')
adminHistoryFrame = ctk.CTkFrame(adminAppointmentFrame, fg_color='white',corner_radius=7)
adminHistoryFrame.pack(side='top', fill='both', expand=True, padx=20, pady=(0, 20))
adminHistoryFrame.pack_propagate(True)
adminHistoryHeader = ctk.CTkFrame(adminHistoryFrame, height=40, fg_color=color2)
adminHistoryHeader.pack(side='top', fill='x')
adminHistoryHeader.pack_propagate(False)
adminHistoryHeader.grid_columnconfigure(0, weight=1)
adminHistoryHeader.grid_columnconfigure(1, weight=3)
adminHistoryHeader.grid_columnconfigure(2, weight=3)
adminHistoryHeader.grid_columnconfigure(3, weight=3)
adminHistoryHeader.grid_columnconfigure(4, weight=2)
adminHistoryHeader.grid_columnconfigure(5, weight=2)
ctk.CTkLabel(adminHistoryHeader, text='#', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=0, sticky='w', padx=10)
ctk.CTkLabel(adminHistoryHeader, text='Patient', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=1, sticky='w', padx=(30,30))
ctk.CTkLabel(adminHistoryHeader, text='Date & Time', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=2, sticky='w', padx=(50,10))
ctk.CTkLabel(adminHistoryHeader, text='Doctor', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=3, sticky='w', padx=(35,35))
ctk.CTkLabel(adminHistoryHeader, text='Fees', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=4, sticky='w', padx=10)
ctk.CTkLabel(adminHistoryHeader, text='Status', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=5, sticky='w', padx=10)
adminHistoryContent = ctk.CTkScrollableFrame(adminHistoryFrame, fg_color='white')
adminHistoryContent.pack(fill='both', expand=True)
adminHistoryContent.grid_columnconfigure(0, weight=1)
adminHistoryContent.grid_columnconfigure(1, weight=3)
adminHistoryContent.grid_columnconfigure(2, weight=3)
adminHistoryContent.grid_columnconfigure(3, weight=3)
adminHistoryContent.grid_columnconfigure(4, weight=2)
adminHistoryContent.grid_columnconfigure(5, weight=2)


#Admin Add Doctor
adminAddDoctorFrame = ctk.CTkFrame(adminMainFrame,height=height,width=width,fg_color=background)
adminAddDoctorLabelFrame = ctk.CTkFrame(adminAddDoctorFrame, fg_color=background)
adminAddDoctorLabelFrame.pack(side='top', fill='x', padx=20, pady=(25, 0))
ctk.CTkLabel(adminAddDoctorLabelFrame, text='Add Doctor', font=('Bahnschrift', 20, 'bold'), pady=10, fg_color=background,text_color='black').pack(side='left')
scrollableFrame = ctk.CTkScrollableFrame(adminAddDoctorFrame, fg_color=color2)
scrollableFrame.pack(padx=40, pady=30, fill='both', expand=True)
scrollableFrame.grid_columnconfigure(0, weight=1)
scrollableFrame.grid_columnconfigure(1, weight=1)
image_label = ctk.CTkLabel(scrollableFrame, text="Click to upload image",width=230, height=300, fg_color='#E0E0E0', corner_radius=10,text_color='gray', font=('Bahnschrift', 14))
image_label.pack(side='top',pady=10)
image_label.bind("<Button-1>", lambda e: select_image())
formRow = ctk.CTkFrame(scrollableFrame, fg_color=color2)
formRow.pack(padx=40, fill='both', expand=True)
leftColumn = ctk.CTkFrame(formRow, fg_color=color2)
leftColumn.pack(side='left', expand=True, fill='both', padx=(0, 20))
rightColumn = ctk.CTkFrame(formRow, fg_color=color2)
rightColumn.pack(side='left', expand=True, fill='both')
left_fields = [
    ("Full Name", "Enter doctor's full name"),
    ("Email", "Enter email address"),
    ("Password", "Enter password"),
    ("Fee", "1000")
]
right_fields = [
    ("Specialty", "e.g., Cardiologist"),
    ("Address", "Enter clinic address"),
    ("Experience", "10"),
]
entries = {}
for label, placeholder in left_fields:
    ctk.CTkLabel(leftColumn, text=label, text_color='white',font=('Bahnschrift', 15, 'bold')).pack(anchor='w', pady=(10, 5))
    if label.lower() == "fee":
        vcmd = leftColumn.register(is_numeric)
        doctor_entry = ctk.CTkEntry(
            leftColumn,
            placeholder_text=placeholder,
            height=40,
            corner_radius=8,
            font=('Bahnschrift', 14),
            validate="key",
            validatecommand=(vcmd, '%P'),
            fg_color='white',
            text_color='black'
        )
    else:
        doctor_entry = ctk.CTkEntry(
            leftColumn,
            placeholder_text=placeholder,
            height=40,
            corner_radius=8,
            font=('Bahnschrift', 14),
            fg_color='white',
            text_color='black'
        )
    doctor_entry.pack(fill='x', pady=(0, 10))
    entries[label] = doctor_entry

for label, placeholder in right_fields:
    ctk.CTkLabel(rightColumn, text=label, text_color='white',font=('Bahnschrift', 15, 'bold')).pack(anchor='w', pady=(10, 5))
    if label == "Specialty":
        doctor_entry = ctk.CTkComboBox(rightColumn,values=doctor_labels,font=('Bahnschrift', 14),height=40,corner_radius=8,state='readonly',fg_color='white',text_color='black',border_color='black')
        doctor_entry.set("Select specialty")
    elif label.lower() == "experience":
        vcmd = rightColumn.register(is_numeric)
        doctor_entry = ctk.CTkEntry(
            rightColumn,
            placeholder_text=placeholder,
            height=40,
            corner_radius=8,
            font=('Bahnschrift', 14),
            validate="key",
            validatecommand=(vcmd, '%P'),
            fg_color='white',
            text_color='black'
        )
    else:
        doctor_entry = ctk.CTkEntry(rightColumn,placeholder_text=placeholder,height=40, corner_radius=8,font=('Bahnschrift', 14),fg_color='white',text_color='black')
    doctor_entry.pack(fill='x', pady=(0, 10))
    entries[label] = doctor_entry

bottomSection = ctk.CTkFrame(scrollableFrame, fg_color=color2)
bottomSection.pack(fill='x', padx=40, pady=(0, 20))

ctk.CTkLabel(bottomSection, text="About Doctor", text_color='white',
             font=('Bahnschrift', 15, 'bold')).pack(anchor='w', pady=(10, 5))

about_textbox = ctk.CTkTextbox(bottomSection, height=100, corner_radius=10,
                               font=('Bahnschrift', 14), wrap='word', fg_color='white',text_color='black')
about_textbox.pack(fill='x')

submit_btn = ctk.CTkButton(bottomSection, text='Add Doctor',
                           height=60, font=('Bahnschrift', 20, 'bold'),
                           corner_radius=10, fg_color='white',text_color=color2,hover_color='#e0e0e0',
                           command=save_doctor
                           )
submit_btn.pack(pady=20,fill='x')

#Doctors List
adminDoctorListFrame = ctk.CTkFrame(adminMainFrame,height=height,width=width,fg_color=background)
adminDoctorHeader = ctk.CTkFrame(adminDoctorListFrame, height=50, fg_color=color2)
adminDoctorHeader.pack(side='top', fill='x', padx=20, pady=(20, 0))
adminDoctorHeader.pack_propagate(False)
ctk.CTkLabel(adminDoctorHeader, text='Doctors List', font=('Bahnschrift', 20, 'bold'), pady=10, fg_color='transparent', text_color='white').pack(side='left', padx=50)
remove_btn = ctk.CTkButton(adminDoctorHeader, text="Remove", fg_color="red", hover_color="#cc0000", width=90,
                            font=('Bahnschrift', 14), command=remove_selected_doctor)
remove_btn.pack(side='right', padx=(5, 10))

unavail_btn = ctk.CTkButton(adminDoctorHeader, text="Unavailable", fg_color="orange", width=100,
                             font=('Bahnschrift', 14), command=lambda: update_doctor_status("Unavailable"))
unavail_btn.pack(side='right', padx=(5, 10))

avail_btn = ctk.CTkButton(adminDoctorHeader, text="Available", fg_color="green", width=90,
                           font=('Bahnschrift', 14), command=lambda: update_doctor_status("Available"))
avail_btn.pack(side='right', padx=(5, 10))
adminDoctorFrame = ctk.CTkScrollableFrame(adminDoctorListFrame, width=width, height=height-60, fg_color='transparent')
adminDoctorFrame.pack(side='top', fill='both', expand=True, padx=20, pady=(10, 20))
load_doctors(adminDoctorFrame,force_refresh=True)

#Doctor Navigation
doctorMainFrame = ctk.CTkFrame(window, fg_color=background)
doctorFrame = ctk.CTkFrame(doctorMainFrame,height=height,width=300,fg_color=color2,corner_radius=0)
doctorFrame.pack(side='left', fill='y')
doctorFrame.pack_propagate(False)
doctorDashboardButton = ctk.CTkButton(
    doctorFrame,
    image=home,
    text='Dashboard',
    font=('Bahnschrift', 20, 'bold'),
    compound='left',
    anchor='w',
    fg_color='white',
    text_color='black',
    corner_radius=5,
    hover_color="#e0e0e0",
    command=lambda: show_dashboard(None)
)
doctorDashboardButton.pack(side='top', fill='x', pady=(40, 15), padx=10)

doctorAppointmentButton = ctk.CTkButton(
    doctorFrame,
    image=calendar,
    text='Appointments',
    font=('Bahnschrift', 20, 'bold'),
    compound='left',
    anchor='w',
    fg_color='white',
    text_color='black',
    corner_radius=5,
    hover_color="#e0e0e0",
    command=lambda: show_appointment(None)
)
doctorAppointmentButton.pack(side='top', fill='x', pady=(0, 15), padx=10)

#Doctor Dashboard
doctorDashboardFrame = ctk.CTkFrame(doctorMainFrame, fg_color=background)
doctorDashboardFrame.pack(side='left', fill='both', expand=True)
doctorStatusFrame = ctk.CTkFrame(doctorDashboardFrame, fg_color=background)
doctorStatusFrame.pack(side='top', fill='x', padx=20, pady=25)
doctorStatusFrame.grid_columnconfigure((0, 1, 2), weight=1)
doctor_income_label = ctk.CTkLabel(doctorStatusFrame, image=income, text='Income: 0', font=('Bahnschrift', 16),
                                  compound='left', padx=15, pady=10, fg_color='white',
                                  text_color='black', corner_radius=10)
doctor_income_label.grid(row=0, column=0, padx=20, pady=5, sticky='ew')

doctor_appointments_label = ctk.CTkLabel(doctorStatusFrame, image=adminAppointment, text='Appointments: 0', font=('Bahnschrift', 16),
                                   compound='left', padx=15, pady=10, fg_color='white',
                                   text_color='black', corner_radius=10)
doctor_appointments_label.grid(row=0, column=2, padx=20, pady=5, sticky='ew')

doctor_patient_label = ctk.CTkLabel(doctorStatusFrame, image=adminPatients, text='Patients: 0', font=('Bahnschrift', 16),
                                   compound='left', padx=15, pady=10, fg_color='white',
                                   text_color='black', corner_radius=10)
doctor_patient_label.grid(row=0, column=1, padx=20, pady=5, sticky='ew')
doctorBookingMainFrame = ctk.CTkFrame(doctorDashboardFrame, fg_color='white',corner_radius=7)
doctorBookingMainFrame.pack(side='top', fill='both', expand=True, padx=20, pady=20)
doctorBookingMainFrame.pack_propagate(True)
doctorBookingHeader = ctk.CTkFrame(doctorBookingMainFrame, height=100, fg_color=color2)
doctorBookingHeader.pack(side='top', fill='x')
doctorBookingHeader.pack_propagate(False)
ctk.CTkLabel(doctorBookingHeader,image=dashDoctor,text='Latest Bookings',fg_color=color2,text_color='white',font=('Bahnschrift',19,'bold'),compound='left',padx=10).pack(side='left',padx=45)
doctorBookingsFrame = ctk.CTkScrollableFrame(doctorBookingMainFrame, fg_color='white',corner_radius=7)
doctorBookingsFrame.pack(side='top', fill='both', expand=True, padx=20, pady=20)
doctorBookingsFrame.pack_propagate(True)

#Doctor Appointments
doctorAppointmentFrame = ctk.CTkFrame(doctorMainFrame,height=height,width=width,fg_color=background)
doctorAppointmentLabelFrame = ctk.CTkFrame(doctorAppointmentFrame, fg_color=background)
doctorAppointmentLabelFrame.pack(side='top', fill='x', padx=20, pady=(25, 0))
ctk.CTkLabel(doctorAppointmentLabelFrame, text='All Appointments', font=('Bahnschrift', 20, 'bold'), pady=10, fg_color=background,text_color='black').pack(side='left')
doctorHistoryFrame = ctk.CTkFrame(doctorAppointmentFrame, fg_color='white',corner_radius=7)
doctorHistoryFrame.pack(side='top', fill='both', expand=True, padx=20, pady=(0, 20))
doctorHistoryFrame.pack_propagate(True)
doctorHistoryHeader = ctk.CTkFrame(doctorHistoryFrame, height=40, fg_color=color2)
doctorHistoryHeader.pack(side='top', fill='x')
doctorHistoryHeader.pack_propagate(False)
doctorHistoryHeader.grid_columnconfigure(0, weight=1)
doctorHistoryHeader.grid_columnconfigure(1, weight=3)
doctorHistoryHeader.grid_columnconfigure(2, weight=3)
doctorHistoryHeader.grid_columnconfigure(3, weight=2)
doctorHistoryHeader.grid_columnconfigure(4, weight=2)
ctk.CTkLabel(doctorHistoryHeader, text='#', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=0, sticky='w', padx=10)
ctk.CTkLabel(doctorHistoryHeader, text='Patient', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=1, sticky='w', padx=10)
ctk.CTkLabel(doctorHistoryHeader, text='Date & Time', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=2, sticky='w', padx=(44,10))
ctk.CTkLabel(doctorHistoryHeader, text='Fees', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=3, sticky='w', padx=0)
ctk.CTkLabel(doctorHistoryHeader, text='Status', fg_color=color2, text_color='white', font=('Bahnschrift', 15, 'bold')).grid(row=0, column=4, sticky='w', padx=(0,10))
doctorHistoryContent = ctk.CTkScrollableFrame(doctorHistoryFrame, fg_color='white')
doctorHistoryContent.pack(fill='both', expand=True)
doctorHistoryContent.grid_columnconfigure(0, weight=1)
doctorHistoryContent.grid_columnconfigure(1, weight=3)
doctorHistoryContent.grid_columnconfigure(2, weight=3)
doctorHistoryContent.grid_columnconfigure(3, weight=2)
doctorHistoryContent.grid_columnconfigure(4, weight=2)

try:
    window.mainloop()
except KeyboardInterrupt:
    print("Program interrupted. Exiting...")
    window.quit()