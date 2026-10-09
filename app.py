import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, g, abort

app = Flask(__name__)
app.secret_key = "uts-lab-pemrograman-2026"
DATABASE = "mahasiswa.db"


# ---------- Koneksi database ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute(
        """CREATE TABLE IF NOT EXISTS mahasiswa (
            nim INTEGER PRIMARY KEY,
            nama TEXT NOT NULL,
            program_studi TEXT NOT NULL,
            angkatan INTEGER NOT NULL,
            ipk REAL NOT NULL
        )"""
    )
    db.commit()
    db.close()


# ---------- Fungsi bantu ----------
def tambah_lama_studi(row):
    data = dict(row)
    data["lama_studi"] = datetime.now().year - data["angkatan"]
    return data


def validasi(form):
    errors = []
    nim_raw = form.get("nim", "").strip()
    nama = form.get("nama", "").strip()
    prodi = form.get("program_studi", "").strip()
    angkatan_raw = form.get("angkatan", "").strip()
    ipk_raw = form.get("ipk", "").strip().replace(",", ".")
    nim = angkatan = ipk = None

    if not nim_raw:
        errors.append("NIM tidak boleh kosong.")
    else:
        try:
            nim = int(nim_raw)
        except ValueError:
            errors.append("NIM harus berupa angka.")

    if not nama:
        errors.append("Nama tidak boleh kosong.")
    if not prodi:
        errors.append("Program studi tidak boleh kosong.")

    if not angkatan_raw:
        errors.append("Angkatan tidak boleh kosong.")
    else:
        try:
            angkatan = int(angkatan_raw)
        except ValueError:
            errors.append("Angkatan harus berupa angka.")

    if not ipk_raw:
        errors.append("IPK tidak boleh kosong.")
    else:
        try:
            ipk = float(ipk_raw)
            if ipk < 0.0 or ipk > 4.0:
                errors.append("IPK harus berada di rentang 0.00 sampai 4.00.")
        except ValueError:
            errors.append("IPK harus berupa angka.")

    data = {"nim": nim, "nama": nama, "program_studi": prodi,
            "angkatan": angkatan, "ipk": ipk}
    return data, errors


# ---------- READ (daftar) ----------
@app.route("/")
def index():
    rows = get_db().execute("SELECT * FROM mahasiswa ORDER BY nim").fetchall()
    mahasiswa = [tambah_lama_studi(r) for r in rows]
    return render_template("index.html", mahasiswa=mahasiswa)


# # ---------- CREATE ----------
@app.route("/tambah", methods=["GET", "POST"])
def tambah():
    if request.method == "POST":
        data, errors = validasi(request.form)
        db = get_db()
        if not errors:
            ada = db.execute("SELECT 1 FROM mahasiswa WHERE nim = ?",
                             (data["nim"],)).fetchone()
            if ada:
                errors.append(f"NIM {data['nim']} sudah terdaftar.")
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("form.html", judul="Tambah Mahasiswa",
                                   m=request.form, edit=False)
        db.execute(
            "INSERT INTO mahasiswa (nim, nama, program_studi, angkatan, ipk) VALUES (?, ?, ?, ?, ?)",
            (data["nim"], data["nama"], data["program_studi"], data["angkatan"], data["ipk"]),
        )
        db.commit()
        flash("Mahasiswa berhasil ditambahkan.", "success")
        return redirect("/")
    return render_template("form.html", judul="Tambah Mahasiswa", m={}, edit=False)(route baru nanti ditambahkan DI ATAS baris if __name__ di bawah ini)

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5001)