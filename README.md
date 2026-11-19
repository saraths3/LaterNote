# LaterNote – Messages to Your Future Self

> A peaceful, minimal web application to write letters to your future self. Messages remain securely locked until your chosen unlock date arrives.

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-darkgreen.svg)](https://www.djangoproject.com/)
[![ASGI Server](https://img.shields.io/badge/Server-Uvicorn-purple.svg)](https://www.uvicorn.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📖 Overview

**LaterNote** is a full-stack Django web application crafted as a showcase portfolio project for a junior Django developer. It allows users to write private reflections, milestones, and advice to their future selves. Each message is sealed with a target unlock date in the future and remains strictly locked until that date arrives.

### Why this project stands out:
- **Clean Django Conventions**: Uses pure function-based views (FBVs), native Django forms, standard ModelForms, and Django's built-in authentication without convoluted layers.
- **Dynamic Lock Engine**: No complicated Celery workers or Redis queues. Status is evaluated dynamically using Django's timezone utilities (`timezone.localdate() >= unlock_date`).
- **Zero Content Leak Guarantee**: Locked messages **never leak their content** in HTML responses or client-side scripts.
- **Production Ready with Render & Uvicorn**: Includes a minimal, beginner-friendly `main.py` entrypoint that automatically handles migrations, collects static assets via WhiteNoise, and spins up a high-performance **Uvicorn ASGI server**.

---

## 🎨 Interface Preview & Wireframes

```text
┌────────────────────────────────────────────────────────────────────────┐
│  LaterNote    [ Dashboard ]   [ My Messages ]   [ New Message ]  (User)│
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   🔒 LOCKED MESSAGE (Before Unlock Date)                               │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │                     [ 🔒 Padlock Icon ]                        │   │
│   │              Unlocks in 42 days • Career & Study               │   │
│   │                                                                │   │
│   │               "Letter to Myself on My First Job"               │   │
│   │                                                                │   │
│   │      [!] This message is sealed in the vault.                  │   │
│   │          The content remains completely hidden until           │   │
│   │          October 15, 2027.                                     │   │
│   │                                                                │   │
│   │          [ Back ]       [ Edit Title ]       [ Delete ]        │   │
│   └────────────────────────────────────────────────────────────────┘   │
│                                                                        │
│   🔓 UNLOCKED MESSAGE (On or After Unlock Date)                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │  [ Unlocked ] • Personal Goals             [ Print Keepsake ]  │   │
│   │                                                                │   │
│   │  "Reflections on Starting My Journey"                          │   │
│   │  Written by you on January 10, 2026                            │   │
│   │  ────────────────────────────────────────────────────────────  │   │
│   │  Dear Future Me,                                               │   │
│   │  Today I wrote my very first Django application from scratch.  │   │
│   │  I hope you are proud of how far we have come...               │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features Breakdown

### 1. User Authentication & Isolation
- User registration, login, and logout powered by Django's native authentication framework.
- Robust password validation with user-friendly feedback.
- Strict data isolation: queries filter strictly by `user=request.user`. Users can never view, edit, or delete another user's letters.

### 2. Message Creation & Future Date Validation
- Clean ModelForm (`MessageCreateForm`) capturing Title, Category, Content, and Unlock Date.
- Date validation guarantees that the unlock date is strictly in the future (`> today`).
- HTML5 date widget dynamically injects a `min` attribute set to tomorrow's date for an intuitive browser datepicker experience.

### 3. Dynamic Message Vault (Locking Mechanism)
- **Dynamic Calculation**: Evaluates status on-the-fly (`message.is_locked()` and `message.is_unlocked()`).
- **Information Security**: When locked, the template `messages/locked.html` renders only the metadata and countdown. `{{ message.content }}` is completely absent from the template context and response body.
- When unlocked, the letter is revealed in full with typography formatted via `linebreaks`.

### 4. Message Organization & Themes
- Organize letters into 6 meaningful categories:
  - 💼 `Career & Study`
  - 🎯 `Goals & Aspirations`
  - 🧘 `Reflections`
  - 🏆 `Milestones & Memories`
  - 🙏 `Gratitude`
  - 🌿 `Personal`
- Color-coded badges displayed across all list views and cards.

### 5. Search & Real-Time Filtering
- Keyword search by message title directly in "My Messages".
- Quick filter pills to view letters by specific categories.

### 6. User Profile & Account Settings
- Personal profile page (`/profile/`) showcasing account age and lifetime letter statistics.
- Update personal information (First Name, Last Name, Email, and Reflection Bio).
- Secure password change form with automatic session re-authentication.

### 7. Printable Keepsake View
- "Print Keepsake" button on unlocked letters with custom `@media print` CSS.
- Automatically hides navbars, footers, and buttons for clean paper printing or PDF export.

---

## 🛠️ Technology Stack

| Component | Technology | Rationale |
|---|---|---|
| **Language** | Python 3.11+ | Clean syntax, wide ecosystem |
| **Framework** | Django 5.x | High-level web framework, batteries included |
| **ASGI Server** | Uvicorn | Blazing-fast ASGI web server implementation |
| **Database** | SQLite | Simple, zero configuration, portable |
| **Static Files** | WhiteNoise | Efficient static asset compression & serving |
| **Styling** | Bootstrap 5 + Custom CSS | Responsive layout, modern calm aesthetic |
| **Package Manager**| `uv` / `pip` | Fast, reliable dependency resolution |

---

## 📁 Project Architecture

```text
laternote/
├── config/                     # Core project configuration
│   ├── __init__.py
│   ├── asgi.py                 # ASGI entry point for Uvicorn
│   ├── settings.py             # Settings, WhiteNoise, templates, static config
│   ├── urls.py                 # Master URL configuration
│   └── wsgi.py                 # WSGI entry point
├── messages_app/               # Main application
│   ├── __init__.py
│   ├── admin.py                # Admin site registration
│   ├── apps.py                 # AppConfig
│   ├── forms.py                # RegisterForm, MessageCreateForm, Profile forms
│   ├── models.py               # Message & Profile models with dynamic methods
│   ├── tests.py                # 26 automated unit & integration tests
│   ├── urls.py                 # App URL endpoints
│   └── views.py                # Pure function-based views (FBVs)
├── templates/                  # Django HTML templates
│   ├── base.html               # Base layout with navbar, alerts, footer
│   ├── home.html               # Public landing page
│   ├── registration/
│   │   ├── change_password.html# Password update form
│   │   ├── login.html          # Login view
│   │   ├── profile.html        # User profile & stats
│   │   └── register.html       # Signup view
│   └── messages/
│       ├── create.html         # Create message form
│       ├── dashboard.html      # Stats, metrics, and upcoming unlocks
│       ├── detail.html         # Unlocked letter view with print action
│       ├── edit.html           # Edit title and content
│       ├── list.html           # Vault list with search & category filters
│       └── locked.html         # Locked view (never leaks content)
├── static/
│   └── css/
│       └── style.css           # Custom calm styling and @media print rules
├── main.py                     # Minimal deployment script for Render (Uvicorn)
├── render.yaml                 # Render Blueprint configuration
├── requirements.txt            # Production dependencies
├── pyproject.toml              # Project metadata & dependencies
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore rules
└── README.md                   # Project documentation
```

---

## 🚀 Local Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/laternote.git
cd laternote
```

### 2. Set up virtual environment & dependencies

#### Using `uv` (Recommended):
```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

#### Using standard `pip`:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Apply database migrations
```bash
python manage.py migrate
```

### 4. Create an admin superuser (Optional)
```bash
python manage.py createsuperuser
```

### 5. Run the local development server
```bash
python manage.py runserver
```
Open your browser at `http://127.0.0.1:8000/`.

---

## 🌐 Deploying to Render (in 3 Simple Steps!)

Deploying **LaterNote** to Render is completely streamlined using [`main.py`](file:///home/sarath-s/Desktop/Projects/Django/Note/main.py).

### How `main.py` works:
```python
# 1. Sets up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# 2. Applies database migrations automatically
call_command("migrate", interactive=False)

# 3. Collects & compresses static files for WhiteNoise
call_command("collectstatic", interactive=False)

# 4. Launches the production Uvicorn ASGI server on Render's $PORT
uvicorn.run("config.asgi:application", host="0.0.0.0", port=port)
```

### Step 1: Push your code to GitHub
Push this repository to your personal GitHub account:
```bash
git remote add origin https://github.com/your-username/laternote.git
git push -u origin main
```

### Step 2: Create a Web Service on Render
1. Log in to [Render](https://render.com/) and click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure the following fields:
   - **Name**: `laternote` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

### Step 3: Set Environment Variables on Render
Under **Environment Variables**, add:
- `SECRET_KEY`: `<generate-a-random-secure-string>`
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `.onrender.com`

Click **Deploy Web Service**! Render will install the dependencies, execute `main.py`, run migrations, collect static files, and serve your app with Uvicorn.

---

## 🧪 Automated Testing

LaterNote comes with a comprehensive suite of **26 automated unit and integration tests** testing models, forms, security, and views.

Run the test suite:
```bash
python manage.py test
```

### What is tested:
- ✅ **Dynamic Locking**: Confirms future dates (`> today`) are locked while today/past dates (`<= today`) are unlocked.
- ✅ **Form Validation**: Asserts past and today's dates are rejected during creation with clear error messages.
- ✅ **Zero Content Leaks**: Asserts that `message.content` is **never present** in the HTTP response of a locked message.
- ✅ **User Isolation**: Verifies User B cannot view, edit, or delete User A's messages (returns HTTP 404).
- ✅ **Unlock Date Immutability**: Editing a message updates title, category, and content, but preserves the original unlock date.
- ✅ **Profile Auto-Creation**: Tests that creating a `User` automatically creates a linked `Profile` via Django signals.
- ✅ **Password Management**: Verifies changing passwords via `PasswordChangeForm` and re-authenticating with the new credentials.
- ✅ **Search & Filter**: Tests querying messages by title substring and filtering by category.

---

## 💡 Architectural Decisions (Interview Cheatsheet)

1. **Why Function-Based Views (FBVs)?**
   - FBVs are explicit, clean, and beginner-readable. Request handling, validation, and authorization checks are visible at a glance without inheriting confusing magic from generic Class-Based Views.
2. **Why Not Use Celery or Background Workers?**
   - Scheduling background jobs for dates months or years away adds unnecessary infrastructure complexity (Redis, Celery, worker maintenance). By checking `unlock_date <= timezone.localdate()` at the moment of request, the application remains lightweight, highly reliable, and zero-maintenance.
3. **Why WhiteNoise with Uvicorn?**
   - WhiteNoise allows Python applications to serve their own static files directly and efficiently with Gzip/Brotli compression, eliminating the need to set up an external Nginx server or AWS S3 bucket for simple deployments.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
