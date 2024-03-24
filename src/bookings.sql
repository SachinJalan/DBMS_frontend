CREATE DATABASE IF NOT EXISTS lab_bookings;

USE lab_bookings;

CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    lab_name VARCHAR(255) NOT NULL,
    time_from TIME NOT NULL,
    time_to TIME NOT NULL ,
    date DATE NOT NULL
);


CREATE TABLE IF NOT EXISTS `inventory` (
  `ID` bigint NOT NULL,
  `Equipment_Name` varchar(255) NOT NULL,
  `Price` float DEFAULT NULL,
  `Vendor_Address` varchar(255) DEFAULT NULL,
  `Vendor_Phone_Number` varchar(255) DEFAULT NULL,
  `Manufacturer_Name` varchar(255) DEFAULT NULL,
  `Status` varchar(255) DEFAULT NULL,
    `Lab_Name` ENUM('Anatomy Lab', 'Biochemistry Lab', 'Biology Lab', 'Botany Lab', 'Chemistry Lab', 'Computer Lab', 'Ecology Lab', 'Engineering Lab', 'Genetics Lab', 'Geology Lab', 'Microbiology Lab', 'Neuroscience Lab', 'Physics Lab', 'Psychology Lab', 'Zoology Lab') NOT NULL, 
  `Quantity` int DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `ID` (`ID`)
);

CREATE TABLE IF NOT EXISTS users (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `role` VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `course` (
	`email` varchar(255) NOT NULL,
  `Course_ID` varchar(255) NOT NULL,
  `Credits` int DEFAULT NULL,
  `Course_Name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Course_ID`),
  UNIQUE KEY `Course_ID` (`Course_ID`)
);


CREATE TABLE IF NOT EXISTS `student_enrolled` (
  `Course_ID` varchar(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`Course_ID`,`email`)
);

CREATE TABLE IF NOT EXISTS EquipmentIssued (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(255),
    equipment_type VARCHAR(255),
    number_of_equipment INT,
    issue_date DATE,
    return_date DATE
);


