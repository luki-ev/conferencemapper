Simple Jigasi ConferenceMapper with Redis, Flask and Gunicorn
=============================================================

This implements the /conferenceMapper part of https://github.com/jitsi/jitsi-meet/blob/master/resources/cloud-api.swagger

Prerequisites: Redis, redis-py, flask and a wsgi server like gunicorn

Packages for Ubuntu Server 20.04

    apt install python3-flask gunicorn redis-server, python3-redis

Copy conferencemapper.service and conferencemapper.socket to /etc/systemd/system

Adapt /etc/systemd/system/conferencemapper.service to match WorkingDirectory to conferencemapper module directory.

Add reverse proxy in front of gunicorn (nginx)

    location = /conferenceMapper {
        proxy_pass http://127.0.0.1:8001/conferenceMapper?$query_string;
    }

Start it and activate nginx config

    systemctl daemon-reload
    systemctl enable conferencemapper.socket
    systemctl start conferencemapper.socket
    systemctl reload nginx
