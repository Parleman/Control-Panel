#!/bin/bash


script_path="${BASH_SOURCE[0]}"
current_directory=$(dirname "$(readlink -f "$script_path")")

echo "Please enter domain enter ip to set on server ip: "
read domain

if [ "$domain" = "ip" ]; then
    saved_domain=127.0.0.1
else
    saved_domain="$domain"
    echo "domain $saved_domain has been saved."
fi

# Install required packages
if [ -f /etc/os-release ]; then
    source /etc/os-release
    if [[ "$ID" == "ubuntu" ]]; then
        sudo apt-get update
        sudo apt-get install -y nginx gunicorn python3 python3-pip python3-venv ufw

    if [[ "$ID" == "debian" ]]; then
        sudo apt-get update
        sudo apt-get install -y nginx gunicorn python3 python3-pip python3-venv ufw
    elif [[ "$ID" == "centos" ]]; then
        sudo yum update -y
        sudo yum install -y nginx gunicorn python3 python3-venv python3-pip ufw
    else
        echo "Only debian - centos - ubuntu supported."
        exit 1
    fi
else
    echo "Linux distro can not be identified"
    exit 1
fi
# repository_url=git@github.com:Sinamzz/djangosocial.git
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
cd $current_directory
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

  server_name 0.0.0.0 $saved_domain;
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