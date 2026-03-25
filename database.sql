CREATE DATABASE IF NOT EXISTS campusinfra_db;
USE campusinfra_db;

--USER 
CREATE TABLE User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(20) NOT NULL,
    middle_name VARCHAR(20),
    last_name VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    date_of_birth DATE NOT NULL,
    age INT,
    user_availability_start TIME,
    user_availability_end TIME,
    user_availability_status ENUM('Available','Busy','Inactive'),
    user_type ENUM('Student','Faculty','Staff')
);

--USER PHONE 
CREATE TABLE User_Phone (
    phone_no VARCHAR(15) PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

--LOCATION
CREATE TABLE Location (
    building_name VARCHAR(100),
    room_no VARCHAR(20),
    floor INT NOT NULL,
    location_type ENUM('Room','Lab','Corridor','Ground','Campus Area'),
    PRIMARY KEY (building_name, room_no)
);

--ISSUE 
CREATE TABLE Issue (
    issue_id INT AUTO_INCREMENT PRIMARY KEY,
    issue_category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    reported_date DATETIME NOT NULL,
    completion_date DATETIME,
    resolution_time INT,
    status ENUM('Pending','Under Review','Scheduled','In Progress','Resolved','Closed','Escalated'),
    proof_image VARCHAR(255),
    building_name VARCHAR(100),
    room_no VARCHAR(20),
    
    FOREIGN KEY (building_name, room_no) 
    REFERENCES Location(building_name, room_no) 
    ON DELETE SET NULL
);

--TECHNICIAN
CREATE TABLE Technician (
    technician_id INT AUTO_INCREMENT PRIMARY KEY,
    technician_name VARCHAR(100) NOT NULL,
    technician_phone VARCHAR(15) NOT NULL,
    specialization VARCHAR(50) NOT NULL,
    technician_availability_start TIME,
    technician_availability_end TIME,
    technician_availability_status ENUM('Available','Busy','On Leave')
);

--TECHNICIAN SKILL
CREATE TABLE Technician_Skill (
    technician_id INT,
    skill VARCHAR(50),
    PRIMARY KEY (technician_id, skill),
    FOREIGN KEY (technician_id) REFERENCES Technician(technician_id) ON DELETE CASCADE
);

--APPLIANCE
CREATE TABLE Appliance (
    appliance_id INT AUTO_INCREMENT PRIMARY KEY,
    appliance_name VARCHAR(100) NOT NULL,
    quantity_available INT CHECK (quantity_available >= 0)
);

--ADMIN
CREATE TABLE Administrator (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    admin_name VARCHAR(100) NOT NULL,
    admin_phone VARCHAR(15) NOT NULL,
    admin_email VARCHAR(100) UNIQUE
);

--SLOT
CREATE TABLE Slot (
    slot_id INT AUTO_INCREMENT PRIMARY KEY,
    slot_date DATE NOT NULL,
    slot_start_time TIME NOT NULL,
    slot_end_time TIME NOT NULL,
    slot_status ENUM('Available','Booked','Completed','Cancelled')
);

--WORK VERIFICATION
CREATE TABLE Work_Verification (
    verification_id INT AUTO_INCREMENT PRIMARY KEY,
    issue_id INT,
    admin_checked BOOLEAN DEFAULT FALSE,
    user_checked BOOLEAN DEFAULT FALSE,
    verification_date DATE,
    FOREIGN KEY (issue_id) REFERENCES Issue(issue_id)
);

-- RELATIONSHIP TABLES --

--REPORTS
CREATE TABLE Reports (
    user_id INT,
    issue_id INT,
    issue_category ENUM('Electrical','Plumbing','Furniture','Network','Cleanliness','Structural','Other'),
    report_time DATETIME NOT NULL,
    urgency_flag BOOLEAN DEFAULT FALSE,
    PRIMARY KEY(user_id, issue_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (issue_id) REFERENCES Issue(issue_id)
);

--HANDLES
CREATE TABLE Handles (
    admin_id INT,
    issue_id INT,
    handle_date DATE NOT NULL,
    remarks TEXT,
    issue_resolution_type ENUM('Temporary Fix','Permanent Repair','Replacement','Escalated'),
    escalated_level INT CHECK (escalated_level >= 0),
    PRIMARY KEY (admin_id, issue_id),
    FOREIGN KEY (admin_id) REFERENCES Administrator(admin_id),
    FOREIGN KEY (issue_id) REFERENCES Issue(issue_id)
);

--ASSIGNS 
CREATE TABLE Assigns (
    admin_id INT,
    slot_id INT,
    assigned_date DATE,
    assigned_priority ENUM('Normal','Urgent','Immediate'),
    assignment_notes TEXT,
    PRIMARY KEY (admin_id, slot_id),
    FOREIGN KEY (admin_id) REFERENCES Administrator(admin_id),
    FOREIGN KEY (slot_id) REFERENCES Slot(slot_id)
);

--HAS 
CREATE TABLE Has (
    slot_id INT PRIMARY KEY,
    technician_id INT,
    technician_role ENUM('Electrician','Plumber','Carpenter','IT Support','General Maintenance'),
    technician_availability_status ENUM('Available','Busy','On Leave'),
    FOREIGN KEY (slot_id) REFERENCES Slot(slot_id),
    FOREIGN KEY (technician_id) REFERENCES Technician(technician_id)
);

--SCHEDULED 
CREATE TABLE Scheduled_In (
    issue_id INT UNIQUE,
    slot_id INT UNIQUE,
    scheduled_date DATE NOT NULL,
    reschedule_count INT DEFAULT 0,
    delay_reason TEXT,
    PRIMARY KEY (issue_id, slot_id),
    FOREIGN KEY (issue_id) REFERENCES Issue(issue_id),
    FOREIGN KEY (slot_id) REFERENCES Slot(slot_id)
);


--REQUIRES 
CREATE TABLE Requires (
    issue_id INT,
    appliance_id INT,
    quantity_used INT CHECK (quantity_used > 0),
    damage_severity ENUM('Minor','Moderate','Severe'),
    repair_cost_estimate DECIMAL(10,2) CHECK (repair_cost_estimate >= 0),
    PRIMARY KEY (issue_id, appliance_id),
    FOREIGN KEY (issue_id) REFERENCES Issue(issue_id),
    FOREIGN KEY (appliance_id) REFERENCES Appliance(appliance_id)
);
