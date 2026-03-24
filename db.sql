CREATE DATABASE IF NOT EXISTS campusinfra_db;
USE campusinfra_db;
--@block
CREATE TABLE IF NOT EXISTS User
(
    user_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(20) NOT NULL,
    middle_name VARCHAR(20) NULL,
    last_name VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    date_of_birth DATE NOT NULL,
    age INT, --derived attribute from DOB
    user_availability_start TIME,
    user_availability_end TIME,
    user_availability_status VARCHAR(255) CHECK (user_availability_status IN('Available','Busy','Inactive')),
    user_type VARCHAR(20) CHECK (user_type IN ('Student','Faculty','Staff'))
);

--@block
CREATE TABLE IF NOT EXISTS User_Phone
(
    user_id FOREIGN KEY,
    phone_no VARCHAR(15) PRIMARY KEY
);

--@block
CREATE TABLE IF NOT EXISTS Location
(
    building_name VARCHAR(100) NOT NULL, 
    room_no VARCHAR(20) NOT NULL,
    floor INT NOT NULL,
    location_type VARCHAR(30) CHECK(location_type IN('Room','Lab','Corridor','Ground','Campus Area')),

    PRIMARY KEY (building_name,room_no) --Composite Key with 2 columns
);

--@block
CREATE TABLE IF NOT EXISTS Issue
(
    issue_id INT PRIMARY KEY AUTO_INCREMENT,

    issue_category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    reported_date DATETIME NOT NULL,
    completion_date DATETIME NULL,
    resolution_time  INT, --derived attribute from reproted_date and completion
    status VARCHAR(20) CHECK(status IN('Pending','Under Review','Scheduled','In Progress','Resolved','Closed','Escalated')),
    proof_image VARCHAR(255)  --image path/url
    FOREIGN KEY(building_name) REFERENCES Location(building_name)
    ON DELETE SET NULL;
    FOREIGN KEY(building_name) REFERENCES Location(building_name)
    ON DELETE SET NULL;
    FOREIGN KEY(room_no) REFERENCES Location(room_no)
    ON DELETE SET NULL;
    
);

--@block
CREATE TABLE IF NOT EXISTS Technician
(
    technician_id INT PRIMARY KEY AUTO_INCREMENT,
    technician_name VARCHAR(100) NOT NULL,
    technician_phone VARCHAR(15) NOT NULL,
    specialization VARCHAR(50) NOT NULL ,
    technician_availability_start TIME ,
    technician_availability_end TIME,
    technician_availability_status VARCHAR(20) CHECK(availability_status IN ('Available','Busy','On Leave'))
   
);

--@block
CREATE TABLE IF NOT EXISTS Technician_Skill
(
    technician_id INT,
    FOREIGN KEY (technician_id) REFERENCES Technician(technician_id) ON DELETE CASCADE;
    skill VARCHAR(50) NOT NULL,

    PRIMARY KEY (technician_id,skill) -- Composite ID with 2 columns
);

--@block
CREATE TABLE IF NOT EXISTS Appliance
(
    appliance_id INT PRIMARY KEY AUTO_INCREMENT,
    appliance_name VARCHAR(100) NOT NULL,
    quantity_available INT CHECK(quantity_available >= 0)
);

CREATE TABLE IF NOT EXISTS Administrator
(
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    admin_name VARCHAR(100) NOT NULL,
    admin_phone VARCHAR(15) NOT NULL,
    admin_email VARCHAR(100) NOT NULL UNIQUE
);

--@block
CREATE TABLE IF NOT EXISTS Slot
(
    slot_id INT PRIMARY KEY AUTO_INCREMENT,
    slot_date DATE NOT NULL,
    slot_start_time TIME NOT NULL,
    slot_end_time TIME NOT NULL,
    slot_status VARCHAR(20) CHECK(slot_status IN ('Available','Booked','Completed','Cancelled'))
);

--@block
CREATE TABLE IF NOT EXISTS Work_Verification
(
    verification_id INT AUTO_INCREMENT,
    issue_id INT,
    admin_checked BOOLEAN DEFAULT FALSE,
    user_checked BOOLEAN DEFAULT FALSE, 
    verification_date DATE NOT NULL,
    FOREIGN KEY (issue_id) REFERENCES Issue(issue_id)
);


--RELATIONSHIP TABLES--

--@block
CREATE TABLE IF NOT EXISTS REPORTS --USER->ISSUE
(
    user_id INT,
    issue_id  INT,
    issue_category VARCHAR(30) CHECK(issue_category IN ('Electrical','Plumbing','Furniture','Network','Cleanliness','STructural','Other'))
    report_time DATETIME NOT NULL,
    urgency_flag BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (issue_id) REFERENCES Issue(issue_id),

    PRIMARY KEY(user_id,issue_id)
);

--@block
CREATE TABLE IF NOT EXISTS HANDLES --ADMIN->ISSUE
(
    admin_id INT,
    issue_id  INT,
    handle_date DATE NOT NULL,
    remarks TEXT NULL,
    issue_resolution_type VARCHAR(30) CHECK IN ('Temporary Fix','Permanent Repair','Replacement','Escalated'),
    escalated_level INT CHECK(escalation_level >=0),

    
    FOREIGN KEY (issue_id) REFERENCES Issue(issue_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    PRIMARY KEY (admin_id,issue_id)
);

--@block
CREATE TABLE IF NOT EXISTS ASSIGNS --ADMIN->SLOT
(
    admin_id INT,
    slot_id  INT,
    assigned_date DATE,
    assigned_priority VARCHAR(20) CHECK IN('Normal','Urgent','Immediate'),
    assignment_notes TEXT,

    FOREIGN KEY (admin_id) REFERENCES Administrator(admin_id),
    FOREIGN KEY (slot_id) REFERENCES Slot(slot_id)
);

--@block
CREATE TABLE IF NOT EXISTS HAS --SLOT->TECHNICIAN
(
    slot_id INT PRIMARY KEY,
    technician_id INT,
    technician_role VARCHAR(30) CHECK IN('Electrician','Plumber','Carpenter','IT Support', 'General Maintenance'),
    technician_availability_status VARCHAR(20) CHECK IN('Available','Busy','On Leave'),

    FOREIGN KEY (slot_id) REFERENCES Slot(slot_id),
    FOREIGN KEY (technician_id) REFERENCES Technician(technician_id)
);

--@block
CREATE TABLE SCHEDULED_IN --  (ISSUE -> SLOT)
(
    issue_id INT UNIQUE,
    slot_id INT UNIQUE,
    scheduled_date DATE NOT NULL,
    reschedule_count INT DEFAULT 0,
    delay_reason TEXT NULL,
    
    FOREIGN KEY (issue_id) REFERENCES Issue(issue_id),
    FOREIGN KEY (slot_id) REFERENCES Slot(slot_id),
    PRIMARY KEY (issue_id, slot_id)
);

--@block
CREATE TABLE IF NOT EXISTS REQUIRES -- (ISSUE -> APPLIANCE)  
(
    issue_id INT,
    appliance_id INT,
    quantity_used INT CHECK (quantity_used>0),
    damage_severity VARCHAR(20) CHECK(damage_severity IN ('Minor','Moderate','Severe')),
    repair_cost_estimate DECIMAL(10,2) CHECK(repair_cost_estimate >=0),
   
    FOREIGN KEY (issue_id) REFERENCES ISSUE(issue_id),
    FOREIGN KEY (appliance_id) REFERENCES APPLIANCE(appliance_id),
     PRIMARY KEY (issue_id, appliance_id)
);
