from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from sqlalchemy import inspect

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///complaints.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'path/to/upload/folder'

# Flask extensions
db = SQLAlchemy(app)

# Model Definition
class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    mobile_number = db.Column(db.String(15))
    email = db.Column(db.String(255))
    department = db.Column(db.String(255))
    stream = db.Column(db.String(255))
    section = db.Column(db.String(255))
    roll = db.Column(db.String(20))
    status = db.Column(db.String(20))
    image = db.Column(db.String(255))
    video = db.Column(db.String(255))
    audio = db.Column(db.String(255))


# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    user_type = request.form.get('user_type')
    if user_type == 'student':
        return redirect(url_for('student'))
    elif user_type == 'admin':
        return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('index'))

@app.route('/student', methods=['GET', 'POST'])
def student():
    if request.method == 'POST':
        name = request.form['name']
        mobile_number = request.form['mobile_number']
        email = request.form['email']
        department = request.form['department']
        complain = request.form['complain']
        section = request.form['section']
        roll = request.form['roll']

        image_file = request.files['image']
        video_file = request.files['video']
        audio_file = request.files['audio']

        image_filename = secure_filename(image_file.filename)
        video_filename = secure_filename(video_file.filename)
        audio_filename = secure_filename(audio_file.filename)

        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], video_filename))
        audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename))

        complain_data = Complaint(
            name=name,
            mobile_number=mobile_number,
            email=email,
            department=department,
            complain=complain,
            section=section,
            roll=roll,
            status='Pending',
            image=image_filename,
            video=video_filename,
            audio=audio_filename
        )

        with app.app_context():
            db.session.add(complain_data)
            db.session.commit()

        return redirect(url_for('index'))

    return render_template('student.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        
        if email == 'admin@example.com' and password == 'admin123':
            return redirect(url_for('complains'))

        return redirect(url_for('index'))

    return render_template('admin_login.html')

@app.route('/complains')
def complains():
    complaints_list = Complaint.query.all()
    return render_template('complains.html', complaints=complaints_list)

@app.route('/complain_details/<int:complaint_id>')
def complain_details(complaint_id):
    complaint_data = Complaint.query.get(complaint_id)
    
    if complaint_data:
        return jsonify({
            'name': complaint_data.name,
            'mobile_number': complaint_data.mobile_number,
            'email': complaint_data.email,
            'department': complaint_data.department,
            'complain': complaint_data.complain,
            'section': complaint_data.section,
            'roll': complaint_data.roll,
            'status': complaint_data.status,
            'image': complaint_data.image,
            'video': complaint_data.video,
            'audio': complaint_data.audio
        })
    else:
        return jsonify({'error': 'Complaint not found'})

if __name__ == '__main__':
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table('complaint'):
            db.create_all()
            print("Database created successfully.")
    
    app.run(debug=True)
