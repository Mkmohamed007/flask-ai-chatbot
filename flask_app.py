from flask import Flask, request, jsonify
import pymysql
import openai
from flask_cors import CORS

# 🔹 Initialize Flask App
app = Flask(__name__)
CORS(app)

# 🔹 MySQL Database Configuration
DB_CONFIG = {
    "host": "sql107.infinityfree.com",  # Change to your MySQL server IP or localhost
    "user": "if0_38267837",
    "password": "PjTRAcATLTR",
    "database": "if0_38267837_sms"
}

# 🔹 OpenAI API Key (Temporarily Hardcoded)
client = openai.OpenAI(api_key="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")

# 🔹 Connect to MySQL Database
def get_db_connection():
    """Establishes a connection to the MySQL database."""
    return pymysql.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        cursorclass=pymysql.cursors.DictCursor
    )

# 🔹 Fetch all tables and their data
def fetch_all_data():
    """Fetches all tables and their data from the MySQL database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SHOW TABLES")
        tables = [list(row.values())[0] for row in cursor.fetchall()]

        database_data = {}
        for table in tables:
            cursor.execute(f"SELECT * FROM {table} LIMIT 50")  # Limit rows to avoid too much data
            database_data[table] = cursor.fetchall()

        conn.close()
        return database_data
    except Exception as e:
        return {"error": str(e)}

# 🔹 AI Chat Endpoint
@app.route('/chat', methods=['POST'])
def chat():
    """Processes user queries using AI with database context."""
    user_prompt = request.json.get("prompt")

    if not user_prompt:
        return jsonify({"success": False, "error": "No prompt provided."})

    # Fetch all database data
    database_data = fetch_all_data()
    if "error" in database_data:
        return jsonify({"success": False, "error": database_data["error"]})

    # Format data for OpenAI
    formatted_data = "\n".join([f"{table}: {data}" for table, data in database_data.items()])

    # Construct AI Prompt
    chat_prompt = f"""
    You are an AI assistant with access to the following database:

    {formatted_data}

    User Question: {user_prompt}
    
    Provide a relevant and helpful response based on the database data.
    """

    # ✅ Send request to OpenAI (Fixed for OpenAI 1.61.1)
    try:
        response = client.chat.completions.create(  # ✅ Correct OpenAI API Call
model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant with access to a MySQL database."},
                {"role": "user", "content": chat_prompt}
            ]
        )

        ai_response = response.choices[0].message.content  # ✅ Corrected Response Extraction
        return jsonify({"success": True, "response": ai_response})  # ✅ Correct Indentation

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# 🔹 Flask Home Route
@app.route('/', methods=['GET'])
def home():
    return "✅ AI Agent Bot API is running!", 200

# 🔹 Run Flask Server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
