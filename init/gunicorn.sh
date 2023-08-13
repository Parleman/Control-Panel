cd control_panel
gunicorn djangosocial.wsgi:application -b 127.0.0.1:8000 --pid /tmp/gunicorn.pid --daemon