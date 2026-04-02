import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image
import hashlib

# Page configuration
st.set_page_config(
    page_title="Attendance Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for yellow background
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFE0;
    }
    .main > div {
        background-color: #FFFFE0;
    }
    .stButton>button {
        background-color: #FFD700;
        color: black;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FFC700;
        color: black;
    }
    .stTextInput>div>div>input {
        background-color: white;
    }
    .stSelectbox>div>div>select {
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Data file paths
STUDENTS_FILE = "students.json"
ATTENDANCE_FILE = "attendance.json"

# Initialize data files if they don't exist
def init_data_files():
    if not os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'w') as f:
            json.dump({}, f)

# Load data
def load_students():
    init_data_files()
    with open(STUDENTS_FILE, 'r') as f:
        return json.load(f)

def save_students(students):
    with open(STUDENTS_FILE, 'w') as f:
        json.dump(students, f, indent=4)

def load_attendance():
    init_data_files()
    with open(ATTENDANCE_FILE, 'r') as f:
        return json.load(f)

def save_attendance(attendance):
    with open(ATTENDANCE_FILE, 'w') as f:
        json.dump(attendance, f, indent=4)

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register new student
def register_student(name, student_id, roll_number, section, password):
    students = load_students()
    
    # Check if student ID already exists
    if student_id in students:
        return False, "Student ID already exists!"
    
    # Check if roll number already exists
    for sid, data in students.items():
        if data['roll_number'] == roll_number and data['section'] == section:
            return False, "Roll number already exists in this section!"
    
    students[student_id] = {
        'name': name,
        'student_id': student_id,
        'roll_number': roll_number,
        'section': section,
        'password': hash_password(password),
        'registered_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_students(students)
    return True, "Registration successful!"

# Verify login
def verify_login(student_id, password):
    students = load_students()
    if student_id not in students:
        return False, None
    if students[student_id]['password'] == hash_password(password):
        return True, students[student_id]
    return False, None

# Mark attendance
def mark_attendance(student_id, status='present'):
    attendance = load_attendance()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if today not in attendance:
        attendance[today] = {}
    
    attendance[today][student_id] = {
        'status': status,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_attendance(attendance)

# Get student attendance
def get_student_attendance(student_id):
    attendance = load_attendance()
    student_attendance = []
    for date, records in attendance.items():
        if student_id in records:
            student_attendance.append({
                'date': date,
                'status': records[student_id]['status'],
                'timestamp': records[student_id]['timestamp']
            })
    return sorted(student_attendance, key=lambda x: x['date'], reverse=True)

# Main app
def main():
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'student_id' not in st.session_state:
        st.session_state.student_id = None
    if 'student_data' not in st.session_state:
        st.session_state.student_data = None
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

    # Home page
    if st.session_state.page == 'home':
        st.title("🎓 Attendance Management System")
        st.markdown("---")
        
        # Display image
        try:
            image_path = "WhatsApp Image 2025-11-09 at 3.43.45 PM.jpeg"
            if os.path.exists(image_path):
                img = Image.open(image_path)
                st.image(img, use_container_width=True, caption="Welcome to Attendance Management System")
            else:
                st.warning("Image file not found. Please ensure the image is in the project folder.")
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")
        
        st.markdown("### Welcome to the Attendance Management System")
        st.markdown("Please select an option from below:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.page = 'home'
        
        with col2:
            if st.button("📝 Register", use_container_width=True):
                st.session_state.page = 'register'
                st.rerun()
        
        with col3:
            if st.button("🔐 Student Login", use_container_width=True):
                st.session_state.page = 'login'
                st.rerun()
    
    # Registration page
    elif st.session_state.page == 'register':
        st.title("📝 Student Registration")
        st.markdown("---")
        
        with st.form("registration_form"):
            st.markdown("### Fill in your details:")
            name = st.text_input("Student Name *", placeholder="Enter your full name")
            student_id = st.text_input("Student ID *", placeholder="Enter unique student ID")
            roll_number = st.text_input("Roll Number *", placeholder="Enter roll number")
            section = st.selectbox("Section *", ["A", "B", "C", "D", "E", "F"])
            password = st.text_input("Password *", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Confirm your password")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Register", use_container_width=True)
            with col2:
                back = st.form_submit_button("Back to Home", use_container_width=True)
            
            if back:
                st.session_state.page = 'home'
                st.rerun()
            
            if submit:
                if not all([name, student_id, roll_number, section, password, confirm_password]):
                    st.error("Please fill in all fields!")
                elif password != confirm_password:
                    st.error("Passwords do not match!")
                elif len(password) < 4:
                    st.error("Password must be at least 4 characters long!")
                else:
                    success, message = register_student(name, student_id, roll_number, section, password)
                    if success:
                        st.success(message)
                        st.info("You can now login with your Student ID and Password")
                        st.session_state.page = 'home'
                        st.rerun()
                    else:
                        st.error(message)
    
    # Login page
    elif st.session_state.page == 'login':
        st.title("🔐 Student Login")
        st.markdown("---")
        
        with st.form("login_form"):
            st.markdown("### Enter your credentials:")
            student_id = st.text_input("Student ID *", placeholder="Enter your student ID")
            password = st.text_input("Password *", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                login = st.form_submit_button("Login", use_container_width=True)
            with col2:
                back = st.form_submit_button("Back to Home", use_container_width=True)
            
            if back:
                st.session_state.page = 'home'
                st.rerun()
            
            if login:
                if not student_id or not password:
                    st.error("Please enter both Student ID and Password!")
                else:
                    success, student_data = verify_login(student_id, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.student_id = student_id
                        st.session_state.student_data = student_data
                        st.session_state.page = 'dashboard'
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid Student ID or Password!")
    
    # Dashboard page
    elif st.session_state.page == 'dashboard' and st.session_state.logged_in:
        st.title("📊 Student Dashboard")
        st.markdown("---")
        
        # Student information
        student_data = st.session_state.student_data
        st.markdown("### Student Information")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.info(f"**Name:** {student_data['name']}")
        with col2:
            st.info(f"**Student ID:** {student_data['student_id']}")
        with col3:
            st.info(f"**Roll Number:** {student_data['roll_number']}")
        with col4:
            st.info(f"**Section:** {student_data['section']}")
        
        st.markdown("---")
        
        # Attendance record
        st.markdown("### Your Attendance Record")
        attendance_records = get_student_attendance(st.session_state.student_id)
        
        if attendance_records:
            # Summary
            total_days = len(attendance_records)
            present_days = sum(1 for record in attendance_records if record['status'] == 'present')
            absent_days = total_days - present_days
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Days", total_days)
            with col2:
                st.metric("Present Days", present_days)
            with col3:
                st.metric("Absent Days", absent_days)
            with col4:
                st.metric("Attendance %", f"{attendance_percentage:.1f}%")
            
            st.markdown("---")
            
            # Detailed records
            st.markdown("### Detailed Attendance History")
            for record in attendance_records:
                status_color = "🟢" if record['status'] == 'present' else "🔴"
                st.markdown(f"**{record['date']}** - {status_color} {record['status'].upper()} - {record['timestamp']}")
        else:
            st.info("No attendance records found. Your attendance will appear here once marked.")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.student_id = None
            st.session_state.student_data = None
            st.session_state.page = 'home'
            st.success("Logged out successfully!")
            st.rerun()
    
    else:
        st.session_state.page = 'home'
        st.rerun()

if __name__ == "__main__":
    main()

