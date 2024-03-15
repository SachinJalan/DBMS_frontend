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

CREATE TABLE IF NOT EXISTS users (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL
);


CREATE TABLE IF NOT EXISTS EquipmentIssued (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(255),
    equipment_type VARCHAR(255),
    number_of_equipment INT,
    issue_date DATE,
    return_date DATE
);


