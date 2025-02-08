from flask import Flask, request, jsonify
import pymysql
import openai
from flask_cors import CORS

# 🔹 Initialize Flask App
app = Flask(__name__)
CORS(app)

# 🔹 MySQL Database Configuration (For Testing)
DB_CONFIG = {
    "host": "srv1700.hstgr.io",  # ✅ Your cPanel MySQL Host
    "user": "u314987953_sms",
    "password": "Lt>Z$TV1$",
    "database": "u314987953_sms"
}

# 🔹 OpenAI API Key (For Testing)
openai.api_key = "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"

# 🔹 Connect to MySQL Database
def get_db_connection():
    """Establishes a connection to the MySQL database with error handling."""
    try:
        conn = pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except pymysql.MySQLError as e:
        print(f"❌ Database Connection Error: {e}")
        return None

# 🔹 Fetch all tables and their data
def fetch_all_data():
    """Fetches all tables and their data from the MySQL database."""
    try:
        conn = get_db_connection()
        if conn is None:
            return {"error": "Database connection failed"}

        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SHOW TABLES")
        tables = [list(row.values())[0] for row in cursor.fetchall()]

        database_data = {}
        for table in tables:
            cursor.execute(f"SELECT * FROM {table} LIMIT 10")  # ✅ Reduced limit for faster response
            database_data[table] = cursor.fetchall()

        return database_data
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()  # ✅ Ensure connection is closed properly

# 🔹 AI Chat Endpoint
@app.route('/chat', methods=['POST'])
def chat():
    """Processes user queries using AI with database context."""
    data = request.get_json(force=True)  # ✅ Force JSON parsing

    print("📡 Received Data:", data)  # Debugging statement

    if not data or "prompt" not in data:
        return jsonify({"success": False, "error": "No prompt provided."})

    user_prompt = data.get("prompt", "").strip()
    if not user_prompt:
        return jsonify({"success": False, "error": "Prompt is empty."})

    # Fetch database data
    database_data = fetch_all_data()
    if "error" in database_data:
        return jsonify({"success": False, "error": database_data["error"]})

    # ✅ Fix: Format data properly for OpenAI
    formatted_data = "\n".join(
        [f"Table {table}:\n" + "\n".join([str(row) for row in data]) for table, data in database_data.items()]
    )

    # Construct AI prompt
    chat_prompt = f"""
    You are an AI assistant with access to the following database:

    {formatted_data}

    User Question: {user_prompt}
    
    Provide a relevant and helpful response based on the database data.
    """

    # Send request to OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant with access to a MySQL database."},
                {"role": "user", "content": chat_prompt}
            ]
        )

        ai_response = response["choices"][0]["message"]["content"]  # ✅ Corrected response extraction
        return jsonify({"success": True, "response": ai_response})

    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return jsonify({"success": False, "error": str(e)})

# 🔹 Flask Home Route
@app.route('/', methods=['GET'])
def home():
    return "✅ AI Agent Bot API is running!", 200

# 🔹 Run Flask Server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
