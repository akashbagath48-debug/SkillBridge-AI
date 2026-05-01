
from flask import send_from_directory
from flask import Flask, render_template, request, redirect, session
from flask_mail import Mail, Message
import random
import mysql.connector
import os
import PyPDF2
from openai import OpenAI

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'

app.config['MAIL_PORT'] = 587

app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = 'akashbagath48@gmail.com'

app.config['MAIL_PASSWORD'] = 'qxux zqjn jmax vohw'

mail = Mail(app)



db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root123",
    database="skillbridge",
    auth_plugin='mysql_native_password'

)

cursor = db.cursor(dictionary=True, buffered=True)


app.secret_key = "skillbridge_secret"

UPLOAD_FOLDER = 'uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# =========================
# GROQ AI CONFIGURATION
# =========================

client = OpenAI(
 GROQ_API_KEY = "YOUR_GROQ_API_KEY",
    base_url="https://api.groq.com/openai/v1"
)


# =========================
# HOME PAGE
# =========================

@app.route('/')
def home():
    return render_template("index.html")


# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        sql = "SELECT * FROM users WHERE username=%s AND password=%s"

        values = (username, password)

        cursor.execute(sql, values)

        user = cursor.fetchone()

        if user:

            session['username'] = username

            return redirect('/dashboard')

        else:

            return "Invalid Username or Password"

    return render_template("login.html")

if __name__ == '__main__':

 @app.route('/send_login_otp', methods=['POST'])
 def send_login_otp():

    email = request.form['email']

    sql = "SELECT * FROM users WHERE email=%s"

    cursor.execute(sql, (email,))

    user = cursor.fetchone()

    if not user:

        return "Email Not Registered"

    otp = random.randint(1000, 9999)

    session['login_otp'] = str(otp)

    session['login_email'] = email

    msg = Message(

        'SkillBridge AI Login OTP',

        sender=app.config['MAIL_USERNAME'],

        recipients=[email]
    )

    msg.body = f'Your Login OTP is: {otp}'

    mail.send(msg)

    return redirect('/verify_login_otp')

