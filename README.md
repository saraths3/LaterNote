# LaterNote – Messages to Your Future Self

LaterNote is a thoughtful, clean, and beginner-friendly Django web application that allows users to write private letters to their future selves. Each message is sealed with a future unlock date and remains completely locked and hidden until that date arrives.

Built with Python, Django, SQLite, and Bootstrap 5, this project showcases clean Django conventions, function-based views, secure authentication, dynamic date-based status evaluation, and thoughtful UI design—ideal for a junior developer portfolio.

---

## 🌟 Main Features

- **User Authentication**:
  - Secure registration, login, and logout using Django's built-in authentication system.
  - Password validation following industry best practices.
  - Strict user isolation: users can only see, create, edit, or delete their own messages.

- **User Profile & Account Settings**:
  - Dedicated Profile page (`/profile/`) showcasing personal statistics (member since, total letters, sealed count, unlocked count).
  - Update first name, last name, email, and personal reflection bio.
  - Secure in-app password changes via Django's `PasswordChangeForm` and `update_session_auth_hash`.

- **Message Categories & Themes**:
  - Tag messages by category: `Personal`, `Career & Study`, `Goals & Aspirations`, `Reflections`, `Milestones & Memories`, and `Gratitude`.
  - Color-coded badges displayed on all message cards.

- **Search & Category Filtering**:
  - Live search bar in "My Messages" allowing quick keyword lookup by title.
  - Category pill filter to quickly view letters by theme.

- **Print Keepsake View**:
  - Clean printable layout for unlocked letters allowing users to print or save their time capsule notes as physical PDF keepsakes.

- **Create a Future Message**:
  - Simple form with message title, category, heartfelt content, and unlock date.
  - Form validation strictly ensures the unlock date is in the future.
  - Native HTML5 datepicker with automatic `min` date constraint.

- **Message Locking System**:
  - Dynamic evaluation: No scheduled jobs, Celery, or background workers are required. Status is determined dynamically by comparing the message's `unlock_date` against `timezone.localdate()`.
  - **Zero Leaks**: When a message is locked, its contents are **never rendered** in the HTML response. The locked view displays the title, unlock date, and remaining days countdown.
  - Once the unlock date arrives, the complete message content is beautifully revealed in a letter sheet.

- **My Messages Vault**:
  - Overview dividing notes into **Locked Messages** (with countdown badges) and **Unlocked Messages** (ready to read).

- **Edit & Delete**:
  - Users can update message titles, categories, and contents.
  - The unlock date remains immutable after creation to preserve the user's original commitment to time.
  - Message deletion is protected via CSRF and strictly executed via POST requests with a modal confirmation.

- **Dashboard**:
  - Overview cards displaying **Total Messages**, **Locked in Time**, and **Ready to Read**.
  - Timeline of upcoming unlock dates and quick links to recently unlocked letters.
  - Quick "+ Write New Message" call to action.

- **Calm & Minimal UI**:
  - Responsive design powered by Bootstrap 5, Bootstrap Icons, and custom CSS.
  - Soft neutral palette with calm amber badges for sealed messages and emerald badges for unlocked letters.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, Django 5.x
