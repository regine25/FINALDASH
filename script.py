import openpyxl
import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(host="localhost", user="root", password="yourpassword", database="scheduling_db")
cursor = conn.cursor()

# Open the Excel file
wb = openpyxl.load_workbook("subjects.xlsx")
sheet = wb.active

# Insert subject data
for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip header
    cursor.execute("INSERT INTO Subjects (subject_code, subject_name, required_specialization) VALUES (%s, %s, %s)", row)

conn.commit()
conn.close()
print("Subjects inserted successfully!")
