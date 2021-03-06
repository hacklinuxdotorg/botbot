import re, string

from util import hook, http

pattern = re.compile('[\W_]+')

@hook.command
def minus(inp, nick='', chan='', db=None):
    '''.minus <nick> -- -1 a nickname'''
    nick = pattern.sub('', inp)
    db.execute("create table if not exists plus"
               "(chan, nick, count default 0,"
               "primary key (chan, nick))")
    db.commit()

    count = list(db.execute("select count from plus where nick=(?) and chan=(?)", (nick, chan)))

    if len(count) > 0:
        count = int(count[0][0])
        count -= 1

        db.execute("UPDATE plus SET count=(?) WHERE nick=(?)", (count, nick))
        db.commit()
    else:
        count = -1
        db.execute("INSERT or fail INTO plus (chan, nick, count) VALUES (?,?,?)", (chan, nick, count))
        db.commit()

    return "{0} has {1} plusses".format(nick, count)
