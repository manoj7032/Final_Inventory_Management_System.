# Final_Inventory_Management_System.

This Inventory Management System is a robust Flask application designed to manage inventory efficiently. It features user authentication, advanced caching with Redis, and load balancing using Nginx, making it ideal for high-traffic environments.

## Features

- User Authentication: Secure user login and registration with bcrypt for password encryption.
- Inventory Operations: Users can add, view, edit, and delete inventory items.
- Redis Caching: Enhances performance by caching frequently accessed data.
- Nginx Load Balancing: Distributes traffic across multiple instances to improve responsiveness and reliability.

## Technology Stack

- Flask: Lightweight WSGI web application framework.
- Redis: High-performance in-memory database, used for caching.
- Nginx: Acts as a reverse proxy and load balancer.
- HTML/CSS: For the frontend presentation.
- bcrypt: Used for securing passwords.

## Getting Started

Follow these instructions to get your project up and running on your local machine for development and testing purposes.

### Prerequisites

Ensure you have the following installed:
- Python 3.6+
- Flask
- Redis
- Nginx

### Installation

1. Install Ms Visual Code.
2. Download the project Files from git. All HTML files are present in templates folder with app.py file.
3. Now Open this project in Ms Visual Code and open terminal.
4. In the terminal install Venv to run the flask application and open Venv ( python -m venv venv  and  .\venv\Scripts\activate  )
5. Install the required python packages.
   Packages - pymysql , flask-login, flask-bcrypt, flask-sqlalchemy, redis.
7. Start the Redis server:
Ensure Redis is running on your machine. You can start Redis by executing --> redis-server
8. Now open another terminal in MsVisualCode and start the Flask application in another server. (Our flask application runs in localhost:5000; and localhost:5001;)
9. Configure and start Nginx:
Refer to the Nginx configuration provided below to set up Nginx as a load balancer.
Configuration -
Here's a basic setup for using Nginx as a load balancer for this application:
upstream inventoryapp {
    server localhost:5000;
    server localhost:5001;
}

server {
    listen 80;
    location / {
        proxy_pass http://inventoryapp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
##Usage
Access the web application via http://localhost after starting the Flask app and ensure Nginx is configured to redirect as shown above.

