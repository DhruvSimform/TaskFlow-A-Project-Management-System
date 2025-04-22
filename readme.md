# 🗂️ Task-Flow – Project & Task Management System

Task-Flow is a role-based project and task management system developed using Django REST Framework. It supports Admin, Manager, and Developer roles with customized functionalities like user and department management, project tracking, task scheduling, automated overdue status marking, and secure authentication with JWT. It also features background task processing using Celery and Redis.

---

## 🚀 Features
### 🔐 Authentication & User Management
- JWT-based Auth (Access & Refresh Tokens)
- Custom Login, Logout (with Token Blacklisting)
- Role-based user access: `Admin`, `Manager`, `Developer`
- Change Password API
- User profile management with profile picture upload (stored in Cloudinary)

### 👥 Role-Based Access Control
- Admin can create Departments, Managers, Developers
- Admin can assign users to departments
- Object-level permission checks for sensitive actions

### 📁 Project & Task Management
- Admin/Manager can create projects and add other users (Developers, Managers, or Admins) as project collaborators.
- Admin/Manager can create tasks, and tasks can be collaborated on by multiple users.
- Collaborator Developers can also create tasks for themselves.
- Tasks can have multiple sub-tasks, but sub-tasks cannot have further sub-tasks.
- Both projects and tasks have object-level permission checks to restrict certain actions based on roles.


### 📅 Task Scheduler
- **Celery**: Sends email notifications to users when they are added as collaborators or assigned tasks.
- **Celery Beat**: Implements scheduled background tasks to send daily reminders to users about their pending tasks, categorized project-wise.

### 🔄 Token Handling
- **Access Token**: Used for authenticating API requests. It has a short lifespan for enhanced security.
- **Refresh Token**: Allows users to generate a new access token without re-authenticating. Refresh tokens are rotated upon use to prevent misuse.
- **Token Blacklisting**: On logout, both access and refresh tokens are stored in the Redis cache with their lifespan, ensuring they are invalidated and cannot be reused for authentication.
- **Secure Workflow**: Users can generate new access tokens using valid refresh tokens, while blacklisted tokens are blocked from further use.

---

## 🛠️ Tech Stack

| Tech            | Use Case                              |
|-----------------|----------------------------------------|
| **Python**      | Core programming language              |
| **Django**      | Web framework backend                  |
| **DRF**         | REST APIs                              |
| **PostgreSQL**  | Production database                    |
| **Celery**      | Background task processing             |
| **Celery Beat** | Scheduled background tasks             |
| **Redis**       | Celery broker & JWT token blacklist    |
| **Cloudinary**  | File/media storage                     |
| **JWT**         | Authentication                         |


---

## 🧾 Installation

### 1. Clone the repo

```bash
git git@github.com:DhruvSimform/TaskFlow-A-Project-Management-System.git
cd Task-Flow
```

### 2. Create virtual environment and activate

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a .env file in the root directory:

```env
# Project Setup keys
DJANGO_SECRET_KEY = 'your_django_secret_key'

# PostgreSQL Configurations 
DATABASE_NAME = 'TaskFlow'
DATABASE_USER = 'your_database_user'
DATABASE_PASSWORD = 'your_database_password'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5432'

# JWT Configuration
ACCESS_TOKEN_LIFETIME_MIN = 30 
REFRESH_TOKEN_LIFETIME_HRS = 2 
ROTATE_REFRESH_TOKENS = True
BLACKLIST_AFTER_ROTATION = True

# Redis Location
RESISH_LOCATION = 'redis://127.0.0.1:6379/1'

# Email
EMAIL_HOST_USER = 'your_email@example.com'
EMAIL_HOST_PASSWORD = 'your_email_password'

# Cloudinary
CLOUD_NAME = 'your_cloud_name'
API_KEY = 'your_api_key'
API_SECRET = 'your_api_secret'

```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Run development server

```bash
python manage.py runserver
```

## 🧵 Celery Setup

### 1. Start Redis server
Make sure Redis is installed and running:

```bash
redis-server
```

### 2. Start Celery Worker

```bash
celery -A taskFlow worker --loglevel=info
```

### 3. Start Celery Beat Scheduler

```bash
```bash
celery -A taskFlow beat --loglevel=info
```

## 🌐 API URL Structure

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| /api/account/login/ | POST | All | Login to get tokens |
| /api/account/logout/ | POST | All | Logout and blacklist tokens |
| /api/account/token/refresh/ | POST | All | Refresh access token |
| /api/account/change-password/ | POST | Authenticated | Change current user's password |
| /api/account/request-reset-password/ | POST | All | Request password reset |
| /api/account/request-reset-password/{uidb64}/{token}/ | POST | All | Confirm password reset |
| /api/account/profile-pic/ | PUT | Authenticated | Update profile picture |
| /api/account/ | GET | Authenticated | Get dashboard details |
| /api/organization/users/ | GET, POST | Admin | View all users or create a new user |
| /api/organization/users/{email}/ | GET, PUT | Admin | Retrieve or update a user by email |
| /api/organization/departments/ | GET, POST | Admin | View all departments or create a new department |
| /api/organization/departments/{id}/ | GET, PUT | Admin | Retrieve or update a department by ID |
| /api/project_management/ | GET, POST | Admin, Manager | List all projects or create a new project |
| /api/project_management/projects/{id}/ | GET, PUT, DELETE | Admin, Collaborator | Retrieve, update, or delete a specific project |
| /api/project_management/projects/{id}/collaborators/{email}/ | POST | Admin, Manager | Add a collaborator to a specific project |
| /api/project/tasks/ | GET, POST | Admin, Manager, Collaborator | List all tasks or create a new task |
| /api/project/tasks/{id}/ | GET, PUT, DELETE | Admin, Manager, Collaborator | Retrieve, update, or delete a specific task |
| /api/project/tasks/{id}/subtasks/ | GET, POST | Admin, Manager, Collaborator | List or create subtasks for a specific task |
| /api/project/tasks/{id}/collaborators/{email}/ | POST | Admin, Manager | Add a collaborator to a specific task |


### 🔍 Filtering, Searching, and Ordering

The following APIs support filtering, searching, and ordering:

#### **Project Management**
- **Endpoint**: `/api/project_management/projects/`
    - **Filterable Fields**: `status`
    - **Searchable Fields**: `name`, `description`
    - **Orderable Fields**: `updated_at`, `status`

#### **Task Management**
- **Endpoint**: `/api/project/<int:project_id>/tasks/`
    - **Filterable Fields**: `status`, `priority`, `project`, `created_by`
    - **Searchable Fields**: `title`, `description`, `project__name`, `status`, `priority`
    - **Orderable Fields**: `start_date`, `due_date`, `priority`, `status`, `title`

## 🧩 Project Structure

```bash
Task-Flow/
├── account/                 # Authentication and user-related views
├── organization/            # Department and user management
├── project_management/      # Project-related logic
├── task_management/         # Task creation, update, scheduler
├── taskFlow/                # Settings, celery, URLs
├── .env                     # Environment config
├── manage.py                # Django entrypoint
├── requirements.txt         # Dependencies
└── readme.md                # Project documentation
```

## 🌍 Deployment

- Use PostgreSQL for production
- Set DEBUG=False in .env
- Configure Gunicorn + Nginx
- Use Docker (optional but recommended)
- Secure Redis & Celery with proper worker configurations

## 🤝 Contributions

Feel free to open issues or submit PRs to improve the system.

## 📜 License

MIT License © 2025

## 🙌 Acknowledgements

Built with ❤️ by Dhruv Patel
Inspired by real-world task & project management needs.
