from data import *
from pyrogram import Client, filters
import sqlite3
import random
import string
from datetime import datetime, timedelta
import re
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

Db_path = "Vortex.db"
roles_path = "roles.db"

def generar_key():
    return 'Vortex-' + '-'.join(''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(4))

def crear_tabla():
    conn = sqlite3.connect(Db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS key (
                        Key TEXT PRIMARY KEY,
                        Dias INTEGER,
                        ID TEXT,
                        Created TEXT,
                        Status TEXT)''')
    conn.commit()
    conn.close()

def asegurarse_columna_status():
    conn = sqlite3.connect(Db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(key)")
    columnas = [col[1] for col in cursor.fetchall()]
    if "Status" not in columnas:
        cursor.execute("ALTER TABLE key ADD COLUMN Status TEXT DEFAULT 'Live ✅'")
    conn.commit()
    conn.close()

def guardar_key(key, dias, usuario):
    conn = sqlite3.connect(Db_path)
    cursor = conn.cursor()
    fecha_creacion = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    cursor.execute("INSERT INTO key (Key, Dias, ID, Created, Status) VALUES (?, ?, ?, ?, ?)", 
                   (key, dias, usuario, fecha_creacion, "Live ✅"))
    conn.commit()
    conn.close()

def calcular_tiempo_restante(dias):
    ahora = datetime.now()
    expiracion = ahora + timedelta(days=dias)
    tiempo_restante = expiracion - ahora
    horas_totales = tiempo_restante.days * 24 + tiempo_restante.seconds // 3600
    return expiracion.strftime('%d/%m/%Y %H:%M'), f"{horas_totales}h (s)"

def verificar_permisos(user_id):
    conn = sqlite3.connect(roles_path)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM roles WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0].lower() in ['owner', 'dev', 'seller', 'admin']

@rex(['key'])
async def chk(client, msg):
    crear_tabla()
    asegurarse_columna_status()
    if not verificar_permisos(msg.from_user.id):
        return
    args = msg.text.split(maxsplit=1)
    if len(args) == 1:
        await msg.reply_text(
            "<b>[<a href=https://t.me/VortexChekerBot>ϟ</a>] AdminHub: Uso correcto: /key Dias</b>", 
            reply_to_message_id=msg.id, 
            disable_web_page_preview=True
        )
        return

    match = re.search(r'(\d+)', args[1])
    dias = int(match.group(1)) if match else 0

    if dias <= 0: 
        await msg.reply_text(
            "<b>[<a href=https://t.me/VortexChekerBot>ϟ</a>] AdminHub: Uso correcto: /key Dias</b>", 
            reply_to_message_id=msg.id, 
            disable_web_page_preview=True
        )
        return

    keys = [generar_key() for _ in range(1)]
    expiracion, tiempo_restante = calcular_tiempo_restante(dias)
    
    keys_str = "\n".join(keys)
    respuesta = f"""<b>[<a href="https://t.me/VortexChekerBot">ϟ</a>] Key Created Successfully: >_ $-Security System ⚠️</b>
━━━━━━━━━━━━━━━━
<b>[<a href="https://t.me/VortexChekerBot">ϟ</a>] Key: <code>{keys_str}</code></b>
<b>[<a href="https://t.me/VortexChekerBot">ϟ</a>] Plan: Premium | AntiSpam: 20s</b>
<b>[<a href="https://t.me/VortexChekerBot">ϟ</a>] Duracion: {expiracion} | Expired in: {tiempo_restante}</b>
━━━━━━━━━━━━━━━━
<b>[<a href="https://t.me/VortexChekerBot">ϟ</a>] Ejem: <code>/claim {keys_str}</code></b>
<b>[<a href="https://t.me/VortexChekerBot">ϟ</a>] BotChk: @VortexChekerbot</b>
━━━━━━━━━━━━━━━━"""

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Owner", url="https://t.me/Exzzex"),
                InlineKeyboardButton("Co-Owner", url="https://t.me/geovvanycop")
            ]
        ]
    )

    for key in keys:
        guardar_key(key, dias, msg.from_user.username)

    await msg.reply_text(
        respuesta, 
        disable_web_page_preview=True, 
        reply_to_message_id=msg.id,
        reply_markup=buttons
    )

    conn = sqlite3.connect(roles_path)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM roles WHERE user_id IN (7202754124, 6912324978)")
    users = cursor.fetchall()
    conn.close()

    for user in users:
        try:
            await client.send_message(
                user[0], 
                respuesta, 
                disable_web_page_preview=True
            )
        except Exception:
            continue
