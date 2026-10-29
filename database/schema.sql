-- AUTO PDI: MySQL 8+ Schema DDL Definition
-- Database: autopdi

CREATE DATABASE IF NOT EXISTS autopdi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE autopdi;

-- 1. users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('CUSTOMER', 'INSPECTOR', 'ADMIN') NOT NULL DEFAULT 'CUSTOMER',
    profile_image VARCHAR(255) DEFAULT '/static/images/default-avatar.png',
    status ENUM('ACTIVE', 'INACTIVE', 'BLOCKED', 'PENDING') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_role (role)
) ENGINE=InnoDB;

-- 2. vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    variant VARCHAR(50),
    fuel_type VARCHAR(30) NOT NULL DEFAULT 'Petrol',
    vehicle_type ENUM('ICE', 'EV', 'HYBRID') NOT NULL DEFAULT 'ICE',
    vin VARCHAR(50) NOT NULL,
    registration_number VARCHAR(50),
    manufacturing_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_vehicle_vin (vin),
    INDEX idx_vehicle_customer (customer_id)
) ENGINE=InnoDB;

-- 3. showrooms table
CREATE TABLE IF NOT EXISTS showrooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50),
    postal_code VARCHAR(20),
    contact_number VARCHAR(20),
    latitude FLOAT DEFAULT 12.9716,
    longitude FLOAT DEFAULT 77.5946,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 4. inspectors table
CREATE TABLE IF NOT EXISTS inspectors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    bio TEXT,
    experience_years INT NOT NULL DEFAULT 1,
    total_inspections INT NOT NULL DEFAULT 0,
    rating FLOAT NOT NULL DEFAULT 5.0,
    trust_score INT NOT NULL DEFAULT 90,
    verification_status ENUM('PENDING', 'VERIFIED', 'REJECTED', 'SUSPENDED') NOT NULL DEFAULT 'PENDING',
    availability_status ENUM('AVAILABLE', 'BUSY', 'OFFLINE') NOT NULL DEFAULT 'AVAILABLE',
    latitude FLOAT DEFAULT 12.9716,
    longitude FLOAT DEFAULT 77.5946,
    specialization VARCHAR(255) DEFAULT 'ICE, EV, Hybrid',
    price_standard FLOAT NOT NULL DEFAULT 1499.00,
    price_premium FLOAT NOT NULL DEFAULT 2499.00,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_inspector_status (verification_status, availability_status)
) ENGINE=InnoDB;

