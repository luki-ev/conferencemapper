Simple Jigasi ConferenceMapper with Redis, Flask and Gunicorn
=============================================================

Prerequisites: Redis, redis-py, flask, gunicorn

Setup with Ubuntu Server 18.04+ (Debian 10+ works same)

    apt install python3-flask gunicorn3 redis-server, python3-redis

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
