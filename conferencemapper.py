from flask import Flask, request, jsonify
import redis
import hashlib
import urllib
from datetime import timedelta

expire = timedelta(days=365)
digits = 6

app = Flask(__name__)
r = redis.Redis()


@app.route("/conferenceMapper")
def mapper():
    conference = request.args.get('conference')
    confid = request.args.get('id')

    if confid:
        try:
            confid = int(confid)
        except ValueError:
            confid = None
    
    if confid:
        conference = r.get(confid)
        
        if conference:
            return jsonify({
                "message": "Successfully retrieved conference mapping",
                "id": confid,
                "conference": conference.decode("utf-8")
            })
        else:
            return jsonify({
                "message": "No conference mapping was found",
                "id": confid,
                "conference": False
            })
    
    if conference:
        confid =int(hashlib.sha1(conference.encode("utf-8")).hexdigest(), 16) % 10**digits
        # jitsi internally uses urlencoded room names, so we need to store the conference name urlencoded as well
        # @ sign is stripped from room names, so we can add that to the list of safe characters, so that room@conference
        # stays intact
        encoded_conference = urllib.parse.quote(conference, safe='/@')
        if r.set(confid, encoded_conference) and r.expire(confid, expire):
            return jsonify({
                "message": "Successfully retrieved conference mapping",
                "id": confid,
                "conference": conference
            })
    
    return jsonify({
        "message": "No conference or id provided",
        "conference": False,
        "id": False
    })

if __name__ == '__main__':
    app.run(port=8001)
