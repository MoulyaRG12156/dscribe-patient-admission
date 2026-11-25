import os, re, sqlite3
from datetime import date
from flask import Flask, request, jsonify, g
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))
DB_PATH = os.getenv('DATABASE_PATH', os.path.join(os.path.dirname(__file__), 'patients.db'))
OPTIONS = {
    'gender': ['Male', 'Female', 'Other'],
    'ward': ['General Ward', 'ICU', 'Pediatric Ward', 'Maternity Ward', 'Surgical Ward', 'Emergency'],
    'department': ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'General Medicine', 'Surgery', 'Obstetrics & Gynecology'],
    'doctor': ['Dr. Sharma', 'Dr. Reddy', 'Dr. Mehta', 'Dr. Kumar', 'Dr. Patel', 'Dr. Iyer']
}

def db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    conn = g.pop('db', None)
    if conn is not None: conn.close()

with app.app_context():
    db().execute('''CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, age INTEGER NOT NULL,
        gender TEXT NOT NULL, ward TEXT NOT NULL, department TEXT NOT NULL,
        doctor TEXT NOT NULL, admission_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Admitted', created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    db().commit()

def validate(data):
    errors = {}
    name = str(data.get('name', '')).strip()
    if not name: errors['name'] = 'Name is required.'
    elif not re.fullmatch(r"[A-Za-z ]+", name): errors['name'] = 'Name must contain letters only.'
    age = data.get('age')
    try:
        if age is None or str(age).strip() == '': raise ValueError()
        age = int(age)
        if not 0 <= age <= 120: raise ValueError()
    except (ValueError, TypeError): errors['age'] = 'Age is required and must be a number between 0 and 120.'
    for key in OPTIONS:
        if data.get(key) not in OPTIONS[key]: errors[key] = f"Please select a valid {key}."
    admission = str(data.get('admission_date', '')).strip()
    try:
        parsed = date.fromisoformat(admission)
        if parsed > date.today(): errors['admission_date'] = 'Admission date cannot be in the future.'
    except ValueError: errors['admission_date'] = 'A valid admission date is required.'
    status = data.get('status', 'Admitted')
    if status not in ['Admitted', 'Discharged']: errors['status'] = 'Status must be Admitted or Discharged.'
    return errors

def serialize(row): return dict(row)

@app.get('/api/health')
def health(): return jsonify({'status':'ok','service':'DScribe Patient Admission API'})

@app.get('/api/options')
def options(): return jsonify(OPTIONS)

@app.get('/api/patients')
def list_patients():
    query = "SELECT * FROM patients WHERE 1=1"
    args = []
    for field in ['ward','department','doctor']:
        value = request.args.get(field)
        if value: query += f' AND {field}=?'; args.append(value)
    search = request.args.get('search','').strip()
    if search: query += ' AND name LIKE ?'; args.append(f'%{search}%')
    query += ' ORDER BY id DESC'
    rows = db().execute(query, args).fetchall()
    return jsonify([serialize(r) for r in rows])

@app.post('/api/patients')
def create_patient():
    data = request.get_json(silent=True) or {}
    errors = validate(data)
    if errors: return jsonify({'error':'Validation failed','fields':errors}), 400
    values = [str(data['name']).strip(), int(data['age']), data['gender'], data['ward'], data['department'], data['doctor'], data['admission_date'], data.get('status','Admitted')]
    cur = db().execute('INSERT INTO patients (name,age,gender,ward,department,doctor,admission_date,status) VALUES (?,?,?,?,?,?,?,?)', values)
    db().commit()
    return jsonify(serialize(db().execute('SELECT * FROM patients WHERE id=?',(cur.lastrowid,)).fetchone())), 201

@app.put('/api/patients/<int:patient_id>')
def update_patient(patient_id):
    if not db().execute('SELECT id FROM patients WHERE id=?',(patient_id,)).fetchone(): return jsonify({'error':'Patient not found.'}),404
    data = request.get_json(silent=True) or {}
    errors = validate(data)
    if errors: return jsonify({'error':'Validation failed','fields':errors}),400
    values = [str(data['name']).strip(), int(data['age']), data['gender'], data['ward'], data['department'], data['doctor'], data['admission_date'], data.get('status','Admitted'), patient_id]
    db().execute('UPDATE patients SET name=?,age=?,gender=?,ward=?,department=?,doctor=?,admission_date=?,status=? WHERE id=?',values)
    db().commit()
    return jsonify(serialize(db().execute('SELECT * FROM patients WHERE id=?',(patient_id,)).fetchone()))

@app.patch('/api/patients/<int:patient_id>/discharge')
def discharge_patient(patient_id):
    cur = db().execute("UPDATE patients SET status='Discharged' WHERE id=?",(patient_id,))
    db().commit()
    if cur.rowcount == 0: return jsonify({'error':'Patient not found.'}),404
    return jsonify(serialize(db().execute('SELECT * FROM patients WHERE id=?',(patient_id,)).fetchone()))

@app.delete('/api/patients/<int:patient_id>')
def delete_patient(patient_id):
    cur = db().execute('DELETE FROM patients WHERE id=?',(patient_id,)); db().commit()
    if cur.rowcount == 0: return jsonify({'error':'Patient not found.'}),404
    return jsonify({'message':'Patient deleted successfully.'})

if __name__ == '__main__': app.run(host='0.0.0.0', port=int(os.getenv('PORT',5000)), debug=True)
