import sys
from fabric import task
import os
import socket

script_path = os.path.abspath(__file__)
current_directory = os.path.dirname(script_path)
print(current_directory)
domain = input('Please enter your domain if you have no domain and you want to run server on your ip pls write ip')
if domain.lower() == 'ip':
    saved_domain = '127.0.0.1'
    print(saved_domain)
else:
    saved_domain = domain
    print(saved_domain)


@task
def setup_environment(c):
    # Detect distribution
    issue_content = c.run("cat /etc/issue", hide=True).stdout.lower()

    # Install Python and pip based on distribution
    if "debian" in issue_content or "ubuntu" in issue_content:
        c.sudo("apt-get update && apt-get install -y python3 python3-pip nginx gunicorn")
    elif "centos" in issue_content or "red hat" in issue_content:
        c.sudo("yum install -y python3 python3-pip nginx gunicorn")

    # Create and activate virtual environment
    c.run(f"cd {current_directory}")
    c.run("cd ..")
    c.run("cd panel")
    c.run("python3 -m venv venv")
    c.run("source venv/bin/activate")


@task
def install_dependencies(c):
    c.run(f"cd {current_directory}")
    c.run("cd ..")
    c.run("cd panel")
    c.run("pip3 install -r requirements.txt")
    c.run("python3 manage.py makemigrations")
    c.run("python3 manage.py migrate")
    c.run("python3 manage.py createsuperuser")


@task
def setup_nginx_config(c):
    # Create Nginx config file
    c.run("touch /etc/nginx/sites-available/control_panel")
    nginx_config = f'server {{\n' \
                   f'listen 54126;' \
                   f'    server_name 0.0.0.0 {saved_domain};\n' \
                   f'    access_log /var/log/nginx/domain-access.log;\n' \
                   f'\n' \
                   f'    location / {{\n' \
                   f'        proxy_pass_header Server;\n' \
                   f'        proxy_set_header Host $http_host;\n' \
                   f'        proxy_redirect off;\n' \
                   f'        proxy_set_header X-Forwarded-For  $remote_addr;\n' \
                   f'        proxy_set_header X-Scheme $scheme;\n' \
                   f'        proxy_connect_timeout 10;\n' \
                   f'        proxy_read_timeout 10;\n' \
                   f'        proxy_pass http://127.0.0.1:8000/;\n' \
                   f'    }}\n' \
                   f'}}'
    print(nginx_config)
    c.run(f"echo {nginx_config} >> /etc/nginx/sites-available/control_panel")

    # Create symbolic link
    c.sudo("ln -s /etc/nginx/sites-available/control_panel /etc/nginx/sites-enabled")

    # Restart Nginx
    c.sudo("systemctl restart nginx")


@task
def run_gunicorn(c):
    # Run Gunicorn
    c.run(f"cd {current_directory}")
    c.run("cd ..")
    c.run("cd panel")
    c.run("gunicorn panel.wsgi:application -b 127.0.0.1:8000 --daemon")


@task
def success(c):
    if saved_domain == '127.0.0.1':
        success_domain = socket.gethostbyname(socket.gethostname())
    else:
        success_domain = saved_domain
    print(f'Panel installed successfully check {success_domain}:54126 in your browser')
