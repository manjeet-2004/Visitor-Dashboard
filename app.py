from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Set up the database URI (SQLite database in this case)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///museum_exhibit.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To disable the warning

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# Create folder to store uploads
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Step 1: Define the Database Models (Tables)

# Exhibit model
class Exhibit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Exhibit {self.name}>'

# Profile model
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    profile_picture = db.Column(db.String(200))

    def __repr__(self):
        return f'<Profile {self.email}>'

# Report model
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exhibit_id = db.Column(db.Integer, db.ForeignKey('exhibit.id'), nullable=False)
    issue_description = db.Column(db.String(200), nullable=False)
    date_reported = db.Column(db.String(20), nullable=False)

    exhibit = db.relationship('Exhibit', backref=db.backref('reports', lazy=True))

    def __repr__(self):
        return f'<Report for {self.exhibit.name}>'

# Step 2: Create the Database

with app.app_context():
    db.create_all()

# Step 3: Routes and Views

@app.route('/')
def home():
    # Fetch exhibits from the database
    exhibits = Exhibit.query.all()
    return render_template('visitor.html', exhibits=exhibits)

@app.route('/profile', methods=['POST'])
def save_profile():
    if request.method == 'POST':
        # Handle profile saving, including file upload
        profile_picture = request.files['profilePicture']
        email = request.form['email']
        phone = request.form['phone']
        
        # Save the profile picture
        if profile_picture:
            picture_filename = os.path.join(app.config['UPLOAD_FOLDER'], profile_picture.filename)
            profile_picture.save(picture_filename)

        # Save the profile data to the database
        profile = Profile(email=email, phone=phone, profile_picture=picture_filename)
        db.session.add(profile)
        db.session.commit()

        return jsonify({"message": "Profile saved successfully!"}), 200

@app.route('/report_issue', methods=['POST'])
def report_issue():
    issue_data = request.json
    exhibit_id = issue_data['exhibit_id']
    issue_description = issue_data['issue_description']
    
    # Save the reported issue in the database
    new_report = Report(
        exhibit_id=exhibit_id,
        issue_description=issue_description,
        date_reported="2024-12-13"  # Here, you can use current date dynamically
    )
    db.session.add(new_report)
    db.session.commit()

    return jsonify({"message": "Issue reported successfully!"}), 200

@app.route('/report_status', methods=['GET'])
def report_status():
    # Fetch all reports from the database
    reports = Report.query.all()
    report_data = [{
        'exhibit': report.exhibit.name,
        'issue_description': report.issue_description,
        'date_reported': report.date_reported
    } for report in reports]

    return jsonify(report_data), 200

@app.route('/feedback', methods=['POST'])
def save_feedback():
    feedback_data = request.json
    exhibit_id = feedback_data['exhibit_id']
    feedback = feedback_data['feedback']
    
    # Save feedback to the database (This part is for further extension)
    print(f"Feedback received for Exhibit {exhibit_id}: {feedback}")
    
    return jsonify({"message": "Feedback saved successfully!"}), 200

# Step 4: Start the Flask App

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
