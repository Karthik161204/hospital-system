from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# HOME PAGE + SEARCH DOCTOR BY SPECIALTY
@app.route("/")
def home():

    specialty = request.args.get("specialty")

    db = get_db()

    if specialty:
        doctors = db.execute(
            "SELECT * FROM doctors WHERE specialty LIKE ?",
            ('%' + specialty + '%',)
        ).fetchall()
    else:
        doctors = db.execute(
            "SELECT * FROM doctors"
        ).fetchall()

    return render_template("index.html", doctors=doctors)


# BOOK APPOINTMENT
@app.route("/book/<doctor_id>", methods=["GET","POST"])
def book(doctor_id):

    if request.method == "POST":

        name = request.form["name"]
        date = request.form["date"]
        prescription = request.form["prescription"]

        db = get_db()

        # TOKEN GENERATION
        token = db.execute(
            "SELECT COUNT(*) FROM appointments WHERE date=? AND doctor_id=?",
            (date, doctor_id)
        ).fetchone()[0] + 1

        db.execute(
            "INSERT INTO appointments (patient_name, doctor_id, date, prescription, token) VALUES (?,?,?,?,?)",
            (name, doctor_id, date, prescription, token)
        )

        db.commit()

        return render_template(
            "success.html",
            name=name,
            date=date,
            token=token
        )

    return render_template("book.html", doctor_id=doctor_id)


# PATIENT HISTORY VIEW
@app.route("/history")
def history():

    db = get_db()

    appointments = db.execute(
        "SELECT * FROM appointments"
    ).fetchall()

    return render_template(
        "history.html",
        appointments=appointments
    )


# DOCTOR UPDATES PRESCRIPTION
@app.route("/update/<appointment_id>", methods=["GET","POST"])
def update(appointment_id):

    db = get_db()

    if request.method == "POST":

        prescription = request.form["prescription"]

        db.execute(
            "UPDATE appointments SET prescription=? WHERE id=?",
            (prescription, appointment_id)
        )

        db.commit()

        return redirect("/history")

    appointment = db.execute(
        "SELECT * FROM appointments WHERE id=?",
        (appointment_id,)
    ).fetchone()

    return render_template(
        "update.html",
        appointment=appointment
    )


# RUN SERVER
if __name__ == "__main__":
    app.run()