-- MediOptima Database Schema
-- Run this script to create the required tables for hospital data

-- Create database
CREATE DATABASE IF NOT EXISTS hospital_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hospital_db;

-- Table 1: Patient Admissions
CREATE TABLE IF NOT EXISTS patient_admissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admission_date DATETIME NOT NULL,
    discharge_date DATETIME,
    patient_id VARCHAR(50),
    ward_type ENUM('General', 'ICU', 'Emergency', 'Maternity') DEFAULT 'General',
    is_emergency BOOLEAN DEFAULT FALSE,
    diagnosis_code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_admission_date (admission_date),
    INDEX idx_ward_type (ward_type)
);

-- Table 2: Bed Inventory (Daily snapshot)
CREATE TABLE IF NOT EXISTS bed_inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    bed_type ENUM('General', 'ICU', 'Emergency', 'Maternity') DEFAULT 'General',
    total_beds INT NOT NULL DEFAULT 0,
    occupied_beds INT NOT NULL DEFAULT 0,
    available_beds INT GENERATED ALWAYS AS (total_beds - occupied_beds) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_date_type (date, bed_type),
    INDEX idx_date (date)
);

-- Table 3: Staff Roster (Daily)
CREATE TABLE IF NOT EXISTS staff_roster (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    role ENUM('Doctor', 'Nurse', 'ICU Nurse', 'Technician', 'Admin') NOT NULL,
    staff_count INT NOT NULL DEFAULT 0,
    shift ENUM('Morning', 'Evening', 'Night', 'All') DEFAULT 'All',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_date_role (date, role, shift),
    INDEX idx_date (date)
);

-- Table 4: Daily Metrics Summary (Pre-aggregated)
CREATE TABLE IF NOT EXISTS daily_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_patients INT DEFAULT 0,
    emergency_cases INT DEFAULT 0,
    icu_admissions INT DEFAULT 0,
    discharge_count INT DEFAULT 0,
    available_general_beds INT DEFAULT 0,
    available_icu_beds INT DEFAULT 0,
    doctors_on_duty INT DEFAULT 0,
    nurses_on_duty INT DEFAULT 0,
    icu_nurses INT DEFAULT 0,
    is_holiday BOOLEAN DEFAULT FALSE,
    temperature DECIMAL(4,1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_date (date)
);

-- Insert sample data for testing
INSERT INTO patient_admissions (admission_date, discharge_date, ward_type, is_emergency) VALUES
(NOW() - INTERVAL 1 DAY, NULL, 'General', FALSE),
(NOW() - INTERVAL 1 DAY, NOW() - INTERVAL 12 HOUR, 'ICU', TRUE),
(NOW() - INTERVAL 2 DAY, NULL, 'General', FALSE),
(NOW() - INTERVAL 2 DAY, NOW() - INTERVAL 1 DAY, 'Emergency', TRUE),
(NOW() - INTERVAL 3 DAY, NULL, 'ICU', FALSE);

INSERT INTO bed_inventory (date, bed_type, total_beds, occupied_beds) VALUES
(CURDATE(), 'General', 350, 280),
(CURDATE(), 'ICU', 45, 38),
(CURDATE() - INTERVAL 1 DAY, 'General', 350, 275),
(CURDATE() - INTERVAL 1 DAY, 'ICU', 45, 40);

INSERT INTO staff_roster (date, role, staff_count) VALUES
(CURDATE(), 'Doctor', 25),
(CURDATE(), 'Nurse', 80),
(CURDATE(), 'ICU Nurse', 18),
(CURDATE() - INTERVAL 1 DAY, 'Doctor', 23),
(CURDATE() - INTERVAL 1 DAY, 'Nurse', 78),
(CURDATE() - INTERVAL 1 DAY, 'ICU Nurse', 17);

-- Create a view for easy querying
CREATE OR REPLACE VIEW hospital_summary AS
SELECT 
    d.date,
    d.total_patients,
    d.emergency_cases,
    d.icu_admissions,
    d.discharge_count,
    d.available_general_beds,
    d.available_icu_beds,
    d.doctors_on_duty,
    d.nurses_on_duty,
    d.icu_nurses,
    d.is_holiday,
    d.temperature
FROM daily_metrics d
ORDER BY d.date DESC;

-- Grant permissions (adjust username as needed)
-- GRANT ALL PRIVILEGES ON hospital_db.* TO 'medoptima_user'@'localhost';
-- FLUSH PRIVILEGES;
