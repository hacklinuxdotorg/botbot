" seen.py: written by sklnd in about two beers July 2009"

import os
import time
from datetime import datetime
import sqlite3

from util import hook, timesince


dbname = "skybot.db"


def adapt_datetime(ts):
    return time.mktime(ts.timetuple())

sqlite3.register_adapter(datetime, adapt_datetime)


@hook.command(hook=r'(.*)', prefix=False, ignorebots=False)
def seeninput(bot, input):
    dbpath = os.path.join(bot.persist_dir, dbname)

    conn = dbconnect(dbpath)
    cursor = conn.cursor()
    cursor.execute("insert or replace into seen(name, date, quote, chan)"
        "values(?,?,?,?)", (input.nick, datetime.now(),
        input.msg, input.chan))
    conn.commit()
    conn.close()


@hook.command
def seen(bot, input):
    ".seen <nick> - Tell when a nickname was last in active in irc"

    if len(input.msg) < 6:
        return seen.__doc__

    query = input.msg[6:].strip()

    if query == input.nick:
        return "Have you looked in a mirror lately?"

    dbpath = os.path.join(bot.persist_dir, dbname)
    conn = dbconnect(dbpath)
    cursor = conn.cursor()

    command = "select date, quote from seen where name = ? and chan = ?"
    cursor.execute(command, (query, input.chan))
    results = cursor.fetchone()

    conn.close()

    if(results != None):
        reltime = timesince.timesince(datetime.fromtimestamp(results[0]))
        return '%s was last seen %s ago saying: <%s> %s' % \
                    (query, reltime, results[1])
    else:
        return "I've never seen %s" % query


def dbconnect(db):
    "check to see that our db has the the seen table and return a connection."
    conn = sqlite3.connect(db)
    results = conn.execute("select count(*) from sqlite_master where name=?",
            ("seen", )).fetchone()

    if(results[0] == 0):
        conn.execute("create table if not exists "
                     "seen(name varchar(30) not null, date datetime not null, "
                     "quote varchar(250) not null, chan varchar(32) not null, "
                     "primary key(name, chan));")
        conn.commit()

    return conn