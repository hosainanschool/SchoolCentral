from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional
from models import Teacher, Student
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])

class TeacherForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    name = StringField('الاسم الكامل', validators=[DataRequired(), Length(max=100)])
    subject = StringField('المادة', validators=[Optional(), Length(max=100)])
    phone = StringField('رقم الهاتف', validators=[Optional(), Length(max=20)])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=6)])
    is_admin = BooleanField('مدير النظام')
    
    def validate_username(self, username):
        teacher = Teacher.query.filter_by(username=username.data).first()
        if teacher:
            raise ValidationError('اسم المستخدم موجود بالفعل. يرجى اختيار اسم آخر.')
    
    def validate_email(self, email):
        teacher = Teacher.query.filter_by(email=email.data).first()
        if teacher:
            raise ValidationError('البريد الإلكتروني موجود بالفعل. يرجى استخدام بريد آخر.')

class StudentForm(FlaskForm):
    student_id = StringField('رقم الطالب', validators=[DataRequired(), Length(max=20)])
    name = StringField('اسم الطالب', validators=[DataRequired(), Length(max=100)])
    grade = StringField('الصف', validators=[DataRequired(), Length(max=20)])
    class_name = StringField('الفصل', validators=[DataRequired(), Length(max=50)])
    birth_date = DateField('تاريخ الميلاد', validators=[Optional()])
    parent_name = StringField('اسم ولي الأمر', validators=[Optional(), Length(max=100)])
    parent_phone = StringField('هاتف ولي الأمر', validators=[Optional(), Length(max=20)])
    address = TextAreaField('العنوان', validators=[Optional()])
    enrollment_date = DateField('تاريخ التسجيل', validators=[Optional()], default=date.today)
    is_active = BooleanField('نشط', default=True)
    
    def validate_student_id(self, student_id):
        student = Student.query.filter_by(student_id=student_id.data).first()
        if student:
            raise ValidationError('رقم الطالب موجود بالفعل. يرجى استخدام رقم آخر.')

class AttendanceForm(FlaskForm):
    date = DateField('التاريخ', validators=[DataRequired()], default=date.today)
    status = SelectField('حالة الحضور', 
                        choices=[('present', 'حاضر'), ('absent', 'غائب'), ('late', 'متأخر'), ('excused', 'غياب بعذر')],
                        validators=[DataRequired()])
    notes = TextAreaField('ملاحظات', validators=[Optional()])

class BehaviorReportForm(FlaskForm):
    date = DateField('التاريخ', validators=[DataRequired()], default=date.today)
    behavior_type = SelectField('نوع السلوك',
                               choices=[('positive', 'إيجابي'), ('negative', 'سلبي'), ('neutral', 'محايد')],
                               validators=[DataRequired()])
    category = SelectField('التصنيف',
                          choices=[('discipline', 'انضباط'), ('academic', 'أكاديمي'), ('social', 'اجتماعي'), 
                                  ('participation', 'مشاركة'), ('respect', 'احترام'), ('other', 'أخرى')],
                          validators=[DataRequired()])
    description = TextAreaField('الوصف', validators=[DataRequired()])
    severity = SelectField('الخطورة',
                          choices=[(1, '1 - بسيط'), (2, '2 - متوسط'), (3, '3 - مهم'), (4, '4 - خطير'), (5, '5 - شديد الخطورة')],
                          coerce=int, validators=[DataRequired()])
    action_taken = TextAreaField('الإجراء المتخذ', validators=[Optional()])
    parent_notified = BooleanField('تم إبلاغ ولي الأمر')

class SearchForm(FlaskForm):
    student_name = StringField('اسم الطالب')
    grade = StringField('الصف')
    class_name = StringField('الفصل')
    date_from = DateField('من تاريخ')
    date_to = DateField('إلى تاريخ')
