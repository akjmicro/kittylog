import datetime
import sqlite3
from flask import g

from kittylog import app

DATABASE = "kittylog/kittylog.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def show_food(timestamp):
    cur = get_db().execute(
        """SELECT rowid, *
           FROM food
           WHERE timestamp BETWEEN
             date(?)
           AND
             date(?, '+1 day')
           ORDER BY time(timestamp) DESC;
        """,
        (timestamp, timestamp),
    )
    rv = cur.fetchall()
    cur.close()
    return rv


def show_food_sums(timestamp):
    cur = get_db().execute(
        """SELECT kitty,
                  sum(wet) as sum_wet,
                  sum(dry) as sum_dry,
                  sum(hairball) as sum_hairball,
                  sum(regular) as sum_regular
           FROM food
           WHERE timestamp > date(?)
           AND timestamp < date(?, '+1 day')
           GROUP BY kitty;
        """,
        (timestamp, timestamp),
    )
    rv = cur.fetchall()
    cur.close()
    return rv


def show_water(ts):
    cur = get_db().execute(
        """SELECT datetime(timestamp) as timestamp, human
           FROM water
           WHERE rowid = (
             SELECT max(rowid)
             FROM water
             WHERE date(timestamp) <= ?
           )
        """,
        (ts,),
    )
    rv = cur.fetchall()
    cur.close()
    return rv


def show_human_feeder_stats():
    cur = get_db().execute(
        """SELECT foodsum.human AS human,
                  (watersum.count + foodsum.count) AS count
           FROM (
             SELECT human, COUNT(human) AS count
             FROM food
             GROUP BY human
           ) AS foodsum
             JOIN (
               SELECT human, COUNT(human) AS count
               FROM water
               GROUP BY human
             ) AS watersum
             ON foodsum.human = watersum.human
           ORDER BY count desc;
        """
    )
    rv = cur.fetchall()
    cur.close()
    return rv


def get_wet_food_data(kitty):
    cur = get_db().execute(
        """SELECT date(timestamp) as date,
                  sum(wet) as sum_wet
           FROM food
           WHERE kitty=?
           AND timestamp >= date(current_timestamp, '-28 days')
           GROUP BY date
        """,
        (kitty,),
    )
    rv = cur.fetchall()
    cur.close()
    return rv


def get_dry_food_data(kitty):
    cur = get_db().execute(
        """SELECT date(timestamp) as date,
                  round(sum(dry) + (sum(regular) / 5.0)) as sum_dry
           FROM food
           WHERE kitty=?
           AND timestamp >= date(current_timestamp, '-28 days')
           GROUP BY date
        """,
        (kitty,),
    )
    rv = cur.fetchall()
    cur.close()
    return rv


def write_to_food_log(human, kitty, wet, dry, hairball, regular):
    timestamp = datetime.datetime.now().isoformat(" ").split('.')[0]
    cur = get_db().execute(
        """INSERT INTO food
           (timestamp, human, kitty, wet, dry, hairball, regular)
           VALUES(?,?,?,?,?,?,?);
        """,
        (timestamp, human, kitty, wet, dry, hairball, regular),
    )
    cur.connection.commit()
    cur.close()


def write_to_water_log(human):
    timestamp = datetime.datetime.now().isoformat(" ").split('.')[0]
    cur = get_db().execute(
        """INSERT INTO water
           (timestamp, human)
           VALUES(?,?);
        """,
        (timestamp, human),
    )
    cur.connection.commit()
    cur.close()


def delete_entry(rowid):
    cur = get_db().execute("""DELETE FROM food WHERE rowid=?;""", (rowid,))
    cur.connection.commit()
    cur.close()


def change_timestamp(rowid, hour, minute):
    cur = get_db().execute("""SELECT timestamp FROM food WHERE rowid=?;""", (rowid,))
    try:
        my_ts = cur.fetchone()["timestamp"]
    except:
        return
    the_day, the_time = my_ts.split()
    hr, mn, sec = the_time.split(":")
    new_time = the_day + " " + hour + ":" + minute + ":" + sec
    cur2 = get_db().execute(
        """UPDATE food SET timestamp=? WHERE rowid=?""", (new_time, rowid)
    )
    cur2.connection.commit()
    cur2.close()
    cur.close()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
