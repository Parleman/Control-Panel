#!/bin/bash

source ./errors.sh

check_root
PYTHON_VERSION=$1

# check appname was supplied as argument
if [ "$PYTHON_VERSION" == "" ]; then
echo "Usage:"
echo "  $ install_os_prereq.sh [python-version]"
echo
echo "  Python version is 2 or 3 and defaults to 3 if not specified. Subversion"
echo "  of Python will be determined during runtime. The required Python version"
echo "  has to be installed and available globally."
echo
exit 1
fi

# Default python version to 3. OS has to have it installed.
if [ "$PYTHON_VERSION" == "" ]; then
PYTHON_VERSION=3
fi

if [ "$PYTHON_VERSION" != "3" -a "$PYTHON_VERSION" != "2" ]; then
error_exit "Invalid Python version specified. Acceptable values are 2 or 3 (default)"

echo "Please enter domain enter ip to set on server ip: "
read domain

if [ "$domain" = "ip" ]; then
    saved_domain=127.0.0.1
else
    saved_domain="$domain"
    echo "domain $saved_domain has been saved."
fi

# Install required packages
apt update
apt install -y python3 python3-pip python3-venv nginx gunicorn git
script_path="${BASH_SOURCE[0]}"
current_directory=$(dirname "$(readlink -f "$script_path")")
repository_url=git@github.com:Sinamzz/djangosocial.git
# Create and activate a virtual environment
python3 -m venv control_panel_venv
source control_panel_venv/bin/activate

# Install Django and required packages

# Clone your project repository
# mkdir control_panel
cd $current_directory
cd ..
# git init
# git pull git@github.com:Sinamzz/djangosocial.git master
python -m venv control_panel_venv
source control_panel_venv/bin/activate
# Install project dependencies
cd current_directory
cd ..
pip3 install -r panel/requirements.txt

# Apply migrations
cd $current_directory
cd ..
python3 panel/manage.py makemigrations
python3 panel/manage.py migrate

# Create a superuser
python3 panel/manage.py createsuperuser
# Configure Gunicorn systemd service
#sudo tee /etc/systemd/system/control_panel_gunicorn.service <<EOF
#[Unit]
#Description=gunicorn daemon for control_panel
#After=network.target

#[Service]
#Type=simple
#WorkingDirectory=$current_directory/control_panel/
#ExecStart=source $current_directory/control_panel_venv/bin/activate && gunicorn djangosocial.wsgi:application -b 127.0.0.1:8000

#[Install]
#WantedBy=multi-user.target
#EOF
# Start and enable Gunicorn service
#sudo systemctl start control_panel_gunicorn
#sudo systemctl enable control_panel_gunicorn

# Configure Nginx
sudo tee /etc/nginx/sites-available/control_panel <<EOF
server {

  server_name 127.0.0.1 $saved_domain;
  access_log /var/log/nginx/domain-access.log;

  location / {
    proxy_pass_header Server;
    proxy_set_header Host \$http_host;
    proxy_redirect off;
    proxy_set_header X-Forwarded-For  \$remote_addr;
    proxy_set_header X-Scheme \$scheme;
    proxy_connect_timeout 10;
    proxy_read_timeout 10;

    # This line is important as it tells nginx to channel all requests to port 8000.
    # We will later run our wsgi application on this port using gunicorn.
    proxy_pass http://127.0.0.1:8000/;
  }

}
EOF

# Create a symbolic link to enable the Nginx configuration
sudo ln -s /etc/nginx/sites-available/control_panel /etc/nginx/sites-enabled

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl daemon-reload
cd $current_directory
cd ..
cd panel
gunicorn panel.wsgi:application -b 127.0.0.1:8000 --daemon