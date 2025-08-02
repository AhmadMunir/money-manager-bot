import sqlite3

# Check finance_bot.db
conn = sqlite3.connect('finance_bot.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM users')
users = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM assets WHERE is_active = 1')
assets = cursor.fetchone()[0]

print(f'Users: {users}, Assets: {assets}')

if assets > 0:
    cursor.execute('SELECT name, symbol, quantity, buy_price FROM assets WHERE is_active = 1')
    for asset in cursor.fetchall():
        print(f'Asset: {asset[0]} ({asset[1]}) - {asset[2]} @ {asset[3]}')

conn.close()
