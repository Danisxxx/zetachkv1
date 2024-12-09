from datetime import datetime
from pyrogram import Client, filters
from pluss.Func import connect_to_db
from data import *
from configs._def_main_ import *

@rex(['register'])
async def chk(client, msg):
    user_id = msg.from_user.id
    user_username = msg.from_user.username or "Sin nombre de usuario"

    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Users WHERE id=?", (user_id,))
    if cursor.fetchone():
        await msg.reply(
            textea.format(user_id=user_id, user_username=user_username),
            disable_web_page_preview=True,
            reply_to_message_id=msg.id
        )
    else:
        fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO Users (id, rango, dias, expiracion, creditos, antispam, bin_lasted, ban, fecha_registro) 
            VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?)
        ''', (user_id, 'Free User', 0, '', 0, 0, 'False', fecha_registro))
        conn.commit()
        await msg.reply(
            texteb.format(user_username=user_username),
            disable_web_page_preview=True,
            reply_to_message_id=msg.id
        )

    conn.close()