- **Database**: SQLite (built-in, zero external setup needed)
- **Frontend**: Django Template Language (DTL), HTML5, CSS3, Bootstrap 5, Bootstrap Icons
- **Forms & Auth**: Django ModelForms, built-in Authentication (`User`, `login`, `logout`)
- **Package Management**: [`uv`](https://github.com/astral-sh/uv) (fast Python package manager) or standard `pip`

---

## 📁 Project Structure

```text
LaterNote/
├── manage.py                   # Django management entry point
├── config/                     # Core project configuration
│   ├── __init__.py
│   ├── settings.py             # Settings, apps, templates, static config
│   ├── urls.py                 # Root URL routing
│   └── wsgi.py                 # WSGI application callable
├── messages_app/               # Main application
│   ├── __init__.py
│   ├── admin.py                # Django admin configuration
│   ├── apps.py                 # AppConfig
│   ├── forms.py                # RegisterForm, MessageCreateForm, MessageEditForm
│   ├── models.py               # Message model & dynamic lock methods
│   ├── tests.py                # 19 automated unit & integration tests
│   ├── urls.py                 # Application URL endpoints
│   └── views.py                # Function-based views
├── templates/                  # Django HTML templates
│   ├── base.html               # Base layout with navbar, alerts, footer
│   ├── home.html               # Public landing page
│   ├── registration/
│   │   ├── login.html          # Login page
│   │   └── register.html       # Signup page
│   └── messages/
│       ├── dashboard.html      # Metrics and upcoming unlocks
│       ├── create.html         # Form to write and seal a message
│       ├── list.html           # Vault list (Locked vs. Unlocked)
│       ├── locked.html         # Locked message view (content never exposed)
│       ├── detail.html         # Unlocked letter view with full content
│       └── edit.html           # Edit title and content
├── static/
│   └── css/
│       └── style.css           # Custom calm styling and card effects
├── pyproject.toml              # Project dependencies and metadata
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore rules
└── README.md                   # Project documentation
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.11 or higher
- `uv` (recommended) or `python3-venv`

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/laternote.git
cd laternote
```

### 3. Environment Setup

#### Option A: Using `uv` (Recommended)
```bash
# Create virtual environment and install dependencies
uv venv
uv pip install -r pyproject.toml
```

#### Option B: Using standard Python `venv`
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "django>=5.0,<6.0"
```

### 4. Configure Environment Variables (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 5. Run Database Migrations
```bash
# Apply initial migrations for auth, sessions, and messages_app
python manage.py migrate
```

### 6. (Optional) Create a Superuser
To access the Django admin panel at `/admin/`:
```bash
python manage.py createsuperuser
```

### 7. Start the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🧪 Running Automated Tests

LaterNote includes a comprehensive test suite (26 tests) covering models, forms, access control, user isolation, view logic, profile updates, password changes, category tagging, search filtering, and the security of locked messages.

Run tests using:
```bash
python manage.py test
```

### Test Coverage Highlights:
- **Locking Logic**: Verifies that messages scheduled for tomorrow or beyond are locked (`is_locked() == True`), while today's or past dates are unlocked.
- **Form Validation**: Confirms that past and current dates are rejected during creation with friendly error messages.
- **Security & Privacy**: Asserts that `message.content` is **never present** in the HTTP response of a locked message.
- **User Isolation**: Verifies that users cannot read, edit, or delete messages belonging to other users (returns `404 Not Found`).
- **Immutability of Unlock Date**: Verifies that editing a message updates title, category, and content, leaving the unlock date unchanged.
- **Profile & Account Management**: Verifies automatic Profile creation via signals, profile updates (names, email, bio), and in-app password changes.
- **Search & Category Filtering**: Tests title keyword search and category filtering in the message vault.

---

## 💡 Architectural Decisions (For Interviewers & Reviewers)

1. **Why Function-Based Views (FBVs)?**
   - FBVs are explicit, straightforward, and readable. They make the flow of request handling, authentication verification, and form validation obvious to anyone reading the code.
2. **Why No Background Jobs / Celery?**
   - Rather than introducing heavyweight queues, workers, and Redis, status is evaluated dynamically at query/render time:
     ```python
     def is_unlocked(self):
         return timezone.localdate() >= self.unlock_date
     ```
   - This keeps the system lightweight, resilient, and simple to host anywhere.
3. **Information Security on Locked Messages**:
   - Instead of hiding content with CSS or JavaScript, the template `messages/locked.html` does not include `{{ message.content }}` anywhere. A user inspecting the DOM or network response will never see the locked text.

---

## 📄 License
This project is open-source and available under the MIT License.
