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
git clone https://github.com/your-username/task-flow.git
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
SECRET_KEY=your-django-secret-key
DEBUG=True
REDIS_URL=redis://localhost:6379
ALLOWED_HOSTS=127.0.0.1,localhost
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
celery -A taskFlow beat --loglevel=info
```

## 🌐 API URL Structure

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| /api/login/ | POST | All | Login to get tokens |
| /api/logout/ | POST | All | Logout and blacklist tokens |
| /api/token/refresh/ | POST | All | Refresh access token |
| /api/change-password/ | POST | Authenticated | Change current user's password |
| /api/users/ | POST | Admin | Create users |
| /api/departments/ | POST | Admin | Create departments |
| /api/projects/ | POST | Admin/Manager | Create projects |
| /api/tasks/ | POST | Admin/Manager | Create tasks |
| /api/tasks/{id}/status/ | PATCH | Developer | Update task status |
| /api/tasks/overdue/ | GET | System | Automated (by Celery Beat) |

⚠️ More routes and detailed descriptions can be added if Swagger or DRF-YASG is integrated.

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

- Use PostgreSQL or MySQL for production
- Set DEBUG=False in .env
- Configure Gunicorn + Nginx
- Use Docker (optional but recommended)
- Secure Redis & Celery with proper worker configurations

## 🤝 Contributions

Feel free to open issues or submit PRs to improve the system.

## 📜 License

MIT License © 2025

## 🙌 Acknowledgements

Built with ❤️ by [Your Name]
Inspired by real-world task & project management needs.