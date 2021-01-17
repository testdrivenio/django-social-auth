# Adding Social Authentication to Django

## Want to learn how to build this?

Check out the [post](https://testdriven.io/blog/django-social-auth/).

## Want to use this project?

1. Fork/Clone

1. Create and activate a virtual environment:

    ```sh
    $ python3 -m venv venv && source venv/bin/activate
    ```

1. Install the requirements:

    ```sh
    (venv)$ pip install -r requirements.txt
    ```

1. Apply the migrations and create a superuser:

    ```sh
    (venv)$ python manage.py migrate
    (venv)$ python manage.py createsuperuser
    ```

1. Create OAuth apps on GitHub and Twitter.

1. Register the providers in the Django admin.

1. Run the server:

    ```sh
    (venv)$ python manage.py runserver
    ```
