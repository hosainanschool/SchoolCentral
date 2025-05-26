from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import Teacher, Student, AttendanceRecord, BehaviorReport
from forms import LoginForm, TeacherForm, StudentForm, AttendanceForm, BehaviorReportForm, SearchForm
from utils import (export_attendance_to_excel, get_monthly_attendance_stats, 
                  get_behavior_trends, get_student_attendance_summary,
                  translate_status, translate_behavior_type, translate_category)
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    # Get current month statistics
    now = datetime.now()
    stats = get_monthly_attendance_stats(now.year, now.month)
    
    # Get recent behavior reports
    recent_reports = BehaviorReport.query.order_by(BehaviorReport.created_at.desc()).limit(5).all()
    
    # Get total counts
    total_students = Student.query.filter_by(is_active=True).count()
    total_teachers = Teacher.query.count()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_reports=recent_reports,
                         total_students=total_students,
                         total_teachers=total_teachers,
                         current_month=now.strftime('%B %Y'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        teacher = Teacher.query.filter_by(username=form.username.data).first()
        if teacher and teacher.check_password(form.password.data):
            login_user(teacher)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('login'))

@app.route('/attendance')
@login_required
def attendance():
    # Get current month and year from query params or use current date
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Calculate first and last day of month
    first_day = datetime(year, month, 1).date()
    if month == 12:
        last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    # Get attendance records for the month
    records = AttendanceRecord.query.filter(
        AttendanceRecord.date >= first_day,
        AttendanceRecord.date <= last_day
    ).join(Student).order_by(AttendanceRecord.date.desc(), Student.name).all()
    
    # Get students for adding new records
    students = Student.query.filter_by(is_active=True).order_by(Student.name).all()
    
    form = AttendanceForm()
    
    # Generate calendar data
    calendar_data = []
    current_date = first_day
    while current_date <= last_day:
        day_records = [r for r in records if r.date == current_date]
        calendar_data.append({
            'date': current_date,
            'records': day_records,
            'is_today': current_date == date.today()
        })
        current_date += timedelta(days=1)
    
    return render_template('attendance.html', 
                         records=records, 
                         students=students, 
                         form=form,
                         calendar_data=calendar_data,
                         current_year=year,
                         current_month=month,
                         month_name=datetime(year, month, 1).strftime('%B %Y'))

@app.route('/add_attendance', methods=['POST'])
@login_required
def add_attendance():
    form = AttendanceForm()
    if form.validate_on_submit():
        student_id = request.form.get('student_id')
        
        # Check if record already exists
        existing_record = AttendanceRecord.query.filter_by(
            student_id=student_id,
            date=form.date.data
        ).first()
        
        if existing_record:
            flash('سجل الحضور موجود بالفعل لهذا الطالب في هذا التاريخ', 'error')
        else:
            record = AttendanceRecord(
                student_id=student_id,
                teacher_id=current_user.id,
                date=form.date.data,
                status=form.status.data,
                notes=form.notes.data
            )
            db.session.add(record)
            db.session.commit()
            flash('تم إضافة سجل الحضور بنجاح', 'success')
    else:
        flash('حدث خطأ في البيانات المدخلة', 'error')
    
    return redirect(url_for('attendance'))

