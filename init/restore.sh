rm -rf /etc/nginx/sites-available/control_panel
rm -rf /etc/nginx/sites-enabled/control_panel
netstat -ntulp | grep 8000
echo "kill <pid>"