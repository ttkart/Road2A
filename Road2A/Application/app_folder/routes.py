from flask import Flask, render_template, redirect, request
from app_folder import app, db
from .forms import LoginForm, RegistrationForm, AppointmentForm, SettingsForm
from .models import User, Availability, Appointments
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import sqlite3


@app.route("/")
def hello():
    """
        Displays the general home page, "Home.html"
    """
    if current_user.is_authenticated:
        return redirect('/Home-Login')
    return render_template('Home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ 
        Displays the login page, "login.html", using "LoginForm()"
        
        Check cross checks credential with database when user enter a username and password.
    """
    if current_user.is_authenticated:
        return redirect('/Home-Login')
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # If user exists in database
        if user:
            # Validates if non-hashed password is equal to the password input when creating account
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect('/Home-Login')
            else:
                return '<h1> Invalid login! </h1>'
        else:
            return '<h1> User does not exist! </h1>' 
    return render_template('login.html', form=form)

@app.route('/create_account', methods=['GET', 'POST'])
def reg():
    """
        Displays the account creation page, "CreateAccount.html"
        When a new user enters their data the data is saved and pushed to the database.
    """
    if current_user.is_authenticated:
        return redirect('/Home-Login')
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('CreateAccount.html', form=form)

# Requires user to login before accessing the "dashboard"
@app.route('/Home-Login')
@login_required
def Home():
    """
        Displays the home page, "Home-Login.html", with the current user
    """
    # Connects to sqlite3 database
    conn = sqlite3.connect('app.db')
    c = conn.cursor()

    # Get all rows in "user" table and assigns it to "records"
    select_query = """SELECT * from availability"""
    c.execute(select_query)
    records = c.fetchall()
    
    # Determine if the user exists in database by checking the each row's column in the 1th index
    time_range = meeting_length = None
    for row in records:
        if row[1] == current_user.username:
            name = row[1]
            time_range = row[2]
            meeting_length = row[3]
    
    # Check for appointments made with creator
    select_query = """SELECT * from appointments"""
    c.execute(select_query)
    appts = c.fetchall()

    # List of appointments for the creator
    students = []
    for row in appts:
        if row[1] == current_user.username:
            info = []
            info.append(row[2]) # Name
            info.append(row[3]) # Email
            info.append(row[4]) # Time
            students.append(info)
    
    # Close the cursor
    c.close()

    return render_template('Home-Login.html', name = current_user.username, time_Range = time_range, meeting_Length = meeting_length, appts = students)

# Log-out
@app.route('/logout')
@login_required
def logout():
    """
        Logs the current user out and redirects to the general home page, "Home.html"
    """
    logout_user()
    return redirect('/')

# Dynamic routes
@app.route('/<username>')
def profile(username):
    """
        Shows the guest-user side of the creator's page using dynamic links
    """

    # Check to see if user exists
    if User.query.filter_by(username=username).first() == None:
        return ' User does not exist in database '

    # Search for the user's availability by checking the user's row in database
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    select_query = """SELECT * from availability"""
    c.execute(select_query)
    timing = c.fetchall()
    
    name = time_range = meeting_length = None
    for row in timing:
        if row[1] == username:
            name = row[1]
            time_range = row[2]
            meeting_length = row[3]
    
    # Determine if time range and or meeting length has been set up by the creator yet
    if time_range == None:
        time_range = "Time Range not set up yet!"
    else:
        time_range += " PST"

    if meeting_length == None:
        meeting_length = "Time Length not set up yet!"
    else:
        meeting_length += " minutes"

    return render_template('dynamic.html', name = username, availability = time_range, time = meeting_length)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
        Settings page that allow user to change availability, email preferance, and delete account.
    """
    form = SettingsForm()

    if form.validate_on_submit():
        available = Availability(name = current_user.username, time_Range=form.time_Range.data, meeting_Length=form.meeting_Length.data)
        db.session.add(available)
        db.session.commit()
        
    return render_template('settings.html', form = form)

@app.route("/DeleteAccount")
@login_required
def delete():
    """
        Delete the current user's account.
    """
    db.session.delete(current_user)
    db.session.commit()
  
    return render_template('DeleteAccount.html')


# Setting up an Appointment and Confirmation Page afterwards
@app.route('/<username>/appointments/<date>')
@app.route('/<username>/appointments/<date>/Confirmation', methods=['POST'])
def appointments(username, date):
    """
        Guest Users can select a date on the calednar and sign up for a session with the creator
    """
    form = AppointmentForm()

    if form.validate_on_submit():
        appt = Appointments(creator = username, name = form.name.data, email = form.email.data, time = form.time.data)
        db.session.add(appt)
        db.session.commit()

        # Since the method in appointments.html is a POST we know to enter if statement when form is complete
        if request.method == 'POST':
            return render_template('Confirmation.html', name = username, date = date)

    return render_template('appointments.html', name = username, date = date, form = form)

@app.route("/emailConfirm")
def emailConfirm():
    """
        Goes to the email confirmation page. 
    """
    return render_template('emailConfirm.html')

@app.route("/splash")
def splash():
    """
        Goes to the splash page. 
    """
    return render_template('splash.html')