@app.route('/export_attendance')
@login_required
def export_attendance():
    # Get date range from query params
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = AttendanceRecord.query.join(Student)
    
    if date_from:
        query = query.filter(AttendanceRecord.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        query = query.filter(AttendanceRecord.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
    
    records = query.order_by(AttendanceRecord.date.desc(), Student.name).all()
    
    filename = f"attendance_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return export_attendance_to_excel(records, filename)

@app.route('/students')
@login_required
def students():
    # Search functionality
    search_form = SearchForm()
    query = Student.query
    
    if request.args.get('student_name'):
        query = query.filter(Student.name.contains(request.args.get('student_name')))
    if request.args.get('grade'):
        query = query.filter(Student.grade.contains(request.args.get('grade')))
    if request.args.get('class_name'):
        query = query.filter(Student.class_name.contains(request.args.get('class_name')))
    
    students = query.order_by(Student.name).all()
    
    return render_template('students.html', students=students, search_form=search_form)

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        student = Student(
            student_id=form.student_id.data,
            name=form.name.data,
            grade=form.grade.data,
            class_name=form.class_name.data,
            birth_date=form.birth_date.data,
            parent_name=form.parent_name.data,
            parent_phone=form.parent_phone.data,
            address=form.address.data,
            enrollment_date=form.enrollment_date.data,
            is_active=form.is_active.data
        )
        db.session.add(student)
        db.session.commit()
        flash('تم إضافة الطالب بنجاح', 'success')
        return redirect(url_for('students'))
    
    return render_template('students.html', form=form, adding=True)

@app.route('/behavior')
@login_required
def behavior():
    # Get filter parameters
    student_id = request.args.get('student_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    behavior_type = request.args.get('behavior_type')
    
    # Build query
    query = BehaviorReport.query.join(Student)
    
    if student_id:
        query = query.filter(BehaviorReport.student_id == student_id)
    if date_from:
        query = query.filter(BehaviorReport.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        query = query.filter(BehaviorReport.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
    if behavior_type:
        query = query.filter(BehaviorReport.behavior_type == behavior_type)
    
    reports = query.order_by(BehaviorReport.created_at.desc()).all()
    
    # Get students for filter dropdown
    students = Student.query.filter_by(is_active=True).order_by(Student.name).all()
    
    form = BehaviorReportForm()
    
    return render_template('behavior.html', 
                         reports=reports, 
                         students=students, 
                         form=form,
                         translate_behavior_type=translate_behavior_type,
                         translate_category=translate_category)

@app.route('/add_behavior_report', methods=['POST'])
@login_required
def add_behavior_report():
    form = BehaviorReportForm()
    if form.validate_on_submit():
        student_id = request.form.get('student_id')
        
        report = BehaviorReport(
            student_id=student_id,
            teacher_id=current_user.id,
            date=form.date.data,
            behavior_type=form.behavior_type.data,
            category=form.category.data,
            description=form.description.data,
            severity=form.severity.data,
            action_taken=form.action_taken.data,
            parent_notified=form.parent_notified.data
        )
        db.session.add(report)
        db.session.commit()
        flash('تم إضافة التقرير السلوكي بنجاح', 'success')
    else:
        flash('حدث خطأ في البيانات المدخلة', 'error')
    
    return redirect(url_for('behavior'))

@app.route('/statistics')
@login_required
def statistics():
    # Get current year and month
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Get monthly attendance statistics
    monthly_stats = get_monthly_attendance_stats(year, month)
    
    # Get behavior trends for the last 6 months
    behavior_trends = get_behavior_trends(months=6)
    
    # Get grade-wise statistics
    grades = db.session.query(Student.grade, func.count(Student.id)).filter_by(is_active=True).group_by(Student.grade).all()
    
    # Get top 10 students with most positive behavior reports
    top_positive_students = db.session.query(
        Student.name,
        func.count(BehaviorReport.id).label('positive_count')
    ).join(BehaviorReport).filter(
        BehaviorReport.behavior_type == 'positive'
    ).group_by(Student.id, Student.name).order_by(
        func.count(BehaviorReport.id).desc()
    ).limit(10).all()
    
    # Get attendance rate by grade
    attendance_by_grade = db.session.query(
        Student.grade,
        func.count(AttendanceRecord.id).filter(AttendanceRecord.status == 'present').label('present_count'),
        func.count(AttendanceRecord.id).label('total_records')
    ).join(AttendanceRecord).filter(
        AttendanceRecord.date >= datetime(year, month, 1).date()
    ).group_by(Student.grade).all()
    
    return render_template('statistics.html',
                         monthly_stats=monthly_stats,
                         behavior_trends=behavior_trends,
                         grades=grades,
                         top_positive_students=top_positive_students,
                         attendance_by_grade=attendance_by_grade,
                         current_year=year,
                         current_month=month,
                         month_name=datetime(year, month, 1).strftime('%B %Y'))

@app.route('/api/attendance_chart_data')
@login_required
def attendance_chart_data():
    """API endpoint for attendance chart data"""
    year = request.args.get('year', datetime.now().year, type=int)
    
    # Get monthly data for the year
    monthly_data = []
    for month in range(1, 13):
        stats = get_monthly_attendance_stats(year, month)
        monthly_data.append({
            'month': datetime(year, month, 1).strftime('%B'),
            'attendance_rate': stats['attendance_rate'],
            'absence_rate': stats['absence_rate']
        })
    
    return jsonify(monthly_data)

@app.route('/api/behavior_chart_data')
@login_required
def behavior_chart_data():
    """API endpoint for behavior chart data"""
    student_id = request.args.get('student_id', type=int)
    months = request.args.get('months', 6, type=int)
    
    trends = get_behavior_trends(student_id=student_id, months=months)
    
    return jsonify(trends)

# Initialize default admin user
@app.before_first_request
def create_default_admin():
    """Create default admin user if no teachers exist"""
    if Teacher.query.count() == 0:
        admin = Teacher(
            username='admin',
            email='admin@school.com',
            name='مدير النظام',
            subject='إدارة',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("تم إنشاء حساب المدير الافتراضي: admin / admin123")

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
