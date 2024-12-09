import asyncio
import sqlite3
from datetime import datetime, timedelta
import re

DB_PATH = "Vortex.db"
update_interval = 1

async def update_viped():
    while True:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, dias, expiracion, rango FROM Users")
        users = cursor.fetchall()

        for user in users:
            user_id, days, expiration, rank = user

            if rank.lower() not in ['free user', 'premium']:
                if days >= 1:
                    
                    if not expiration or expiration == "":
                        if days == 1:
                            expiration = "0 días 23 horas 59 minutos 58 segundos"
                        else:
                            expiration = f"{days-1} días 23 horas 59 minutos 59 segundos"
                        cursor.execute("UPDATE Users SET expiracion = ? WHERE id = ?", (expiration, user_id))

                    match = re.match(r"(\d+) días (\d+) horas (\d+) minutos (\d+) segundos", expiration)
                    if match:
                        days_left, hours_left, minutes_left, seconds_left = map(int, match.groups())

                        if days_left != days - 1:  
                            days_left = days - 1
                            hours_left = 23
                            minutes_left = 59
                            seconds_left = 59

                        if seconds_left > 0:
                            seconds_left -= 1
                        elif minutes_left > 0:
                            minutes_left -= 1
                            seconds_left = 59
                        elif hours_left > 0:
                            hours_left -= 1
                            minutes_left = 59
                            seconds_left = 59
                        elif days_left > 0:
                            days_left -= 1
                            hours_left = 23
                            minutes_left = 59
                            seconds_left = 59

                        if days_left == 0 and hours_left == 0 and minutes_left == 0 and seconds_left == 0:
                            cursor.execute("UPDATE Users SET expiracion = '' WHERE id = ?", (user_id,))
                            cursor.execute("UPDATE Users SET dias = dias - 1 WHERE id = ?", (user_id,))
                        else:
                            new_expiration = f"{days_left} días {hours_left} horas {minutes_left} minutos {seconds_left} segundos"
                            cursor.execute("UPDATE Users SET expiracion = ? WHERE id = ?", (new_expiration, user_id))

                elif days == 0 and expiration != '':
                    cursor.execute("UPDATE Users SET expiracion = '' WHERE id = ?", (user_id,))

            else:
                if days >= 1:
                    cursor.execute("UPDATE Users SET rango = 'Premium' WHERE id = ?", (user_id,))

                    if not expiration or expiration == "":
                        if days == 1:
                            expiration = "0 días 23 horas 59 minutos 58 segundos"
                        else:
                            expiration = f"{days-1} días 23 horas 59 minutos 59 segundos"
                        cursor.execute("UPDATE Users SET expiracion = ? WHERE id = ?", (expiration, user_id))

                    match = re.match(r"(\d+) días (\d+) horas (\d+) minutos (\d+) segundos", expiration)
                    if match:
                        days_left, hours_left, minutes_left, seconds_left = map(int, match.groups())

                        if days_left != days - 1:  
                            days_left = days - 1
                            hours_left = 23
                            minutes_left = 59
                            seconds_left = 59

                        if seconds_left > 0:
                            seconds_left -= 1
                        elif minutes_left > 0:
                            minutes_left -= 1
                            seconds_left = 59
                        elif hours_left > 0:
                            hours_left -= 1
                            minutes_left = 59
                            seconds_left = 59
                        elif days_left > 0:
                            days_left -= 1
                            hours_left = 23
                            minutes_left = 59
                            seconds_left = 59

                        if days_left == 0 and hours_left == 0 and minutes_left == 0 and seconds_left == 0:
                            cursor.execute("UPDATE Users SET rango = 'Free user' WHERE id = ?", (user_id,))
                            cursor.execute("UPDATE Users SET expiracion = '' WHERE id = ?", (user_id,))
                            cursor.execute("UPDATE Users SET dias = dias - 1 WHERE id = ?", (user_id,))
                        else:
                            new_expiration = f"{days_left} días {hours_left} horas {minutes_left} minutos {seconds_left} segundos"
                            cursor.execute("UPDATE Users SET expiracion = ? WHERE id = ?", (new_expiration, user_id))

                elif days == 0 and expiration != '':
                    cursor.execute("UPDATE Users SET rango = 'Free user' WHERE id = ?", (user_id,))
                    cursor.execute("UPDATE Users SET expiracion = '' WHERE id = ?", (user_id,))

        conn.commit()
        conn.close()

        await asyncio.sleep(update_interval)

loop = asyncio.get_event_loop()
loop.create_task(update_viped())
