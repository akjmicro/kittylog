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
        """select rowid, * from kittylog
           where timestamp > date(?)
           and timestamp < date(?, '+1 day')
           order by timestamp desc, kitty desc;
        """, (timestamp, timestamp,)
    )
    rv = cur.fetchall()
    cur.close()
    return rv


def show_sums(timestamp):
    cur = get_db().execute(
        """select kitty,
                  sum(wet) as sum_wet,
                  sum(dry) as sum_dry,
                  sum(hairball) as sum_hairball,
                  sum(treats) as sum_treats
           from kittylog
           where timestamp > date(?)
           and timestamp < date(?, '+1 day')
           group by kitty;
        """, (timestamp, timestamp,)
    )
    rv = cur.fetchall()
    cur.close()
    return rv


def write_to_log(feeder, kitty, wet, dry, hairball, treats):
    timestamp = datetime.datetime.now().isoformat(' ')
    cur = get_db().execute(
        """insert into kittylog
           (timestamp, feeder, kitty, wet, dry, hairball, treats)
           VALUES(?,?,?,?,?,?,?);
        """, (timestamp, feeder, kitty, wet, dry, hairball, treats)
    )
    cur.connection.commit()
    cur.close()


def delete_entry(rowid):
    cur = get_db().execute(
        """delete from kittylog where rowid=?;""", (rowid,)
    )
    cur.connection.commit()
    cur.close()


def change_timestamp(rowid, hour, minute):
    cur = get_db().execute(
        """select timestamp from kittylog where rowid=?;""", (rowid,)
    )
    try:
        my_ts = cur.fetchone()['timestamp']
    except:
        return        
    the_day, the_time = my_ts.split()
    hr, mn, sec = the_time.split(':')
    new_time = the_day + ' ' + hour + ':' + minute + ':' + sec
    cur2 = get_db().execute(
        """update kittylog set timestamp=? where rowid=?""", (new_time, rowid,)
    )
    cur2.connection.commit()
    cur2.close()
    cur.close()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
