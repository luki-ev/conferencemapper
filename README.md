Simple Jigasi ConferenceMapper with Redis, Flask and Gunicorn
=============================================================

Prerequisites: Redis, redis-py, flask, gunicorn

Packages for Ubuntu Server 18.04 & Debian 10

    apt install python3-flask gunicorn3 redis-server, python3-redis

Packages for Ubuntu Server 20.04

    apt install python3-flask gunicorn redis-server, python3-redis

Copy conferencemapper.service and conferencemapper.socket to /etc/systemd/system

Adapt /etc/systemd/system/conferencemapper.service to match path to conferencemapper.py

Add reverse proxy in front of gunicorn3 (nginx)

    location = /conferenceMapper {
        proxy_pass http://127.0.0.1:8001/conferenceMapper?$query_string;
    }

Start it and activate nginx config

    systemctl daemon-reload
    systemctl enable conferencemapper.socket
    systemctl start conferencemapper.socket
    systemctl reload nginx