@app.route('/verify_login_otp', methods=['GET', 'POST'])
def verify_login_otp():

    if request.method == 'POST':

        entered_otp = request.form['otp']

        if entered_otp == session['login_otp']:

            email = session['login_email']

            sql = "SELECT * FROM users WHERE email=%s"

            cursor.execute(sql, (email,))

            user = cursor.fetchone()

            session['username'] = user['username']

            return redirect('/dashboard')

        else:

            return "Invalid OTP"

    return render_template('verify_login_otp.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        sql = """
        SELECT * FROM admin
        WHERE username=%s
        AND password=%s
        """

        cursor.execute(sql, (username, password))

        admin = cursor.fetchone()

        if admin:

            session['admin'] = username

            return redirect('/admin_dashboard')

        else:

            return "Invalid Admin Credentials"

    return render_template('admin_login.html')


@app.route('/admin_support')
def admin_support():

    if 'admin' in session:

        sql = "SELECT * FROM support_messages ORDER BY id DESC"

        cursor.execute(sql)

        tickets = cursor.fetchall()

        return render_template(
            'admin_support.html',
            tickets=tickets
        )

    return redirect('/admin_login')

if __name__ == '__main__':

 @app.route('/reply_ticket/<int:id>', methods=['POST'])
 def reply_ticket(id):

    if 'admin' in session:

        admin_reply = request.form['admin_reply']

        sql = """
        UPDATE support_messages
        SET admin_reply=%s
        WHERE id=%s
        """

        values = (
            admin_reply,
            id
        )

        cursor.execute(sql, values)

        db.commit()

        return redirect('/admin_support')

    return redirect('/admin_login')   





# =========================
# DASHBOARD
# =========================

@app.route('/dashboard')
def dashboard():

    if 'username' in session:

        username = session['username']

        sql = "SELECT * FROM users WHERE username=%s"

        cursor.execute(sql, (username,))

        user = cursor.fetchone()

        return render_template(
            "dashboard.html",
            username=username,
            user=user
        )

    return redirect('/login')

@app.route('/admin_dashboard')
def admin_dashboard():

    if 'admin' in session:

        sql = "SELECT * FROM users"

        cursor.execute(sql)

        users = cursor.fetchall()

        return render_template(
            'admin_dashboard.html',
            users=users
        )

    return redirect('/admin_login')


@app.route('/delete_user/<int:id>')
def delete_user(id):

    if 'admin' in session:

        sql = "DELETE FROM users WHERE id=%s"

        cursor.execute(sql, (id,))

        db.commit()

        return redirect('/admin_dashboard')

    return redirect('/admin_login')

# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    session.pop('username', None)

    return redirect('/login')


# =========================
# REGISTER
# =========================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        sql = """
        INSERT INTO users(username,email,password)
        VALUES(%s,%s,%s)
        """

        values = (username, email, password)

        cursor.execute(sql, values)

        db.commit()

        return f"User {username} Registered Successfully"

    return render_template("register.html")


if __name__ == '__main__':

 @app.route('/support', methods=['GET', 'POST'])
 def support():

    if 'username' in session:

        username = session['username']

        sql = "SELECT * FROM users WHERE username=%s"

        cursor.execute(sql, (username,))

        user = cursor.fetchone()

        if request.method == 'POST':

            subject = request.form['subject']

            message = request.form['message']

            sql = """
            INSERT INTO support_messages
            (username,email,subject,message)
            VALUES(%s,%s,%s,%s)
            """

            values = (
                username,
                user['email'],
                subject,
                message
            )

            cursor.execute(sql, values)

            db.commit()

        sql = """
        SELECT * FROM support_messages
        WHERE username=%s
        ORDER BY id DESC
        """

        cursor.execute(sql, (username,))

        tickets = cursor.fetchall()

        return render_template(
            'support.html',
            username=username,
            user=user,
            tickets=tickets
        )

    return redirect('/login') 

# =========================
# RESUME UPLOAD + ANALYZER
# =========================

@app.route('/upload', methods=['GET', 'POST'])
def upload():

    extracted_text = ""

    detected_skills = []

    skills = [
        "Python",
        "Java",
        "SQL",
        "HTML",
        "CSS",
        "JavaScript",
        "Flask",
        "Django",
        "React"
    ]

    if request.method == 'POST':

        file = request.files['resume']

        if file:

            filepath = os.path.join(
                app.config['UPLOAD_FOLDER'],
                file.filename
            )

            file.save(filepath)

            with open(filepath, 'rb') as pdf_file:

                reader = PyPDF2.PdfReader(pdf_file)

                for page in reader.pages:

                    extracted_text += page.extract_text()

            for skill in skills:

                if skill.lower() in extracted_text.lower():

                    detected_skills.append(skill)

            score = int(
                (len(detected_skills) / len(skills)) * 100
            )

            missing_skills = []

            for skill in skills:

                if skill not in detected_skills:

                    missing_skills.append(skill)

            return render_template(
                "result.html",
                skills=detected_skills,
                score=score,
                missing_skills=missing_skills
            )

    return render_template("upload.html")


# =========================
# AI CHATBOT
# =========================

@app.route('/chatbot', methods=['POST'])
def chatbot():

    user_message = request.form['message']

    username = session['username']

    sql = "SELECT * FROM users WHERE username=%s"

    cursor.execute(sql, (username,))

    user = cursor.fetchone()

    try:

        chat_completion = client.chat.completions.create(

            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ],

            model="llama-3.3-70b-versatile"
        )

        bot_response = (
            chat_completion
            .choices[0]
            .message
            .content
        )

    except Exception as e:

        bot_response = f"AI Error: {str(e)}"

    return render_template(
        "dashboard.html",
        user_message=user_message,
        bot_response=bot_response,
        username=username,
        user=user
    )

@app.route('/interview_ai', methods=['POST'])
def interview_ai():

    user_message = request.form['interview_message']

    username = session['username']

    sql = "SELECT * FROM users WHERE username=%s"

    cursor.execute(sql, (username,))

    user = cursor.fetchone()

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

                {
                    "role": "system",
                    "content": """
                    You are InterviewGPT.

                    Help users with:
                    - Technical interview questions
                    - HR interview preparation
                    - Coding rounds
                    - SQL queries
                    - Python explanations
                    - Resume preparation
                    - Placement guidance

                    Answer professionally like ChatGPT.
                    """
                },

                {
                    "role": "user",
                    "content": user_message
                }

            ]
        )

        interview_response = (
            response
            .choices[0]
            .message
            .content
        )

    except Exception as e:

        interview_response = (
            f"AI Error: {str(e)}"
        )

    return render_template(
        "dashboard.html",
        interview_response=interview_response,
        username=username,
        user=user
    )

@app.route('/coding')
def coding():

    questions = [

        {
            "title": "Two Sum",
            "difficulty": "Easy",
            "link": "https://leetcode.com/problems/two-sum/"
        },

        {
            "title": "Valid Parentheses",
            "difficulty": "Easy",
            "link": "https://leetcode.com/problems/valid-parentheses/"
        },

        {
            "title": "Merge Sorted Array",
            "difficulty": "Medium",
            "link": "https://leetcode.com/problems/merge-sorted-array/"
        },

        {
            "title": "SQL Employee Query",
            "difficulty": "Medium",
            "link": "https://leetcode.com/problemset/database/"
        }

    ]

    return render_template(
        "coding.html",
        questions=questions
    )


@app.route('/profile', methods=['POST'])
def profile():

    if 'username' in session:

        username = session['username']

        college = request.form['college']

        college_address = request.form['college_address']

        degree = request.form['degree']

        passing_year = request.form['passing_year']

        skills = request.form['skills']

        bio = request.form['bio']

        image = request.files['profile_image']

        image_name = ""

        if image:

            image_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                image.filename
            )

            image.save(image_path)

            image_name = image.filename

        sql = """
        UPDATE users
        SET
        profile_image=%s,
        college=%s,
        college_address=%s,
        degree=%s,
        passing_year=%s,
        skills=%s,
        bio=%s
        WHERE username=%s
        """

        values = (
            image_name,
            college,
            college_address,
            degree,
            passing_year,
            skills,
            bio,
            username
        )

        cursor.execute(sql, values)

        db.commit()

    return redirect('/dashboard')

@app.route('/uploads/<filename>')
def uploaded_file(filename):

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )


@app.route('/view_profile')
def view_profile():

    if 'username' in session:

        username = session['username']

        sql = "SELECT * FROM users WHERE username=%s"

        cursor.execute(sql, (username,))

        user = cursor.fetchone()

        return render_template(
            "view_profile.html",
            user=user,
            username=username
        )

    return redirect('/login')


@app.route('/edit_profile')
def edit_profile():

    if 'username' in session:

        username = session['username']

        sql = "SELECT * FROM users WHERE username=%s"

        cursor.execute(sql, (username,))

        user = cursor.fetchone()

        return render_template(
            "edit_profile.html",
            user=user
        )

    return redirect('/login')

# =========================
# RUN FLASK
# =========================

if __name__ == '__main__':
    app.run(debug=True)