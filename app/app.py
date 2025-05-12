from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import User, Event
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

# local import
from models import db, User

app = Flask(__name__)
app.secret_key = 'SOME_SECRET_KEY'

# Config inline
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db + migrate
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/aboutus')
def aboutus():
    return render_template('about_us.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name= request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for('register'))

        new_user = User(email=email, password=hashed_pw,name=name)
        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully! Please login.")
        return redirect(url_for('login'))

    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user'] = user.email
            session['user_id'] = user.id   # Add this line
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials.")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session.get('user_id')

    now = datetime.now()

    # Add/Edit Event
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        title = request.form['title']
        event_datetime = datetime.strptime(request.form['datetime'], '%Y-%m-%dT%H:%M')

        if event_id:
            event = Event.query.get(int(event_id))
            if event and event.user_id == user_id:
                event.title = title
                event.datetime = event_datetime
        else:
            db.session.add(Event(title=title, datetime=event_datetime, user_id=user_id))

        db.session.commit()
        return redirect('/dashboard')

    # Delete Event
    delete_id = request.args.get('delete')
    if delete_id:
        event = Event.query.get(int(delete_id))
        if event and event.user_id == user_id:
            db.session.delete(event)
            db.session.commit()
        return redirect('/dashboard')

    # Fetch Events
    events = Event.query.filter_by(user_id=user_id).order_by(Event.datetime).all()
    upcoming_events = [e for e in events if now <= e.datetime <= now + timedelta(days=1)][:5]

    total_events = len(events)
    events_today = sum(1 for e in events if e.datetime.date() == now.date())
    past_events = sum(1 for e in events if e.datetime < now)

    return render_template('dashboard.html',
                           user=session['user'],
                           all_events=events,
                           upcoming_events=upcoming_events,
                           total_events=total_events,
                           events_today=events_today,
                           past_events=past_events)




@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))
    
if __name__ == '__main__':
    app.run(debug=True)
