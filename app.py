from flask import Flask
from flask_apscheduler import APScheduler
import gunicorn
import eventlet

app = Flask(__name__)
scheduler = APScheduler()

class Config:
    SCHEDULER_API_ENABLED = True
app.config.from_object(Config)

@app.get('/')
def index():
    return "HELLO WORLD"

cnt = 0
job_id = "job0"

@scheduler.task("interval", id=job_id, seconds=1, misfire_grace_time=900)
def job0():
    global cnt
    print(f"CNT: {cnt}")
    cnt += 1
print("STARTING SCHEDULER")
scheduler.start()

if __name__ == "__main__":
    app.run()

print(gunicorn, eventlet)