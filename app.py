from flask import Flask, render_template, request, url_for, redirect, session, flash, send_file
from flask_login import login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import csv, json
import time


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.sqlite3"
app.config["SECRET_KEY"] = "kertenkerem_is_the_best"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODEL SCHEMA FOR data.db


class PasswordManager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry_name = db.Column(db.String(100), nullable=False)
    site_url = db.Column(db.String(100), nullable=False)
    entry_username = db.Column(db.String(100), nullable=False)
    entry_password = db.Column(db.String(100), nullable=False)
    entry_notes = db.Column(db.String(100), nullable=False)
    is_hidden = db.Column(db.Integer(), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    is_manager = db.Column(db.Integer(), nullable=False)


def __init__(self, entry_name, site_url, entry_username, entry_password, entry_notes, is_hidden):
    self.entry_name = entry_name
    self.site_url = site_url
    self.entry_username = entry_username
    self.entry_password = entry_password
    self.entry_notes = entry_notes
    self.is_hidden = is_hidden


# Routes
# Route for handling the login page logic
""" @app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['email'] != 'admin@admin.com' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            return redirect("/pwmng")
    return render_template('login.html', error=error) """

@app.route('/',methods=["GET","POST"])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        con=sqlite3.connect("data.sqlite3")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from users where email=? and password=?",(email,password))
        data=cur.fetchone()


        if data:
            session["name"]=data["name"]
            session["email"]=data["email"]
            return redirect("/pwmng")
        else:
            flash("Username and Password Mismatch","danger")
    return render_template('login.html')


@app.route("/pwmng")
def index():
    passwordlist = PasswordManager.query.all()
    return render_template("index.html", passwordlist=passwordlist)


@app.route("/add", methods=["GET", "POST"])
def add_details():
    if request.method == "POST":
        entry_name = request.form["entry_name"]
        site_url = request.form["site_url"]
        entry_username = request.form["entry_username"]
        entry_password = request.form["entry_password"]
        entry_notes = request.form["entry_notes"]
#       is_hidden = request.form["is_hidden"]
        new_entry_password = PasswordManager(entry_name=entry_name,site_url=site_url,entry_username=entry_username,entry_password=entry_password,entry_notes=entry_notes)
        
        db.session.add(new_entry_password)
        db.session.commit()
        return redirect("/pwmng")


@app.route("/update/<int:id>", methods=["GET","POST"])
def updated_details(id):
    updated_details = PasswordManager.query.get_or_404(id)
    if request.method == "POST":
        updated_details.entry_name = request.form["entry_name"]
        updated_details.site_url = request.form["site_url"]
        updated_details.entry_username = request.form["entry_username"]
        updated_details.entry_password = request.form["entry_password"]
        updated_details.entry_notes = request.form["entry_notes"]
#       updated_details.is_hidden = request.form["is_hidden"]
        try:
            db.session.commit()
            return redirect("/pwmng")
        except Exception:
            return "there was an error updating details"
    return render_template("update.html", updated_details=updated_details)


@app.route("/delete/<int:id>")
def delete_details(id):
    new_details_to_delete = PasswordManager.query.get_or_404(id)
    try:
        db.session.delete(new_details_to_delete)
        db.session.commit()
        return redirect("/")
    except Exception:
        return "there was an error deleting details"
    
    
@app.route("/export")
def export_data():
    on_time = time.strftime("%d.%m.%Y-%H%M%S")
    with open (f"Password_List{on_time}.csv","w") as f:
        out = csv.writer(f)
        out.writerow(["id","entry_name","site_url","entry_username","entry_password","entry_notes"])
        for item in PasswordManager.query.filter_by(is_hidden=0):
            #if item.is_hidden == 0:
            out.writerow([item.id, item.entry_name, item.site_url, item.entry_username, item.entry_password, item.entry_notes])
    return send_file(f"./Password_List{on_time}.csv", as_attachment=True)


@app.route('/logout',methods =["POST"] )
def logout():
    session.clear()
    flash('You were logged out.')
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