-- 5. equipment table
CREATE TABLE IF NOT EXISTS equipment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspector_id INT NOT NULL,
    equipment_name VARCHAR(100) NOT NULL,
    equipment_type VARCHAR(50),
    serial_number VARCHAR(100),
    verification_status ENUM('PENDING', 'VERIFIED', 'REJECTED') NOT NULL DEFAULT 'PENDING',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspector_id) REFERENCES inspectors(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 6. certifications table
CREATE TABLE IF NOT EXISTS certifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspector_id INT NOT NULL,
    certificate_name VARCHAR(150) NOT NULL,
    issuer VARCHAR(100) NOT NULL,
    certificate_number VARCHAR(100),
    issue_date DATE,
    expiry_date DATE,
    document_url VARCHAR(255),
    verification_status ENUM('PENDING', 'VERIFIED', 'REJECTED') NOT NULL DEFAULT 'PENDING',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspector_id) REFERENCES inspectors(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. inspector_specializations table
CREATE TABLE IF NOT EXISTS inspector_specializations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspector_id INT NOT NULL,
    brand VARCHAR(50),
    vehicle_type VARCHAR(20) NOT NULL,
    skill_level VARCHAR(20) NOT NULL DEFAULT 'EXPERT',
    FOREIGN KEY (inspector_id) REFERENCES inspectors(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 8. availability table
CREATE TABLE IF NOT EXISTS availability (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspector_id INT NOT NULL,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (inspector_id) REFERENCES inspectors(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 9. bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    showroom_id INT NOT NULL,
    inspector_id INT,
    inspection_type ENUM('STANDARD', 'PREMIUM') NOT NULL DEFAULT 'PREMIUM',
    scheduled_date DATE NOT NULL,
    scheduled_time TIME NOT NULL,
    price FLOAT NOT NULL DEFAULT 2499.00,
    status ENUM('REQUESTED', 'ACCEPTED', 'REJECTED', 'RESCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED') NOT NULL DEFAULT 'REQUESTED',
    payment_status ENUM('PENDING', 'PAID', 'REFUNDED') NOT NULL DEFAULT 'PAID',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (showroom_id) REFERENCES showrooms(id) ON DELETE CASCADE,
    FOREIGN KEY (inspector_id) REFERENCES inspectors(id) ON DELETE SET NULL,
    INDEX idx_booking_status (status)
) ENGINE=InnoDB;

-- 10. inspection_categories table
CREATE TABLE IF NOT EXISTS inspection_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    vehicle_type VARCHAR(20) NOT NULL DEFAULT 'ALL',
    weight FLOAT NOT NULL DEFAULT 15.0,
    description VARCHAR(255)
) ENGINE=InnoDB;

-- 11. inspections table
CREATE TABLE IF NOT EXISTS inspections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL UNIQUE,
    vehicle_id INT NOT NULL,
    inspector_id INT NOT NULL,
    vin_verified BOOLEAN DEFAULT FALSE,
    started_at DATETIME,
    completed_at DATETIME,
    overall_score FLOAT DEFAULT 0.0,
    final_status ENUM('DELIVERY_READY', 'ATTENTION_REQUIRED', 'HOLD_DELIVERY') NOT NULL DEFAULT 'ATTENTION_REQUIRED',
    ai_score FLOAT DEFAULT 0.0,
    inspection_hash VARCHAR(64),
    verification_code VARCHAR(30) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (inspector_id) REFERENCES inspectors(id) ON DELETE CASCADE,
    INDEX idx_inspection_code (verification_code)
) ENGINE=InnoDB;

-- 12. inspection_checkpoints table
CREATE TABLE IF NOT EXISTS inspection_checkpoints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id INT NOT NULL,
    category_id INT NOT NULL,
    item_name VARCHAR(150) NOT NULL,
    status ENUM('PASS', 'ATTENTION', 'FAIL', 'NOT_APPLICABLE') NOT NULL DEFAULT 'PASS',
    severity ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL DEFAULT 'LOW',
    remark TEXT,
    ai_detected BOOLEAN DEFAULT FALSE,
    ai_confidence FLOAT DEFAULT 0.0,
    inspector_verified BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES inspection_categories(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 13. inspection_media table
CREATE TABLE IF NOT EXISTS inspection_media (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id INT NOT NULL,
    checkpoint_id INT,
    file_url VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL DEFAULT 'IMAGE',
    latitude FLOAT,
    longitude FLOAT,
    captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ai_analysis TEXT,
    ai_confidence FLOAT DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE,
    FOREIGN KEY (checkpoint_id) REFERENCES inspection_checkpoints(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 14. ai_findings table
CREATE TABLE IF NOT EXISTS ai_findings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id INT NOT NULL,
    checkpoint_id INT NOT NULL,
    image_id INT,
    finding_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    confidence FLOAT NOT NULL DEFAULT 0.85,
    severity ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') NOT NULL DEFAULT 'LOW',
    inspector_confirmation ENUM('PENDING', 'CONFIRMED', 'REJECTED') NOT NULL DEFAULT 'PENDING',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE,
    FOREIGN KEY (checkpoint_id) REFERENCES inspection_checkpoints(id) ON DELETE CASCADE,
    FOREIGN KEY (image_id) REFERENCES inspection_media(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 15. reports table
CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id INT NOT NULL UNIQUE,
    report_number VARCHAR(50) NOT NULL UNIQUE,
    overall_score FLOAT NOT NULL,
    report_url VARCHAR(255),
    verification_code VARCHAR(30) NOT NULL UNIQUE,
    report_hash VARCHAR(64) NOT NULL,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE,
    INDEX idx_report_code (verification_code)
) ENGINE=InnoDB;

-- 16. ratings table
CREATE TABLE IF NOT EXISTS ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    inspector_id INT NOT NULL,
    rating FLOAT NOT NULL DEFAULT 5.0,
    review TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (inspector_id) REFERENCES inspectors(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 17. notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    booking_id INT,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'INFO',
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 18. issue_resolution table
CREATE TABLE IF NOT EXISTS issue_resolution (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id INT NOT NULL,
    checkpoint_id INT NOT NULL,
    issue_description TEXT NOT NULL,
    status ENUM('OPEN', 'DEALER_NOTIFIED', 'IN_PROGRESS', 'RESOLVED', 'CUSTOMER_VERIFIED') NOT NULL DEFAULT 'OPEN',
    dealer_response TEXT,
    resolution_image VARCHAR(255),
    customer_verified BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE,
    FOREIGN KEY (checkpoint_id) REFERENCES inspection_checkpoints(id) ON DELETE CASCADE
) ENGINE=InnoDB;
