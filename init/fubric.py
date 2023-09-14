from fabric import task
import os
import socket
import subprocess
import sys

script_path = os.path.abspath(__file__)
current_directory = os.path.dirname(script_path)
default_port = '54126'
print(current_directory)
domain = input('Please enter your domain if you have no domain and you want to run server on your ip\n please write ip: ')
if domain.lower() == 'ip':
    saved_domain = '127.0.0.1'
    print(saved_domain)
else:
    saved_domain = domain
    print(saved_domain)

result = subprocess.run(['netstat', '-tuln'], stdout=subprocess.PIPE, text=True)
if f':{default_port}' in result.stdout:
    print(f"Port {default_port} is already in use.\n You can change the port from the config file.")
    sys.exit(1)  # Exit the program with an error code

@task
def setup_environment(c):
    # Detect distribution
    issue_content = c.run("cat /etc/issue", hide=True).stdout.lower()

    # Install Python and pip based on distribution
    if "debian" in issue_content or "ubuntu" or 'Mint' or 'Debian' or 'Ubuntu' or 'mint' in issue_content:
        c.sudo("apt-get update && apt-get install -y python3 python3-pip nginx gunicorn")
        print("Installed in debian")
    elif "centos" in issue_content or "red hat" or 'CentOS' or 'Red hat' in issue_content:
        c.sudo("yum install -y python3 python3-pip nginx gunicorn")

    # Create and activate virtual environment
    setup_venv_command = f"cd {current_directory} && cd .. && cd panel && python3 -m venv venv && source venv/bin/activate"
    c.run(setup_venv_command)
    print('venv activated')

@task
def install_dependencies(c):
    install_commands = [
        f"cd {current_directory} && cd .. && cd panel",
        "pip3 install -r requirements.txt",
        "python3 manage.py makemigrations",
        "python3 manage.py migrate",
        "python3 manage.py createsuperuser"
    ]
    c.run(" && ".join(install_commands))
    print('packages installed')

@task
def setup_nginx_config(c):
    nginx_config = f'server {{\n' \
                   f'    listen 54126;\n' \
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
    print('nginx configed successfully')
    nginx_config_path = "/etc/nginx/sites-available/control_panel"
    c.run(f"echo '{nginx_config}' | sudo tee {nginx_config_path}")
    c.sudo(f"ln -s {nginx_config_path} /etc/nginx/sites-enabled")
    c.sudo("systemctl restart nginx")
    print('nginx restarted')

@task
def run_gunicorn(c):
    run_gunicorn_command = f"cd {current_directory} && cd .. && cd panel && gunicorn panel.wsgi:application -b 127.0.0.1:8000 --daemon"
    c.run(run_gunicorn_command)
    print('runned gunicorn')

@task
def success(c):
    if saved_domain == '127.0.0.1':
        success_domain = socket.gethostbyname(socket.gethostname())
    else:
        success_domain = saved_domain
    print(f'Panel installed successfully. Check http://{success_domain}:54126 in your browser')
