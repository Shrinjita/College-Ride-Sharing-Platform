# SRM Ride Pool Application

A secure and user-friendly web application for SRM University students to coordinate ride-sharing and improve campus transportation safety.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Authentication System](#authentication-system)
- [User Roles](#user-roles)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Screenshots](#screenshots)
- [Security Features](#security-features)
- [Future Enhancements](#future-enhancements)

## 📝 Overview

SRM Ride Pool is a campus-specific ride-sharing application designed for SRM University students. It allows students to find and share rides within and around campus, enhancing convenience and safety while reducing individual transportation costs.

## ✨ Features

### User Features
- **User Registration & Authentication**: Secure registration with SRM roll numbers
- **Ride Booking**: Schedule rides with pickup/drop locations and times
- **Ride Management**: View, track, and manage ride history
- **SOS Alert System**: Emergency assistance at the press of a button
- **Contact Integration**: Easy one-tap calling for ride participants

### Admin Features
- **Comprehensive Dashboard**: Analytics on rides, users, and issues
- **Ride Monitoring**: Track all rides across the campus
- **User Management**: Monitor user activity and registrations
- **SOS Response System**: Track and respond to emergency alerts
- **Issue Resolution System**: Handle reported ride problems

## 💻 Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python with Flask
- **Database**: SQLite3
- **Authentication**: Session-based Authentication
- **Styling**: Custom CSS with responsive design

## 📁 Project Structure

```
SRM-Ride-Pool/
├── app.py                     # Main Flask application file
├── ride_pool.db               # SQLite database
├── .env                       # Environment variables (secret key)
├── static/
│   ├── style.css              # Main stylesheet
│   ├── script.js              # JavaScript for common functionality
├── templates/
│   ├── signin.html            # Login and registration page
│   ├── index.html             # User dashboard
│   ├── admin.html             # Admin dashboard
```

## 🚀 Setup Instructions

1. **Clone the repository**

2. **Create a virtual environment**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```
   pip install flask python-dotenv
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root with:
   ```
   FLASK_SECRET_KEY=your_secure_secret_key_here
   ```

5. **Initialize the database**
   The database will be created automatically on first run

6. **Run the application**
   ```
   python app.py
   ```
   Access the application at `http://localhost:5000`

## 🔐 Authentication System

- **User Authentication**: Based on SRM roll number with pattern `RA2211047010xxx`
- **Password Generation**: Created using pattern `srmXXX` where XXX is the last three digits of roll number
- **Admin Access**: Special credentials for administrative functions
  - **Admin Username**: RA2211047010017
  - **Admin Password**: ADMIN

## 👥 User Roles

### Regular User
- Can register/login with their SRM roll number
- Create and manage personal rides
- View ride history
- Send SOS alerts in emergencies

### Administrator
- Access comprehensive analytics dashboard
- View and manage all rides in the system
- Handle user reported issues and SOS alerts
- Edit or delete any ride in the system

## 🗃️ Database Schema

The application uses four main tables:

### user
- `id`: Unique identifier (Primary Key)
- `roll_number`: SRM roll number (Unique)
- `phone_number`: Contact number
- `created_at`: Registration timestamp

### ride
- `id`: Unique identifier (Primary Key)
- `user_id`: Reference to user table
- `pickup`: Pickup location
- `drop`: Drop location
- `time`: Scheduled time
- `gender`: Gender specification
- `contact`: Contact information
- `status`: Ride status (Scheduled/Completed)

### sos_alerts
- `id`: Unique identifier (Primary Key)
- `user_id`: Reference to user table
- `timestamp`: Alert time
- `resolved`: Resolution status

### ride_issues
- `id`: Unique identifier (Primary Key)
- `ride_id`: Reference to ride table
- `issue_type`: Category of issue
- `description`: Detailed description
- `timestamp`: Report time
- `resolved`: Resolution status

## 📡 API Endpoints

### Authentication
- `POST /login`: User login
- `POST /register`: New user registration
- `GET /logout`: User logout

### Ride Management
- `POST /add_ride`: Create new ride
- `GET /get_ride`: Get ride details
- `POST /edit_ride`: Update ride information
- `POST /delete_ride`: Remove ride

### Emergency & Support
- `POST /send_sos`: Send emergency alert
- `POST /report_issue`: Report ride issue
- `POST /resolve_sos`: Mark SOS alert resolved
- `POST /resolve_issue`: Mark ride issue resolved

### Dashboards
- `GET /user`: User dashboard
- `GET /admin`: Admin dashboard
- `GET /admin_stats`: Admin statistics

## 📷 Screenshots

*Screenshots would be included here*

## 🔒 Security Features

- **Input Validation**: Strict validation for registration numbers and inputs
- **SQL Injection Protection**: Using parameterized queries
- **Session Management**: Secure session handling
- **Authentication Checks**: Route protection based on user roles
- **Error Handling**: Proper error messages without exposing system details

## 🚀 Future Enhancements

- **Real-time ride tracking** using WebSockets
- **Payment integration** for paid rides
- **Rating system** for drivers and passengers
- **Ride scheduling** for recurring rides
- **Mobile application** with push notifications
- **Email/SMS notifications** for ride updates
- **Advanced ride filtering** options
- **Chat functionality** between ride participants
- **Integration with campus events** for coordinated transportation
