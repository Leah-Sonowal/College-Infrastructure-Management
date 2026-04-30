CREATE DATABASE IF NOT EXISTS campusinfra_db;
USE campusinfra_db;

-- USER
CREATE TABLE IF NOT EXISTS User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(20) NOT NULL,
    middle_name VARCHAR(20),
    last_name VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    date_of_birth DATE NOT NULL,
    age INT,
    password VARCHAR(255) NOT NULL,          -- ← was missing from original schema
    user_availability_start TIME,
    user_availability_end TIME,
    user_availability_status ENUM('Available','Busy','Inactive'),
    user_type ENUM('Student','Faculty','Staff') NOT NULL
);

-- USER PHONE
CREATE TABLE IF NOT EXISTS User_Phone (
    phone_no VARCHAR(15) PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

-- LOCATION
CREATE TABLE IF NOT EXISTS Location (
    building_name VARCHAR(100),
    room_no VARCHAR(20),
    floor INT NOT NULL,
    location_type ENUM('Room','Lab','Corridor','Ground','Campus Area'),
    PRIMARY KEY (building_name, room_no)
);

-- ISSUE
CREATE TABLE IF NOT EXISTS Issue (
    issue_id INT AUTO_INCREMENT PRIMARY KEY,
    issue_category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    reported_date DATETIME NOT NULL,
    completion_date DATETIME,
    resolution_time INT,
    status ENUM('Pending','Under Review','Scheduled','In Progress','Resolved','Closed','Escalated') DEFAULT 'Pending',
    proof_image VARCHAR(255),
    building_name VARCHAR(100),
    room_no VARCHAR(20),
    FOREIGN KEY (building_name, room_no)
        REFERENCES Location(building_name, room_no)
        ON DELETE SET NULL
);

-- TECHNICIAN
CREATE TABLE IF NOT EXISTS Technician (
    technician_id INT AUTO_INCREMENT PRIMARY KEY,
    technician_name VARCHAR(100) NOT NULL,
    technician_phone VARCHAR(15) NOT NULL,
    specialization VARCHAR(50) NOT NULL,
    technician_availability_start TIME,
    technician_availability_end TIME,
    technician_availability_status ENUM('Available','Busy','On Leave') DEFAULT 'Available'
);

-- TECHNICIAN SKILL
CREATE TABLE IF NOT EXISTS Technician_Skill (
    technician_id INT,
    skill VARCHAR(50),
    PRIMARY KEY (technician_id, skill),
    FOREIGN KEY (technician_id) REFERENCES Technician(technician_id) ON DELETE CASCADE
);

-- APPLIANCE
CREATE TABLE IF NOT EXISTS Appliance (
    appliance_id INT AUTO_INCREMENT PRIMARY KEY,
    appliance_name VARCHAR(100) NOT NULL,
    quantity_available INT CHECK (quantity_available >= 0)
);

-- ADMIN
CREATE TABLE IF NOT EXISTS Administrator (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    admin_name VARCHAR(100) NOT NULL,
    admin_phone VARCHAR(15) NOT NULL,
    admin_email VARCHAR(100) UNIQUE
);

-- SLOT
CREATE TABLE IF NOT EXISTS Slot (
    slot_id INT AUTO_INCREMENT PRIMARY KEY,
    slot_date DATE NOT NULL,
    slot_start_time TIME NOT NULL,
    slot_end_time TIME NOT NULL,
    slot_status ENUM('Available','Booked','Completed','Cancelled') DEFAULT 'Available'
);

-- WORK VERIFICATION
CREATE TABLE IF NOT EXISTS Work_Verification (
    verification_id INT AUTO_INCREMENT PRIMARY KEY,
    issue_id INT,
    admin_checked BOOLEAN DEFAULT FALSE,
    user_checked BOOLEAN DEFAULT FALSE,
    verification_date DATE,
    FOREIGN KEY (issue_id) REFERENCES Issue(issue_id)
);

-- REPORTS
CREATE TABLE IF NOT EXISTS Reports (
    user_id INT,
    issue_id INT,
    issue_category ENUM('Electrical','Plumbing','Furniture','Network','Cleanliness','Structural','Other'),
    report_time DATETIME NOT NULL,
    urgency_flag BOOLEAN DEFAULT FALSE,
    PRIMARY KEY(user_id, issue_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (issue_id) REFERENCES Issue(issue_id)
);

-- HANDLES
CREATE TABLE IF NOT EXISTS Handles (
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

-- ASSIGNS
CREATE TABLE IF NOT EXISTS Assigns (
    admin_id INT,
    slot_id INT,
    assigned_date DATE,
    assigned_priority ENUM('Normal','Urgent','Immediate'),
    assignment_notes TEXT,
    PRIMARY KEY (admin_id, slot_id),
    FOREIGN KEY (admin_id) REFERENCES Administrator(admin_id),
    FOREIGN KEY (slot_id) REFERENCES Slot(slot_id)
);

-- HAS
CREATE TABLE IF NOT EXISTS Has (
    slot_id INT PRIMARY KEY,
    technician_id INT,
    technician_role ENUM('Electrician','Plumber','Carpenter','IT Support','General Maintenance'),
    technician_availability_status ENUM('Available','Busy','On Leave'),
    FOREIGN KEY (slot_id) REFERENCES Slot(slot_id),
    FOREIGN KEY (technician_id) REFERENCES Technician(technician_id)
);

-- SCHEDULED_IN
CREATE TABLE IF NOT EXISTS Scheduled_In (
    issue_id INT UNIQUE,
    slot_id INT UNIQUE,
    scheduled_date DATE NOT NULL,
    reschedule_count INT DEFAULT 0,
    delay_reason TEXT,
    PRIMARY KEY (issue_id, slot_id),
    FOREIGN KEY (issue_id) REFERENCES Issue(issue_id),
    FOREIGN KEY (slot_id) REFERENCES Slot(slot_id)
);

-- REQUIRES
CREATE TABLE IF NOT EXISTS Requires (
    issue_id INT,
    appliance_id INT,
    quantity_used INT CHECK (quantity_used > 0),
    damage_severity ENUM('Minor','Moderate','Severe'),
    repair_cost_estimate DECIMAL(10,2) CHECK (repair_cost_estimate >= 0),
    PRIMARY KEY (issue_id, appliance_id),
    FOREIGN KEY (issue_id) REFERENCES Issue(issue_id),
    FOREIGN KEY (appliance_id) REFERENCES Appliance(appliance_id)
);

-- =============================================
-- SEED DATA (for demo/evaluation)
-- =============================================

-- Locations
INSERT IGNORE INTO Location (building_name, room_no, floor, location_type) VALUES
('Block A', '101', 1, 'Room'),
('Block B', 'Lab3', 2, 'Lab'),
('Main Block', 'Server Room', 0, 'Room');

-- Technicians
INSERT IGNORE INTO Technician (technician_name, technician_phone, specialization, technician_availability_status) VALUES
('John Kumar', '9876543210', 'Network', 'Available'),
('Alice Raj', '9876543211', 'Hardware', 'Available'),
('Bob Singh', '9876543212', 'Software', 'Busy');

-- Sample Issues
INSERT IGNORE INTO Issue (issue_id, issue_category, description, reported_date, status, building_name, room_no) VALUES
(101, 'Network', 'WiFi down in Building A — no connectivity since morning', NOW(), 'In Progress', 'Block A', '101'),
(102, 'Hardware', 'Printer out of ink, replacement needed urgently', NOW(), 'Pending', 'Block B', 'Lab3'),
(103, 'Software', 'System needs OS update, causing boot delays', NOW(), 'Resolved', 'Main Block', 'Server Room'),
(104, 'Network', 'Server core dump error, requires immediate attention', NOW(), 'Pending', 'Main Block', 'Server Room');
