import psycopg2
import os
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, jsonify, request

app = Flask(__name__, template_folder='templates')

# --------------- Database Connection ---------------

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

# --------------- Routes ---------------

@app.route('/')
def index():
    """
    Renders the welcome page with a company logo.
    Forventet at bruge templates/index.html
    """
    return render_template('index.html')


@app.route('/save_wifi', methods=['POST'])
def save_wifi():
    """
    Modtager WiFi-oplysninger (ssid + password) fra frontend som JSON
    og gemmer dem i databasen i tabellen wifi_oplysninger.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Ingen JSON modtaget."}), 400

    ssid = data.get("ssid")
    password = data.get("password")

    if not ssid or not password:
        return jsonify({"error": "Både SSID og password skal udfyldes."}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Sørg for at tabellen eksisterer (simpel "auto-oprettelse" – kan fjernes hvis du laver tabellen manuelt)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS wifi_oplysninger (
                id SERIAL PRIMARY KEY,
                ssid TEXT NOT NULL,
                password_plaintext TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

        # Indsæt data
        cur.execute(
            """
            INSERT INTO wifi_oplysninger (ssid, password_plaintext)
            VALUES (%s, %s);
            """,
            (ssid, password)
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "ok", "message": "WiFi-oplysninger gemt."}), 200

    except Exception as e:
        # Log fejlen til konsollen (praktisk når du kører debug=True)
        print("Databasefejl i /save_wifi:", e)
        return jsonify({"error": "Der opstod en databasefejl."}), 500

# --------------- Run the App ---------------

if __name__ == '__main__':
    # debug=True er fint til udvikling, men slå det fra i produktion
    app.run(debug=True)
