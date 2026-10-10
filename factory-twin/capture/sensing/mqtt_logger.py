"""MQTT → SQLite 로거 (Raspberry Pi). 토픽 kr/factory/sense/<node>/sensor/<name>/state 의 값을 1Hz로 저장.
실행: pip install paho-mqtt ; python3 mqtt_logger.py --broker 192.168.0.10 --db sense.db"""
import argparse, sqlite3, time, datetime
import paho.mqtt.client as mqtt

ap = argparse.ArgumentParser(); ap.add_argument("--broker", default="127.0.0.1"); ap.add_argument("--db", default="sense.db"); ap.add_argument("--prefix", default="kr/factory/sense/#")
a = ap.parse_args()
db = sqlite3.connect(a.db); db.execute("PRAGMA journal_mode=WAL"); db.execute("CREATE TABLE IF NOT EXISTS readings(ts_utc REAL, topic TEXT, value REAL)")
buf = []

def on_msg(c, u, m):
    try:
        v = float(m.payload.decode())
    except ValueError:
        return
    buf.append((time.time(), m.topic, v))
    if len(buf) >= 200:
        db.executemany("INSERT INTO readings VALUES (?,?,?)", buf); db.commit(); buf.clear()

cl = mqtt.Client(); cl.on_message = on_msg; cl.connect(a.broker); cl.subscribe(a.prefix)
print(datetime.datetime.now(), "logging", a.prefix, "->", a.db); cl.loop_forever()
