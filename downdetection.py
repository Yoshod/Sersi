from flask import Flask, Request
from threading import Thread


app = Flask('')


@app.route('/')
def home():
    return ("Hello World!")


def run():
    app.run(host="0.0.0.0", port=8074)


def down_detection():
    t = Thread(target=run)
    t.start()
    print(Request.host)
