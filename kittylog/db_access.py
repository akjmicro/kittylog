import datetime
import sqlite3
from flask import g

from kittylog import app

DATABASE = 'kittylog/kittylog.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory= sqlite3.Row
    return db


def show_log(timestamp):
    cur = get_db().execute(
        """SELECT rowid, *
           FROM food
           WHERE timestamp > date(?)
           AND timestamp < date(?, '+1 day')
           ORDER BY timestamp desc, kitty DESC;
        """, (timestamp, timestamp,)
    )
    rv = cur.fetchall()
    cur.close()
    return rv


def show_sums(timestamp):
    cur = get_db().execute(
        """SELECT kitty,
                  sum(wet) as sum_wet,
                  sum(dry) as sum_dry,
                  sum(hairball) as sum_hairball,
                  sum(treats) as sum_treats
           FROM food
           WHERE timestamp > date(?)
           AND timestamp < date(?, '+1 day')
           GROUP BY kitty;
        """, (timestamp, timestamp,)
    )
    rv = cur.fetchall()
    cur.close()
    return rv


def show_water(timestamp):
    cur = get_db().execute(
        """SELECT datetime(timestamp) as timestamp, feeder
           FROM water
           WHERE rowid = (
             SELECT max(rowid)
             FROM water
             WHERE date(timestamp) <= ?
           )
        """, (timestamp,)
    )
    rv = cur.fetchall()
    cur.close()
    return rv


def write_to_food_log(feeder, kitty, wet, dry, hairball, treats):
    timestamp = datetime.datetime.now().isoformat(' ')
    cur = get_db().execute(
        """INSERT INTO food
           (timestamp, feeder, kitty, wet, dry, hairball, treats)
           VALUES(?,?,?,?,?,?,?);
        """, (timestamp, feeder, kitty, wet, dry, hairball, treats)
    )
    cur.connection.commit()
    cur.close()


def write_to_water_log(feeder):
    timestamp = datetime.datetime.now().isoformat(' ')
    cur = get_db().execute(
        """INSERT INTO water
           (timestamp, feeder)
           VALUES(?,?);
        """, (timestamp, feeder)
    )
    cur.connection.commit()
    cur.close()


def delete_entry(rowid):
    cur = get_db().execute(
        """DELETE FROM food WHERE rowid=?;""", (rowid,)
    )
    cur.connection.commit()
    cur.close()


def change_timestamp(rowid, hour, minute):
    cur = get_db().execute(
        """SELECT timestamp FROM food WHERE rowid=?;""", (rowid,)
    )
    try:
        my_ts = cur.fetchone()['timestamp']
    except:
        return
    the_day, the_time = my_ts.split()
    hr, mn, sec = the_time.split(':')
    new_time = the_day + ' ' + hour + ':' + minute + ':' + sec
    cur2 = get_db().execute(
        """UPDATE food SET timestamp=? WHERE rowid=?""", (new_time, rowid,)
    )
    cur2.connection.commit()
    cur2.close()
    cur.close()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
