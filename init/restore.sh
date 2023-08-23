sudo rm -rf /etc/nginx/sites-available/control_panel
sudo rm -rf /etc/nginx/sites-enabled/control_panel
sudo netstat -ntulp | grep 8000
echo "kill <pid>"