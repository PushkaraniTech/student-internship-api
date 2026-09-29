from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

DATABASE = "internship.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            skill TEXT NOT NULL,
            location TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/internships", methods=["GET"])
def get_internships():
    connection = get_db_connection()

    internships = connection.execute(
        "SELECT * FROM internships"
    ).fetchall()

    connection.close()

    return jsonify([dict(row) for row in internships])


@app.route("/internships", methods=["POST"])
def add_internship():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "JSON data is required"
        }), 400

    required_fields = ["company", "role", "skill", "location"]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"{field} is required"
            }), 400

    connection = get_db_connection()

    connection.execute("""
        INSERT INTO internships
        (company, role, skill, location)
        VALUES (?, ?, ?, ?)
    """, (
        data["company"],
        data["role"],
        data["skill"],
        data["location"]
    ))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Internship added successfully"
    }), 201


@app.route("/internships/search", methods=["GET"])
def search_internships():
    skill = request.args.get("skill")

    if not skill:
        return jsonify({
            "error": "Please provide a skill"
        }), 400

    connection = get_db_connection()

    internships = connection.execute(
        "SELECT * FROM internships WHERE skill LIKE ?",
        ("%" + skill + "%",)
    ).fetchall()

    connection.close()

    return jsonify([dict(row) for row in internships])


@app.route("/internships/<int:internship_id>", methods=["DELETE"])
def delete_internship(internship_id):
    connection = get_db_connection()

    result = connection.execute(
        "DELETE FROM internships WHERE id = ?",
        (internship_id,)
    )

    connection.commit()
    connection.close()

    if result.rowcount == 0:
        return jsonify({
            "error": "Internship not found"
        }), 404

    return jsonify({
        "message": "Internship deleted successfully"
    })


if __name__ == "__main__":
    create_table()
    app.run(debug=True)