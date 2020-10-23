import datetime
import pysqlite3 as sqlite3
from flask import g

from kittylog import app, config

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
           WHERE date(timestamp) = date(?)
           ORDER BY time(timestamp) DESC;
        """,
        (timestamp,),
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
           WHERE date(timestamp) = date(?)
           GROUP BY kitty;
        """,
        (timestamp,),
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


def get_calorie_data(kitty, offset=0):
    offset_min = (offset + 1) * -28
    offset_max = offset * -28
    nutrition = config["nutrition"]
    dry_factor = nutrition["dry"]
    wet_factor = nutrition["wet"]
    hairball_factor = nutrition["hairball"]
    regular_factor = nutrition["regular"]
    cur = get_db().execute(
        f"""SELECT date(timestamp) as date,
                   (sum(dry) * {dry_factor}
                   + sum(wet) * {wet_factor}
                   + sum(hairball) * {hairball_factor}
                   + sum(regular) * {regular_factor}) as calories
           FROM food
           WHERE kitty=?
           AND date(timestamp) BETWEEN
             date(current_timestamp, '{offset_min} days')
             AND
             date(current_timestamp, '{offset_max} days')
           GROUP BY date
        """,
        (kitty,),
    )
    rv = cur.fetchall()
    cur.close()
    return rv


def get_calorie_moving_average_data(kitty, offset=0):
    offset_min = (offset + 1) * -28
    offset_max = offset * -28
    nutrition = config["nutrition"]
    dry_factor = nutrition["dry"]
    wet_factor = nutrition["wet"]
    hairball_factor = nutrition["hairball"]
    regular_factor = nutrition["regular"]
    cur = get_db().execute(
        f"""SELECT inner.date, AVG(inner.calories)
              OVER (ORDER BY date ASC ROWS 3 PRECEDING) AS moving_avg_7
           FROM
           (
               SELECT date(timestamp) as date,
                       (sum(dry) * {dry_factor}
                       + sum(wet) * {wet_factor}
                       + sum(hairball) * {hairball_factor}
                       + sum(regular) * {regular_factor}) as calories
               FROM food
               WHERE kitty=?
               AND date(timestamp) BETWEEN
                 date(current_timestamp, '{offset_min - 6} days')
                 AND
                 date(current_timestamp, '{offset_max} days')
               GROUP BY date
           ) AS inner
           WHERE date BETWEEN
             date(current_timestamp, '{offset_min} days')
             AND
             date(current_timestamp, '{offset_max} days')
        """,
        (kitty,),
    )
    rv = cur.fetchall()
    cur.close()
    return rv


def write_to_food_log(human, kitty, wet, dry, hairball, regular):
    timestamp = datetime.datetime.now().isoformat(" ").split(".")[0]
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
    timestamp = datetime.datetime.now().isoformat(" ").split(".")[0]
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
