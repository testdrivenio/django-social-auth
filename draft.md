# Adding Social Authentication to Django

This tutorial looks at how to add social auth (also known as social login, social signon, or OAuth) to a Django application with [Django Allauth](https://github.com/pennersr/django-allauth). You'll also configure GitHub and Twitter auth as well as regular auth with username and password.

> Social login is a form of single sign-on using existing information from a social networking service such as Facebook, Twitter or Google, to sign in to a third-party website instead of creating a new login account specifically for that website. It is designed to simplify logins for end-users and provide more reliable demographic information to web developers. - [Wikipedia](https://en.wikipedia.org/wiki/Social_login)

Using a social auth has its advantages. You won't need to set up auth for the web application, since it's handled by the third-party, [OAuth provider](https://en.wikipedia.org/wiki/List_of_OAuth_providers). Also, since providers like Google, Facebook, and GitHub perform extensive checks to prevent unauthorized access to their services, leveraging social auth instead of rolling your own auth mechanism can boost your application's security.

TODO: for michael (re-record demo app)

## Why OAuth?

Why would you want to leverage OAuth over rolling your own auth?

**Pros**:

1. Improved security.
1. Easier and faster log-in flows since there's no need to create and remember a username or password.
1. In case of a security breach, no third-party damage will occur, as the authentication is passwordless.

**Cons**:

1. Your application now depends on another app outside of your control. If the provider is down, users won't be able to log in.
1. People often tend to ignore the permissions requested by OAuth providers.
1. Users that don't have accounts on one of the providers that you have configured won't be able to access your application. The best approach is to implement both -- e.g., username and password and social auth -- and let the user choose.

TODO: can you add just a brief not about what OAuth is and how it relates to social auth?
TODO: move the social auth flow here, along with the image

## Django Allauth vs. Python Social Auth

[Django Allauth](https://github.com/pennersr/django-allauth) and [Python Social Auth](https://python-social-auth.readthedocs.io/en/latest/) are the two most popular packages for implementing social authentication in Django. Which one should you use?

### Django Allauth

**Pros**:

1. Django Allauth is one of the most popular Django packages.
1. It supports over 50 authentication providers (i.e., GitHub, Twitter, Google).
1. Along with social auth, it also provides regular auth with username and password.
1. Django Allauth makes it easy to customize the forms used during the auth flow.

**Cons**:

1. Despite the package's popularity, the documentation is poorly structured and not meant for beginners.
1. There's quite a bit of initial setup required to register an OAuth provider, which can be difficult for beginners.
1. There's 250+ issues on GitHub (as of writing).

### Python Social Auth

**Pros**:

1. Python Social Auth provides support for several Python web frameworks like Django, Flask, Webpy, Pyramid, and Tornado.
1. It supports almost 50 OAuth providers.
1. It supports the Django ORM and [MongoEngine](http://mongoengine.org/) ODM
1. It provides a storage interface to allow users to add more ORMs.

    > For example, to see how the storage interface is used to work with the SQLAlchemy ORM, review the code [here](https://github.com/python-social-auth/social-storage-sqlalchemy/blob/1.1.0/social_sqlalchemy/storage.py). Check out the [official documentation](https://python-social-auth.readthedocs.io/en/latest/storage.html#storage-interface) for more on how to use the storage interface.

**Cons**:

1. The documentation is a bit simpler, but it could still use some work with regard to the organization.
1. Again, there's quite a bit of initial setup required to register an OAuth provider, which can be difficult for beginners.
1. There's close to 100 open issues on GitHub (as of writing).

<br>

Both packages have their ups and downs. However, this tutorial focuses on Django Allauth as it's much more popular and supports social auth and regular auth via username and password.

## Django Setup

Let's create a new Django project and configure Django Allauth.

### Create a new Django project

Start by creating a virtual environment and installing Django:

```bash
$ mkdir django-social-auth && cd django-social-auth
$ python3.9 -m venv .venv
$ source .venv/bin/activate
(.venv)$ pip install Django==3.1.5
```

> Feel free to swap out venv and Pip for [Poetry](https://python-poetry.org/) or [Pipenv](https://pipenv.pypa.io/). For more, review [Modern Python Environments](/blog/python-environments/).

Now create a new project, apply the migrations, and run the server:

```bash
(.venv)$ django-admin startproject social_app .
(.venv)$ python manage.py migrate
(.venv)$ python manage.py runserver
```

Navigate to [http://http://127.0.0.1:8000](http://http://127.0.0.1:8000). You should see the following screen:

<img data-src="/static/images/blog/django-social-auth/django_landing.png"  loading="lazy" class="lazyload" style="max-width:100%;" alt="django landing page">

### Configure Django Allauth

Next, let's set up Django Allauth for our Django app.

```bash
(.venv)$ pip install django-allauth==0.44.0
```

For Django Allauth to work with our django app, update `INSTALLED_APPS` inside the *settings.py* file like so:

```python
# social_app/settings.py

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # new
    # 3rd party
    "allauth", # new
    "allauth.account", # new
    "allauth.socialaccount", # new
    # social providers
    "allauth.socialaccount.providers.github", # new
    "allauth.socialaccount.providers.twitter", # new
]
```

First, we added the [Django "sites" framework](https://docs.djangoproject.com/en/3.1/ref/contrib/sites/), which is required for Allauth to work properly. We then added the core Allauth apps: `allauth`, `allauth.account`, and `allauth.socialaccount`.

Now add the following to the bottom of *settings.py*:

```python
# social_app/settings.py

AUTHENTICATION_BACKENDS = (
    "allauth.account.auth_backends.AuthenticationBackend",
)

SITE_ID = 1
ACCOUNT_EMAIL_VERIFICATION = "none"
LOGIN_REDIRECT_URL = "home"
ACCOUNT_LOGOUT_ON_GET = True
```

Here, we defined the following:

- We added `allauth` as the authentication backend. All logging in and out (via OAuth or regular username and password) will now be handled by Allauth.
- `SITE_ID`, which is required for Django Allauth to function.
- `ACCOUNT_EMAIL_VERIFICATION = "none"` turns off verification emails. Django automatically sets up an email verification workflow. We do not need this functionality right now.
- `LOGIN_REDIRECT_URL = "home"` redirects the user to the homepage after a successful login.
- `ACCOUNT_LOGOUT_ON_GET = True` directly logs the user out when the logout button is clicked via a GET request. This skips the [confirm logout page](https://django-allauth.readthedocs.io/en/latest/views.html#logout-account-logout).

Update the *urls.py* to include Django Allauth:

```python
from django.contrib import admin
from django.urls import path, include # new


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")), # new
]
```

Apply the migration files associated with Django Allauth:

```bash
(.venv)$ python manage.py migrate
```

> Migrations are important here since a number of new tables are required by Allauth. Don't forget this step!

Create a superuser:

```bash
(.venv)$ python manage.py createsuperuser
```

### Templates

Create a new folder called "templates", and add two files to it called *_base.html* and *home.html*:

```bash
(.venv)$ mkdir templates && cd templates
(.venv)$ touch _base.html home.html
```

Update `TEMPLATES` in *settings* so that Django knows where to find the templates:

```python
# social_app/settings.py

TEMPLATES = [
    {
        ...
        "DIRS": [str(BASE_DIR.joinpath("templates"))],
        ...
    },
]
```

*templates/_base.html*:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
    <link
      rel="stylesheet"
      href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"
    />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Django Social Login</title>
  </head>
  <body>
    {% block content %} {% endblock content %}
  </body>
</html>
```

*templates/home.html*

```html
{% extends '_base.html' %} {% load socialaccount %}

{% block content %}

<div class="container" style="text-align: center; padding-top: 10%;">
  <h1>Django Social Login</h1>

  <br /><br />

  {% if user.is_authenticated %}
    <h3>Welcome {{ user.username }} !!!</h3>
    <br /><br />
    <a href="{% url 'account_logout' %}" class="btn btn-danger">Logout</a>
  {% endif %}
</div>

{% endblock content %}
```

TODO: what does `{% load socialaccount %}` do?

Create a view to serve up the *home.html* template:

```python
# social_app/views.py

from django.views.generic import TemplateView


class Home(TemplateView):
    template_name = "home.html"
```

Add the new URL:

```python
# social_app/urls.py

from django.contrib import admin
from django.urls import path, include

from .views import Home # new


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", Home.as_view(), name="home"), # new
]
```

That's it! Django Allauth is configured and ready to test. Run the server. Navigate to [http://http://127.0.0.1:8000/accounts/login/](http://http://127.0.0.1:8000/accounts/login/). Make sure you can log in with your superuser credentials.

TODO: can you provide a link to a resource for customizing the forms?

## GitHub Provider

Now that both the Django and Django Allauth are ready let's wire up our first social auth provider -- GitHub.

### App

First, we need to create an OAuth app and get the OAuth keys from GitHub. Log in to your GitHub account, and then navigate to [https://github.com/settings/applications/new](https://github.com/settings/applications/new) to create a new [OAuth application](https://docs.github.com/en/free-pro-team@latest/developers/apps/authorizing-oauth-apps):

```text
Application name: Testing Django Allauth
Homepage URL: http://127.0.0.1:8000
Callback URL: http://127.0.0.1:8000/accounts/github/login/callback
```

<img data-src="/static/images/blog/django-social-auth/register_github_oauth_app.png"  loading="lazy" class="lazyload" style="max-width:100%;" alt="register github oauth app">

Click "Register application". You'll be redirected to your app. Take note of the Client ID and Client Secret:

<img data-src="/static/images/blog/django-social-auth/github_oauth_app.png"  loading="lazy" class="lazyload" style="max-width:100%;" alt="github oauth ap">

> If a Client Secret wasn't generated, click "Generate a new client secret".

Next, we need to add the GitHub provider in the Django admin panel.

Run the server:

```bash
(.venv)$ python manage.py runserver
```

Log in to the admin at [http://http://127.0.0.1:8000/admin](http://http://127.0.0.1:8000/admin). Then, under "Social applications", click "Add Social Application":

- Choose GitHub as the Provider
- Add a name
- Add the Client ID and Client Secret (to Secret key) obtained earlier
- Add example.com as one of the Chosen Sites

<img data-src="/static/images/blog/django-social-auth/django_admin_github.png"  loading="lazy" class="lazyload" style="max-width:100%;" alt="django admin github oauth provider setup">

We've successfully integrated GitHub as a social auth provider. With that, let's update the *templates/home.html* template to test it out:

```html
{% extends '_base.html' %} {% load socialaccount %}

{% block content %}

<div class="container" style="text-align: center; padding-top: 10%;">
  <h1>Django Social Login</h1>

  <br /><br />

  {% if user.is_authenticated %}
    <h3>Welcome {{ user.username }} !!!</h3>
    <br /><br />
    <a href="{% url 'account_logout' %}" class="btn btn-danger">Logout</a>
  {% else %}
    <!-- GitHub button starts here -->
    <a href="{% provider_login_url 'github' %}" class="btn btn-secondary">
      <i class="fa fa-github fa-fw"></i>
      <span>Login with GitHub</span>
    </a>
    <!-- GitHub button ends here -->
  {% endif %}
</div>

{% endblock content %}
```

Run the app. You should now be able to log in via GitHub.

<img data-src="/static/images/blog/django-social-auth/django_github_social_auth.png"  loading="lazy" class="lazyload" style="max-width:100%;" alt="django github social auth">

After logging in, you should see the user at [http://http://127.0.0.1:8000/admin/auth/user/](http://http://127.0.0.1:8000/admin/auth/user/) as well as the associated social account at [http://127.0.0.1:8000/admin/socialaccount/socialaccount/](http://127.0.0.1:8000/admin/socialaccount/socialaccount/). If you view the social account, you'll see all the public data associated with the GitHub account. This data can be used for your user profile on Django. It's recommended to use a custom [User Model](https://docs.djangoproject.com/en/3.1/ref/contrib/auth/#user-model) for this. For more, review [Creating a Custom User Model in Django](/blog/django-custom-user-model/).

## Twitter Provider

Setting up the Twitter provider is similar to GitHub:

1. Create an OAuth app on Twitter
1. Register the provider in the Django admin
1. Update the *home.html* template

Start by [applying](https://developer.twitter.com/en/portal/dashboard) for a Twitter developer account. Once created, navigate to [Projects and Apps](https://developer.twitter.com/en/portal/projects-and-apps) and click "Create App".

Give the app a name, and take note of the API key and API secret key. Then, under "Authentication Settings". Enable "Enable 3-legged OAuth" and "Request email address from users". Add the Callback, Website, Terms of service, and Privacy policy URLs as well:

```text
Callback URL: http://127.0.0.1:8000/accounts/twitter/login/callback
Website URL: http://example.com
Terms of service: http://example.com
Privacy policy: http://example.com
```

<img data-src="/static/images/blog/django-social-auth/register_twitter_oauth_app.png"  loading="lazy" class="lazyload" style="max-width:100%;" alt="register twitter oauth app">

Let's add the provider in the Django Admin.

Run the server:

```bash
(.venv)$ python manage.py runserver
```

Log in to the admin at [http://http://127.0.0.1:8000/admin](http://http://127.0.0.1:8000/admin). Then, under "Social applications", click "Add Social Application":

- Choose Twitter as the Provider
- Add a name
- Add the API key (to Client id) and and API secret key (to Secret key) obtained earlier
- Add example.com as one of the Chosen Sites

<img data-src="/static/images/blog/django-social-auth/django_admin_twitter.png"  loading="lazy" class="lazyload" style="max-width:100%;" alt="django admin twitter oauth provider setup">

> Remember to safeguard your API keys and tokens.

Finally, add a "Login with Twitter" button to *templates/home.html*:

```html
{% extends '_base.html' %} {% load socialaccount %}

{% block content %}

<div class="container" style="text-align: center; padding-top: 10%;">
  <h1>Django Social Login</h1>

  <br /><br />

  {% if user.is_authenticated %}
    <h3>Welcome {{ user.username }} !!!</h3>
    <br /><br />
    <a href="{% url 'account_logout' %}" class="btn btn-danger">Logout</a>
  {% else %}

    ...

    <!-- Twitter button starts here -->
      </a>
      <a href="{% provider_login_url 'twitter' %}" class="btn btn-primary">
        <i class="fa fa-twitter fa-fw"></i>
        <span>Login with Twitter</span>
      </a>
    <!-- Twitter button ends here -->
  {% endif %}
</div>

{% endblock content %}
```

Navigate to [http://http://127.0.0.1:8000](http://http://127.0.0.1:8000) to test out the auth workflow.

## Conclusion

This tutorial detailed how to set up social auth with Django and Django Allauth. You should now have a solid understanding of how to wire up new social auth providers:

1. Add the appropriate Allauth app to `INSTALLED_APPS` in the settings file
1. Create an OAuth app on the provider's developer site and take note of the tokens/keys/secret
1. Register the app in the Django Admin
1. Add the URL to the template

Although this tutorial focused on Django Allauth, it doesn't necessarily mean it should be used over Python Social Auth in every scenario. Explore both packages. Try implementing custom forms and linking multiple social accounts.
