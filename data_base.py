import sqlite3 as sq

async def db_start():
    global db, cur

    db = sq.connect('new.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS profile(id TEXT PRIMARY KEY, Страна TEXT, Имя TEXT, Фамилия TEXT, Паспорт TEXT, Boardcode TEXT, Телефон TEXT, Email TEXT, С TEXT, До TEXT, Оплата TEXT)")

    db.commit()


async def create_profile(user_id):
    user = cur.execute("SELECT 1 FROM profile WHERE id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO profile VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, '', '', '', '', '', '', '', '', '', ''))
        db.commit()


async def edit_profile(state, user_id):
    async with state.proxy() as data:
        cur.execute("""UPDATE profile SET 
                        Страна = '{}', 
                        Имя = '{}', 
                        Фамилия = '{}', 
                        Паспорт = '{}', 
                        Boardcode = '{}', 
                        Телефон = '{}', 
                        Email = '{}', 
                        С = '{}', 
                        До = '{}',
                        Оплата = '{}'
                        
                        WHERE id == '{}'""".format
                    (data['country'], data['first_name'], data['second_name'],
                     data['passport_num'], data['boardcode_num'], data['phone'],
                     data['email'], data['first_date'], data['second_date'], '', user_id))
        db.commit()
