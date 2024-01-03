import os
from flask import Flask, render_template, request, session, redirect, flash, current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename, send_from_directory, send_file
import json
from flask_mail import Mail

local_server = True
app = Flask(__name__, template_folder = 'template')
app.secret_key = 'super-secret-key'

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app.config['UPLOAD_FOLDER'] = params['upload_location']


if local_server == True:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['proud_uni']

db = SQLAlchemy()
db.init_app(app)

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)
mail = Mail(app)

# Tables
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), unique = False, nullable = False)
    email = db.Column(db.String(80), unique=False, nullable=False)
    phone = db.Column(db.String(80), unique=False, nullable=False)
    message = db.Column(db.String(180), unique=False, nullable=False)
    date =  db.Column(db.String(180), nullable=True)

class Projects(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(80), unique = False, nullable = False)
    description = db.Column(db.String(80), unique=False, nullable=False)
    img = db.Column(db.String(80), unique=False, nullable=False)
    link = db.Column(db.String(180), unique=False, nullable=False)

class Resume_exp(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    timeframe = db.Column(db.String(80), unique=False, nullable=False)
    position = db.Column(db.String(80), unique=False, nullable=False)
    company = db.Column(db.String(80), unique=False, nullable=False)
    city = db.Column(db.String(80), unique=False, nullable=False)
    description = db.Column(db.String(180), unique=False, nullable=False)

class Res_edu(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    timeframe = db.Column(db.String(80), unique=False, nullable=False)
    college = db.Column(db.String(80), unique=False, nullable=False)
    location = db.Column(db.String(80), unique=False, nullable=False)
    degree = db.Column(db.String(80), unique=False, nullable=False)
    field = db.Column(db.String(80), unique=False, nullable=False)
    description = db.Column(db.String(180), unique=False, nullable=False)

class Lang_class(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)

class Skill_class(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)



@app.route('/')
def home():
    return render_template('index.html', params = params)

@app.route('/projects')
def projects():
    project = Projects.query.filter_by().all()
    pro_count = Projects.query.count()
    return render_template('projects.html', project = project, pro_count = pro_count)

@app.route('/contact', methods = ['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contacts(name = name, email = email, phone = phone, message = message, date = datetime.now())
        db.session.add(entry)
        db.session.commit()

        mail.send_message("Message from" + name,
                          sender = email,
                          recipients = [params['gmail-user']],
                          body = message + '\n' + f"Phone: {phone}")
        flash("Message Sent Successfully", 'success')
    return render_template('contact.html', parmas  = params)



@app.route('/resume')
def resume():
    # Experience
    exp = Resume_exp.query.filter_by().all()
    edu = Res_edu.query.filter_by().all()
    skill = Skill_class.query.filter_by().all()
    lang = Lang_class.query.filter_by().all()
    skill_count = Skill_class.query.count()
    lang_count = Lang_class.query.count()
    exp_count = Resume_exp.query.count()
    edu_count = Res_edu.query.count()
    return render_template('resume.html', exp = exp, edu = edu, skill = skill, lang = lang, skill_count = skill_count, lang_count = lang_count, edu_count = edu_count, exp_count = exp_count)

@app.route('/dashboard', methods = ['GET','POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        return render_template('dashboard.html', params=params)
    if request.method == 'POST':
        username = request.form.get('username')
        user_pass = request.form.get('password')
        if username == params['admin_user'] and user_pass == params['admin_password']:
            session['user'] = username
            return render_template('dashboard.html', params = params)
    return render_template('login.html', prams = params)

@app.route('/manageprojects')
def manageprojects():
    project = Projects.query.filter_by().all()
    pro_count = Projects.query.count()
    return render_template('manageprojects.html', project = project, pro_count = pro_count)

@app.route('/manageresume')
def manageresume():
    project = Projects.query.filter_by().all()
    lang = Lang_class.query.filter_by().all()
    skill = Skill_class.query.filter_by().all()
    exp = Resume_exp.query.filter_by().all()
    edu = Res_edu.query.filter_by().all()
    skill_count = Skill_class.query.count()
    lang_count = Lang_class.query.count()
    exp_count = Resume_exp.query.count()
    edu_count = Res_edu.query.count()
    pro_count = Projects.query.count()
    return render_template('manageresume.html', project = project, lang = lang, skill = skill, skill_count = skill_count, lang_count = lang_count, edu = edu, exp = exp, edu_count = edu_count, exp_count = exp_count, pro_count = pro_count)

@app.route('/del/<string:sno>', methods = ['GET','POST'])
def skill_del(sno):
    lang = Lang_class.query.filter_by().all()
    skill_count = Skill_class.query.count()
    if skill_count > 0:
        if 'user' in session and session['user'] == params['admin_user']:
            sno = int(sno)
            del_skill = Skill_class.query.filter_by(sno=sno).first()
            db.session.delete(del_skill)
            db.session.commit()
    skill = Skill_class.query.filter_by().all()
    project = Projects.query.filter_by().all()
    return redirect("/manageresume")

@app.route('/lang_del/<string:sno>', methods = ['GET','POST'])
def lang_del(sno):
    lang = Lang_class.query.filter_by().all()
    lang_count = Lang_class.query.count()
    if lang_count > 0:
        if 'user' in session and session['user'] == params['admin_user']:
            sno = int(sno)
            del_skill = Lang_class.query.filter_by(sno=sno).first()
            db.session.delete(del_skill)
            db.session.commit()
    skill = Skill_class.query.filter_by().all()
    project = Projects.query.filter_by().all()
    return redirect("/manageresume")

@app.route('/add_lang', methods = ['GET','POST'])
def add_lang():
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            language = request.form.get('language')
            add = Lang_class(name = language)
            db.session.add(add)
            db.session.commit()
    return redirect("/manageresume")

@app.route('/add_skill', methods = ['GET','POST'])
def add_skill():
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            skill = request.form.get('skill')
            add = Skill_class(name = skill)
            db.session.add(add)
            db.session.commit()
    return redirect("/manageresume")

@app.route('/edu_del/<string:sno>', methods = ['GET','POST'])
def edu_del(sno):
    edu = Res_edu.query.filter_by().all()
    edu_count = Res_edu.query.count()
    if edu_count > 0:
        if 'user' in session and session['user'] == params['admin_user']:
            sno = int(sno)
            del_edu = Res_edu.query.filter_by(sno=sno).first()
            db.session.delete(del_edu)
            db.session.commit()
    skill = Skill_class.query.filter_by().all()
    project = Projects.query.filter_by().all()
    return redirect("/manageresume")

@app.route('/exp_del/<string:sno>', methods = ['GET','POST'])
def exp_del(sno):
    exp = Resume_exp.query.filter_by().all()
    exp_count = Resume_exp.query.count()
    if exp_count > 0:
        if 'user' in session and session['user'] == params['admin_user']:
            sno = int(sno)
            del_exp = Resume_exp.query.filter_by(sno=sno).first()
            db.session.delete(del_exp)
            db.session.commit()
    skill = Skill_class.query.filter_by().all()
    project = Projects.query.filter_by().all()
    return redirect("/manageresume")

@app.route('/add_exp', methods = ['GET','POST'])
def add_exp():
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            timeframe = request.form.get('Timeframe')
            position = request.form.get('position')
            company = request.form.get('company')
            city = request.form.get('city')
            description = request.form.get('description')
            add = Resume_exp(timeframe = timeframe, position = position, company = company, city = city, description = description)
            db.session.add(add)
            db.session.commit()
    return redirect("/manageresume")

@app.route('/add_edu', methods = ['GET','POST'])
def add_edu():
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            timeframe = request.form.get('Timeframe')
            college = request.form.get('college')
            location = request.form.get('location')
            degree = request.form.get('degree')
            field = request.form.get('field')
            description = request.form.get('description')
            add = Res_edu(timeframe = timeframe, college = college, location = location, degree = degree, field = field, description = description)
            db.session.add(add)
            db.session.commit()
    return redirect("/manageresume")

@app.route('/edit_exp/<string:sno>', methods = ['GET','POST'])
def edit_exp(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            timeframe = request.form.get('Timeframe')
            position = request.form.get('position')
            company = request.form.get('company')
            city = request.form.get('city')
            description = request.form.get('description')

            exp = Resume_exp.query.filter_by(sno = sno).first()

            exp.timeframe = timeframe
            exp.position = position
            exp.company = company
            exp.city = city
            exp.description = description
            db.session.commit()

        return redirect("/manageresume")

@app.route('/edit_edu/<string:sno>', methods = ['GET','POST'])
def edit_edu(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            timeframe = request.form.get('Timeframe')
            college = request.form.get('college')
            location = request.form.get('location')
            degree = request.form.get('degree')
            field = request.form.get('field')
            description = request.form.get('description')

            edu = Res_edu.query.filter_by(sno = sno).first()

            edu.timeframe = timeframe
            edu.college = college
            edu.location = location
            edu.degree = degree
            edu.field = field
            edu.description = description
            db.session.commit()

        return redirect("/manageresume")


@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            curr_dir = os.chdir(params['upload_location'])
            lis = os.listdir(curr_dir)

            for item in lis:
                if item == 'resume.pdf':
                    os.remove(params['upload_location']+'/'+item)

            f = request.files['file']


            if f.filename.endswith('.pdf'):
                f.filename = "resume.pdf"
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            else:
                flash("Invalid File Format", "danger")
                return redirect("/dashboard")
            flash("File Uploaded Successfully", "success")
            return redirect("/dashboard")

@app.route('/add_project', methods = ['GET', 'POST'])
def add_project():
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            curr_dir = os.chdir(params['upload_location'])
            image = request.files['image']
            title = request.form.get('title')
            description = request.form.get('description')
            link = request.form.get('link')

            if image.filename.endswith('.jpg') or image.filename.endswith('.png'):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                add = Projects(title=title, img=filename, link=link, description=description)
                db.session.add(add)
                db.session.commit()

            else:
                flash("Invalid File Format", "danger")
                return redirect("/manageprojects")
            flash("File Uploaded Successfully", "success")
            return redirect("/manageprojects")

@app.route('/del_pro/<string:sno>', methods = ['GET', 'POST'])
def del_pro(sno):
    if 'user' in session and session['user'] == params['admin_user']:

        sno = int(sno)
        item = Projects.query.filter_by(sno = sno).first()
        img_name = item.img
        curr_dir = os.chdir(params['upload_location'])
        lis= os.listdir(curr_dir)
        if img_name in lis:
            os.remove(img_name)
        db.session.delete(item)
        db.session.commit()
    flash("File Deleted Successfully", "success")
    return redirect("/manageprojects")

@app.route('/edit_project/<string:sno>', methods = ['GET','POST'])
def edit_project(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            curr_dir = os.chdir(params['upload_location'])
            image = request.files['image']
            title = request.form.get('title')
            description = request.form.get('description')
            link = request.form.get('link')
            project = Projects.query.filter_by(sno=sno).first()

            try:
                if image.filename.endswith('.jpg') or image.filename.endswith('.png'):
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    project.img = filename
                    db.session.commit()

                else:
                    flash("Invalid File Format", "danger")
                    return redirect("/manageprojects")

            finally:

                project.title = title
                project.description = description
                project.link = link
                db.session.commit()

            flash("Editted Successfully", "success")
            return redirect("/manageprojects")

@app.route('/download', methods=['GET', 'POST'])
def download():
    path = "C:\\Users\\Yash\\PycharmProjects\\Practice_Python\\Portfolio - YH\\static\\assets\\resume.pdf"
    return send_file(path, as_attachment=True, environ=request.environ)



@app.route("/logout")
def logout():
    session.pop('user')
    return render_template("login.html")


if __name__ == '__main__':
    app.run(debug = True)
