from werkzeug.security import generate_password_hash

if __name__ == '__main__':
    # إضافة بيانات وهمية (ضع هذا قبل if __name__ == '__main__')
    def add_sample_data():
        with app.app_context():
            # حذف البيانات القديمة أولًا (اختياري)
            db.drop_all()
            db.create_all()

            # إضافة 5 معلمين
            teachers = [
                User(username="teacher1", password=generate_password_hash("pass1"), role="teacher"),
                User(username="teacher2", password=generate_password_hash("pass2"), role="teacher"),
                User(username="teacher3", password=generate_password_hash("pass3"), role="teacher")
            ]

            # إضافة 10 طلاب
            students = [
                User(username="student1", password=generate_password_hash("s_pass1"), role="student"),
                User(username="student2", password=generate_password_hash("s_pass2"), role="student")
            ]

            db.session.add_all(teachers + students)
            db.session.commit()
            print("تمت إضافة البيانات بنجاح!")

    # استدعاء الدالة عند التشغيل (اختياري)
    add_sample_data()
    app.run(host='0.0.0.0', port=5000, debug=True)
@app.route('/teachers')
def show_teachers():
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('teachers.html', teachers=teachers)