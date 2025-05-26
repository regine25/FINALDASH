import openpyxl
import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",
    database="scheduling_db"
)
cursor = conn.cursor()

# Load the Excel file
wb = openpyxl.load_workbook(r"C:\Users\Jello Marimla\OneDrive\Desktop\scheduling-app\subjects.xlsx")
sheet = wb.active

# Insert subject data
for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip header
    print(f"Inserting: {row}")  # Debugging output
    cursor.execute("INSERT INTO Subjects (subject_code, subject_name, required_specialization) VALUES (%s, %s, %s)", row)

conn.commit()
conn.close()
print("✅ Subjects inserted successfully!")
