from flask import Flask, request, jsonify
from flask_cors import CORS
from db import mysql
import config

app = Flask(__name__)
CORS(app)

# DB config
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql.init_app(app)

#Opening message
@app.route('/')
def home():
    return {"message": "Backend running"}


#Registration API
@app.route('/register', methods=['POST'])  
# This creates an API endpoint:
# URL - http://localhost:5000/register
# Method - POST (used to send data)

def register():

    data = request.json  
    # Get JSON data sent from frontend
    # Example:
    # {
    #   "first_name": "Leah",
    #   "last_name": "Sonowal",
    #   "email": "leah@gmail.com",
    #   "date_of_birth": "2004-01-01",
    #   "user_type": "Student"
    # }

    cursor = mysql.connection.cursor()  
    # Create a cursor object to execute SQL queries

    cursor.execute("""
        INSERT INTO User 
        (first_name, middle_name, last_name, email, date_of_birth, user_type)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data['first_name'],              # Required field
        data.get('middle_name'),         # Optional field
        data['last_name'],               # Required field
        data['email'],                   # Must be unique
        data['date_of_birth'],           # Format: YYYY-MM-DD
        data['user_type']                # Student / Faculty / Staff
    ))

    mysql.connection.commit()  # Save changes permanently in database

    cursor.close()   # Close cursor to free resources

    return jsonify     # Send response back to frontend in JSON format
    ({  
        "message": "User registered successfully"
    })  
   
#Report Issue API - send data to backend -> database
@app.route('/report-issue', methods=['POST'])
def report_issue():
    data = request.json

    cursor = mysql.connection.cursor()

    # 1. Insert into Issue
    cursor.execute("""
        INSERT INTO Issue (issue_category, description, reported_date, status)
        VALUES (%s, %s, NOW(), 'Pending')
    """, (data['category'], data['description']))

    issue_id = cursor.lastrowid

    # 2. Insert into REPORTS
    cursor.execute("""
        INSERT INTO REPORTS (user_id, issue_id, report_time, urgency_flag)
        VALUES (%s, %s, NOW(), %s)
    """, (data['user_id'], issue_id, data['urgent']))

    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Issue reported", "issue_id": issue_id})


#Get All Issues API - lets frontend FETCH data from database
@app.route('/issues',methods=['GET'])
def get_issues():
    cursor = mysql.connection.cursor()

    cursor.execute = ("SELECT * FROM ISSUE")
    rows = cursor.fetchall()

    issues=[]
    for row in rows:
        issues.append
        ({
            "issue_id": row[0],
            "category": row[1],
            "description": row[2],
            "status": row[6]
        })

    cursor.close()
    return jsonify(issues)
    

#Update Issue Status - makes system interactive
@app.route('/update-status/<int:id>', methods=['PUT'])
# API endpoint:
# URL → http://localhost:5000/update-status/1
# <int:id> → dynamic value (issue_id passed in URL)
# Method - PUT (used for updating data)

def update_status(id):

    data = request.json  
    status = data['status']  
 
    valid_status = ['Pending','Under Review','Scheduled','In Progress','Resolved','Closed','Escalated']
    if status not in valid_status:
       return jsonify({"error": "Invalid status"}), 400
    cursor = mysql.connection.cursor()  
    
    cursor.execute("""
        UPDATE Issue 
        SET status=%s 
        WHERE issue_id=%s
    """, (status, id))
    # Update status of specific issue
    # %s used to safely insert values

    mysql.connection.commit()  
    
    cursor.close()  

    return jsonify
    ({"message": "Status updated successfully"})

#Assign technician API
@app.route('/assign', methods=['POST'])
def assign():
    data = request.json

    cursor = mysql.connection.cursor()

    # Create slot
    cursor.execute("""
        INSERT INTO Slot (slot_date, slot_start_time, slot_end_time, slot_status)
        VALUES (%s, %s, %s, 'Booked')
    """, (data['date'], data['start'], data['end']))

    slot_id = cursor.lastrowid #retrieves the auto-generated primary key (ID) 
    #of the newly inserted row in the Slot table from the previous INSERT statemen

    # Assign technician
    cursor.execute("""
        INSERT INTO HAS (slot_id, technician_id)
        VALUES (%s, %s)
    """, (slot_id, data['technician_id']))

    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Technician assigned"})

#Delete Issue API
@app.route('/delete-issue/<int:id>', methods=['DELETE'])
def delete_issue(id):

    cursor = mysql.connection.cursor()
    
     #Check if issue exists
    cursor.execute("SELECT * FROM Issue WHERE issue_id=%s", (id,))
    issue = cursor.fetchone()

    if not issue:
        cursor.close()
        return jsonify({
            "error": "Issue not found"
        }), 404
    # If issue doesn't exist then return error

    #Delete issue
    cursor.execute("DELETE FROM Issue WHERE issue_id=%s", (id,))
    # Because of ON DELETE CASCADE → related records auto deleted

    mysql.connection.commit()
    
    cursor.close()
   
    return jsonify({
        "message": "Issue deleted successfully"
    })

   

#Run server
if __name__ == '__main__':
    app.run(debug=True)
