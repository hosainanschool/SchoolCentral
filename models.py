from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Teacher(UserMixin, db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attendance_records = db.relationship('AttendanceRecord', backref='teacher', lazy=True)
    behavior_reports = db.relationship('BehaviorReport', backref='teacher', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Teacher {self.name}>'

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date)
    parent_name = db.Column(db.String(100))
    parent_phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    enrollment_date = db.Column(db.Date, default=datetime.utcnow().date())
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy=True)
    behavior_reports = db.relationship('BehaviorReport', backref='student', lazy=True)
    
    def __repr__(self):
        return f'<Student {self.name}>'

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # present, absent, late, excused
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Composite unique constraint to prevent duplicate records
    __table_args__ = (db.UniqueConstraint('student_id', 'date', name='unique_student_date'),)
    
    def __repr__(self):
        return f'<AttendanceRecord {self.student.name} - {self.date} - {self.status}>'

class BehaviorReport(db.Model):
    __tablename__ = 'behavior_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    behavior_type = db.Column(db.String(50), nullable=False)  # positive, negative, neutral
    category = db.Column(db.String(100))  # discipline, academic, social, etc.
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.Integer, default=1)  # 1-5 scale
    action_taken = db.Column(db.Text)
    parent_notified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BehaviorReport {self.student.name} - {self.date} - {self.behavior_type}>'

class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemSettings {self.key}>'
