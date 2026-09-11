# Context

- [Context](#context)
  - [Project Setup](#project-setup)
  - [Settings Configuration & Media Files](#settings-configuration--media-files)
  - [Custom User Model — With `user_type`](#custom-user-model--with-user_type)
  - [RecruiterProfileModel](#recruiterprofilemodel)
  - [SeekerProfileModel](#seekerprofilemodel)
  - [CategoryModel & JobPostModel](#categorymodel--jobpostmodel)
  - [ApplyJobModel](#applyjobmodel)
  - [Register Models In Admin](#register-models-in-admin)
  - [Database Migrations](#database-migrations)
  - [Create Superuser](#create-superuser)
  - [HTML Templates Setup](#html-templates-setup)
  - [Register Page — URL & View](#register-page--url--view)
  - [User Registration Form](#user-registration-form)
  - [Registration Form Template](#registration-form-template)
  - [Register View — Full Logic](#register-view--full-logic)
  - [Login View & Dashboard Page](#login-view--dashboard-page)
  - [Logout](#logout)
  - [Project Structure](#project-structure)
  - [Final Output](#final-output)

This README follows the actual **commit history** of the project (`Commits on Jul 18, 2026` and `Commits on Jul 19, 2026`) — every section below matches one real commit, in the same order they were built.

## Project Setup

- Create and activate a virtual environment

  ```sh
  python -m venv venv
  venv\Scripts\activate      # Windows
  source venv/bin/activate   # Linux/Mac
  ```

- Install Django and the packages used in this project

  ```sh
  pip install django crispy-forms crispy-bootstrap5 pillow
  ```

- Create the project and app

  ```sh
  django-admin startproject jobPortalProject
  cd jobPortalProject
  py manage.py startapp jobportal
  ```

- Register the app + crispy-forms in [settings.py](./jobPortalProject/settings.py)

  ```py
  INSTALLED_APPS = [
      'django.contrib.admin',
      'django.contrib.auth',
      'django.contrib.contenttypes',
      'django.contrib.sessions',
      'django.contrib.messages',
      'django.contrib.staticfiles',
      'jobportal',
      "crispy_forms",
      "crispy_bootstrap5",
  ]

  CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
  CRISPY_TEMPLATE_PACK = "bootstrap5"
  ```

---
[⬆️ Go to Context](#context)

## Settings Configuration & Media Files

- Since recruiters upload a company logo and seekers upload a profile image + resume, `MEDIA_URL` / `MEDIA_ROOT` are configured right at the start of the project (this project uses `ImageField` and `FileField`, so `Pillow` is required)

  ```py
  STATIC_URL = 'static/'
  STATIC_ROOT = BASE_DIR / 'staticfiles/'
  MEDIA_URL = '/media/'
  MEDIA_ROOT = BASE_DIR / 'media/'
  ```

- Media files are served in development by connecting them in the project's [urls.py](./jobPortalProject/urls.py)

  ```py
  from django.conf import settings
  from django.conf.urls.static import static

  urlpatterns = [
      path('admin/', admin.site.urls),
      path('', include('jobportal.urls')),
  ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  ```

> [!NOTE]
> Unlike the previous project (Calorie Counter) which wrapped this in `if settings.DEBUG:`, here it's appended directly with `+`. Functionally the same result while `DEBUG = True`, but it means this line would need to be guarded before deploying to production, otherwise Django tries to serve media files itself even in production (not recommended — a dedicated file/media server should handle that instead).

---
[⬆️ Go to Context](#context)

## Custom User Model — With `user_type`

- Just like the previous project, this app fully replaces Django's built-in `User` with a custom one via `AbstractUser` — but this time it also carries a `user_type` field, which is the field that decides whether someone is a **Recruiter** (job provider) or a **Seeker** (job applicant)
- Defined in [jobportal/models.py](./jobportal/models.py)

  ```py
  from django.db import models
  from django.contrib.auth.models import AbstractUser


  class User(AbstractUser):

      USER_TYPES = [
          ('Recruiter', 'Recruiter'),
          ('Seeker', 'Seeker'),
      ]

      display_name = models.CharField(max_length=200, null=True)
      user_type = models.CharField(choices=USER_TYPES, max_length=20, null=True)

      def __str__(self):
          return f'{self.username} - {self.user_type}'
  ```

- `display_name` is added on top of the default username, for showing a friendlier name in the UI
- `user_type` is what powers the whole "two kinds of accounts" system this portal is built around — every profile model below hooks into one or the other

> [!IMPORTANT]
> `AUTH_USER_MODEL = 'jobportal.User'` must be set in `settings.py` **before the first migration** — same rule as the Calorie Counter project. This is confirmed later in [settings.py](./jobPortalProject/settings.py):
> ```py
> AUTH_USER_MODEL = 'jobportal.User'
> LOGIN_URL = 'login_view'
> ```
> `LOGIN_URL` tells Django where to redirect a user if they hit a `@login_required` page while logged out.

---
[⬆️ Go to Context](#context)

## RecruiterProfileModel

- Extra profile info specifically for **Recruiter** accounts — company name, address, contact, logo
- `OneToOneField` to `User` → one recruiter account has exactly one company profile

  ```py
  class RecruiterProfileModel(models.Model):

      recruiter = models.OneToOneField(
          User,
          on_delete=models.CASCADE,
          related_name='recruiter_profile',
          null=True
      )
      company_name = models.CharField(max_length=200, null=True)
      address = models.TextField(null=True)
      contact = models.CharField(max_length=20, null=True)
      logo = models.ImageField(upload_to='company_logo', null=True)

      created_at = models.DateField(auto_now_add=True, null=True)
      updated_at = models.DateField(auto_now=True, null=True)

      def __str__(self):
          return f'{self.company_name}'
  ```

- `created_at` (`auto_now_add=True`) is stamped once, on creation. `updated_at` (`auto_now=True`) refreshes **every time** the record is saved — useful for showing "last updated" info later

---
[⬆️ Go to Context](#context)

## SeekerProfileModel

- Extra profile info specifically for **Seeker** (job applicant) accounts

  ```py
  class SeekerProfileModel(models.Model):

      seeker = models.OneToOneField(
          User,
          on_delete=models.CASCADE,
          related_name='seeker_profile',
          null=True
      )

      name = models.CharField(max_length=200, null=True)
      address = models.TextField(null=True)
      contact = models.CharField(max_length=20, null=True)
      profile_image = models.ImageField(upload_to='seeker_image', null=True)

      skills_set = models.TextField(null=True)

      created_at = models.DateField(auto_now_add=True, null=True)
      updated_at = models.DateField(auto_now=True, null=True)

      def __str__(self):
          return f'{self.name}'
  ```

- `skills_set` uses `TextField` instead of `CharField` — skills can be a long, free-form list, so there's no fixed max length

> [!NOTE]
> Two separate `OneToOneField` profile models (`RecruiterProfileModel`, `SeekerProfileModel`) both point back to the **same** `User` model, but only one of them will actually have data for any given user — whichever matches their `user_type`. This is a common pattern for "one login, multiple account types."

---
[⬆️ Go to Context](#context)

## CategoryModel & JobPostModel

- `CategoryModel` is a simple lookup table (e.g. "Web Development", "Marketing", "Design") used to categorize job posts

  ```py
  class CategoryModel(models.Model):
      name = models.CharField(max_length=200, null=True)

      def __str__(self):
          return f'{self.name}'
  ```

- `JobPostModel` is the core listing a Recruiter creates

  ```py
  class JobPostModel(models.Model):

      posted_by = models.ForeignKey(
          RecruiterProfileModel,
          on_delete=models.CASCADE,
          related_name='job_post_info',
          null=True
      )

      title = models.CharField(max_length=200, null=True)
      number_of_openings = models.PositiveIntegerField(null=True)
      category = models.ForeignKey(CategoryModel, on_delete=models.CASCADE, null=True)
      description = models.TextField(null=True)
      skills_set = models.TextField(null=True)
      deadline = models.DateField(null=True)
      salary = models.FloatField(null=True)

      created_at = models.DateField(auto_now_add=True, null=True)
      updated_at = models.DateField(auto_now=True, null=True)

      def __str__(self):
          return f'{self.title}'
  ```

- `posted_by` uses `ForeignKey` (not `OneToOne`) → **one recruiter can post many jobs**
- `category` also uses `ForeignKey` → many job posts can share the same category

---
[⬆️ Go to Context](#context)

## ApplyJobModel

- The "join table" connecting a **Seeker** to a **JobPostModel** they applied for — this is what actually records an application

  ```py
  class ApplyJobModel(models.Model):

      applied_by = models.ForeignKey(
          SeekerProfileModel,
          on_delete=models.CASCADE,
          related_name='applied_by_info',
          null=True
      )
      applied_job = models.ForeignKey(
          JobPostModel,
          on_delete=models.CASCADE,
          related_name='applied_job_info',
          null=True
      )
      resume = models.FileField(upload_to='seeker_resume', null=True)
      applied_at = models.DateField(auto_now_add=True, null=True)

      def __str__(self):
          return f'{self.applied_by.name}-{self.applied_job.title}'
  ```

- Both `applied_by` and `applied_job` are `ForeignKey`s → **one seeker can apply to many jobs**, and **one job post can receive many applications**
- `resume = models.FileField(...)` — different from `ImageField` used elsewhere, since a resume is usually a PDF/DOC file, not an image

---
[⬆️ Go to Context](#context)

## Register Models In Admin

- All 6 models registered together in [jobportal/admin.py](./jobportal/admin.py)

  ```py
  from django.contrib import admin
  from jobportal.models import *

  admin.site.register([
      User,
      RecruiterProfileModel,
      SeekerProfileModel,
      CategoryModel,
      JobPostModel,
      ApplyJobModel,
  ])
  ```

---
[⬆️ Go to Context](#context)

## Database Migrations

- With 6 models in place (`User`, `RecruiterProfileModel`, `SeekerProfileModel`, `CategoryModel`, `JobPostModel`, `ApplyJobModel`), migrations are generated and applied together

  ```sh
  py manage.py makemigrations
  py manage.py migrate
  ```

---
[⬆️ Go to Context](#context)

## Create Superuser

  ```sh
  py manage.py createsuperuser
  ```

- This admin account is used to log into `/admin/` and manually add `CategoryModel` entries (categories need to exist before recruiters can pick one for a job post)

---
[⬆️ Go to Context](#context)

## HTML Templates Setup

- A `master` template folder is created, following the same reusable-layout pattern as the Calorie Counter project

  ```txt
  📁 templates
  ├── 📁 master
  │   ├── 🌐 base.html          # root layout, navbar, Bootstrap CDN
  │   ├── 🌐 base-form.html      # shared layout for register + login forms
  │   ├── 🌐 nav.html             # navbar
  │   └── 🌐 messages.html        # flash/success messages block
  └── 🌐 dashboard.html
  ```

- [master/base.html](./jobportal/templates/master/base.html) — root layout, with both a `{% block title %}` (for the browser tab title) and a `{% block content %}` (for page content)

  ```html
  <!doctype html>
  <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>{% block title %}{% endblock title %}</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
      {% include 'master/nav.html' %}
      <div class="container mt-4">
        {% include 'master/messages.html' %}
      </div>
      <div class="container">
        {% block content %}{% endblock content %}
      </div>
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
    </body>
  </html>
  ```

- [master/nav.html](./jobportal/templates/master/nav.html) shows different links depending on `request.user.is_authenticated` — same pattern used in the Calorie Counter project

  ```html
  {% if request.user.is_authenticated %}
    <li class="nav-item"><a href="#">Home</a></li>
    <li class="nav-item"><a href="{% url 'logout_view' %}">logout</a></li>
  {% else %}
    <li class="nav-item"><a href="{% url 'login_view' %}">Login</a></li>
    <li class="nav-item"><a href="{% url 'register_view' %}">Register</a></li>
  {% endif %}
  ```

---
[⬆️ Go to Context](#context)

## Register Page — URL & View

- App-level routing in [jobportal/urls.py](./jobportal/urls.py)

  ```py
  from django.urls import path
  from jobportal.views import *

  urlpatterns = [
      path('register/', register_view, name='register_view'),
      path('login/', login_view, name='login_view'),
      path('logout/', logout_view, name='logout_view'),
      path('dashboard/', dashboard_view, name='dashboard_view'),
  ]
  ```

- Included in the project's [urls.py](./jobPortalProject/urls.py) via `include('jobportal.urls')` (shown earlier in [Settings Configuration & Media Files](#settings-configuration--media-files))

---
[⬆️ Go to Context](#context)

## User Registration Form

- Built by extending `UserCreationForm`, and includes the two custom fields (`display_name`, `user_type`) that were added to the `User` model
- In [jobportal/forms.py](./jobportal/forms.py)

  ```py
  from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
  from django import forms
  from jobportal.models import *


  class RegisterForm(UserCreationForm):
      class Meta:
          model = User
          fields = ['username', 'display_name', 'email', 'user_type', 'password1', 'password2']
  ```

- Because `user_type` uses `choices` on the model, this form automatically renders it as a dropdown (Recruiter / Seeker) — so at signup, the person picks which kind of account they want

---
[⬆️ Go to Context](#context)

## Registration Form Template

- Same reusable-form idea as the Calorie Counter project — **one** `base-form.html` handles Register, Login, and any future form, driven by variables passed through `context`
- [master/base-form.html](./jobportal/templates/master/base-form.html)

  ```html
  {% extends 'master/base.html' %}
  {% block title %}{{title}}{% endblock title %}

  {% block content %}
  {% load crispy_forms_tags %}

  <h3>{{form_title}}</h3>
  <form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{form_data|crispy}}
    <button type="submit" class="btn btn-primary">{{form_btn}}</button>
  </form>
  {% endblock content %}
  ```

- Note the extra `title` variable here (used for `{% block title %}`, the browser tab text) — on top of `form_title` and `form_btn` seen in the Calorie Counter project. One more piece of context, same reusable pattern.

---
[⬆️ Go to Context](#context)

## Register View — Full Logic

- In [jobportal/views.py](./jobportal/views.py)

  ```py
  def register_view(request):

      if request.method == 'POST':
          form_data = RegisterForm(request.POST)
          if form_data.is_valid():
              form_data.save()
              messages.success(request, 'User Creation Successfully.')
              return redirect('login_view')

      form_data = RegisterForm()

      context = {
          'form_data': form_data,
          'title': "Register Page",
          'form_title': 'User Registration Form',
          'form_btn': 'Register',
      }

      return render(request, 'master/base-form.html', context)
  ```

- Same GET/POST pattern seen in the Calorie Counter project: empty form on GET, validate + save + redirect on successful POST
- After successful registration, the new user is redirected to **login** (not automatically logged in) — they need to sign in with their new credentials next

---
[⬆️ Go to Context](#context)

## Login View & Dashboard Page

  ```py
  def login_view(request):

      if request.method == "POST":
          form_data = AuthenticationForm(request, request.POST)
          if form_data.is_valid():
              user = form_data.get_user()
              if user:
                  login(request, user)
                  messages.success(request, 'User Login Successfully.')
                  return redirect('dashboard_view')

          messages.error(request, 'Invalid Credentials.')

      form_data = AuthenticationForm()

      context = {
          'form_data': form_data,
          'title': "Login Page",
          'form_title': 'User Login Form',
          'form_btn': 'Login',
      }

      return render(request, 'master/base-form.html', context)
  ```

- Unlike the Calorie Counter project (which built a custom `LoginForm(AuthenticationForm): pass`), this view uses Django's built-in `AuthenticationForm` directly — functionally identical, just one less line of indirection
- Adds an explicit `messages.error(...)` branch for **invalid credentials**, which the earlier project didn't have — giving the user clearer feedback when login fails

- [dashboard_view](./jobportal/views.py) is protected with `@login_required` and greets the user

  ```py
  @login_required
  def dashboard_view(request):
      return render(request, 'dashboard.html')
  ```

- [dashboard.html](./jobportal/templates/dashboard.html)

  ```html
  {% extends 'master/base.html' %}
  {% block content %}
      <h3>Welcome to {{request.user.username}}</h3>
  {% endblock content %}
  ```

---
[⬆️ Go to Context](#context)

## Logout

  ```py
  @login_required
  def logout_view(request):
      logout(request)
      return redirect('login_view')
  ```

- Also protected with `@login_required` — only a currently logged-in user can trigger a logout
- Unlike the Calorie Counter project's logout, this one doesn't show a `messages.success(...)` banner — it just redirects straight to the login page

---
[⬆️ Go to Context](#context)

## Project Structure

```txt
jobPortalProject/
├── jobPortalProject/
│   ├── settings.py            # AUTH_USER_MODEL, MEDIA settings, crispy_forms
│   ├── urls.py                 # project-level routing + media static serving
│   ├── asgi.py
│   └── wsgi.py
├── jobportal/
│   ├── models.py                 # User, RecruiterProfileModel, SeekerProfileModel,
│   │                              #  CategoryModel, JobPostModel, ApplyJobModel
│   ├── admin.py                    # all 6 models registered
│   ├── forms.py                      # RegisterForm
│   ├── views.py                       # register_view, login_view,
│   │                                   #  dashboard_view, logout_view
│   ├── urls.py                          # app-level routing
│   ├── migrations/
│   └── templates/
│       ├── master/
│       │   ├── base.html
│       │   ├── base-form.html
│       │   ├── nav.html
│       │   └── messages.html
│       └── dashboard.html
├── media/
│   ├── company_logo/
│   ├── seeker_image/
│   └── seeker_resume/
├── db.sqlite3
└── manage.py
```

---
[⬆️ Go to Context](#context)

## Final Output

- `http://127.0.0.1:8000/register/` → Registration page — pick `Recruiter` or `Seeker` as account type
- `http://127.0.0.1:8000/login/` → Login page
- `http://127.0.0.1:8000/dashboard/` → Welcome dashboard (protected, requires login)
- `http://127.0.0.1:8000/logout/` → Logs the user out, redirects to login
- `http://127.0.0.1:8000/admin/` → Admin panel — manage all 6 models, including adding `CategoryModel` entries

**Flow so far:** Register (choose Recruiter/Seeker) → redirected to Login → Login → Dashboard → Logout

> [!NOTE]
> As of the latest commit (`logout done`), the core authentication system and all data models are complete, but the actual **job posting**, **browsing**, and **apply-to-job** pages/views haven't been built yet — the models (`JobPostModel`, `ApplyJobModel`) are ready in the database, waiting for their views and templates in a future commit.

---
[⬆️ Go to Context](#context)
