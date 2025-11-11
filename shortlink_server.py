# ...existing code...
@app.route('/image/<tracker_id>')
def image_tracker_endpoint(tracker_id):
    try:
        ip = get_client_ip(request)
        ua_string = request.headers.get('User-Agent', '')
        ua = ua_parse(ua_string)
        browser = f"{ua.browser.family} {ua.browser.version_string}" if ua.browser.family else "Inconnu"
        device_type = "Mobile" if ua.is_mobile else ("Tablet" if ua.is_tablet else ("PC" if ua.is_pc else "Bot/Autre"))

        # record click in DB
        conn = sqlite3.connect("links.db")
        cursor = conn.cursor()

        # check owner & get image
        cursor.execute('SELECT user_id, image_data FROM image_trackers WHERE id = ?', (tracker_id,))
        row = cursor.fetchone()
        owner_id = row[0] if row else None
        image_blob = row[1] if row else None

        cursor.execute('''
            INSERT INTO image_clicks (tracker_id, ip_address, browser, device_type, country, region, city, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tracker_id, ip, browser, device_type, 'Inconnu', 'Inconnu', 'Inconnu', ua_string))
        cursor.execute('UPDATE image_trackers SET clicks = clicks + 1 WHERE id = ?', (tracker_id,))
        conn.commit()
        conn.close()

        # try to enrich location (non-blocking best effort)
        location = get_ip_location(ip)

        # send DM to creator asynchronously
        if owner_id and bot_instance:
            try:
                bot_instance.loop.create_task(notify_creator_dm(owner_id, tracker_id, ip, browser, device_type, ua_string, location))
            except Exception as e:
                logger.exception(f"Impossible de scheduler la notification: {e}")

        # return the actual image
        if image_blob:
            return send_file(io.BytesIO(image_blob), mimetype='image/png', etag=False)
        else:
            # fallback: tiny transparent PNG
            img_bytes = io.BytesIO()
            img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            return send_file(img_bytes, mimetype='image/png', etag=False)
    except Exception as e:
        logger.exception(f"Erreur endpoint image_tracker: {e}")
        return Response(status=204)
# ...existing code...