from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random, time

app = Flask(__name__)
app.secret_key = 'secret123'

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
db = SQLAlchemy(app)

# MODELS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    attempts = db.Column(db.Integer)
    time_taken = db.Column(db.Float)

# GAME VARIABLES
secret_number = random.randint(1, 100)
attempts = 0
start_time = time.time()

# HOME
@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template('index.html')

# REGISTER
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(username=username).first():
            return "User already exists!"

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')

# LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()

        if user and check_password_hash(user.password, request.form['password']):
            session['user'] = user.id
            return redirect('/')
        else:
            return "Invalid credentials!"

    return render_template('login.html')

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# GUESS (AJAX)
@app.route('/guess', methods=['POST'])
def guess():
    global secret_number, attempts, start_time

    if 'user' not in session:
        return "Login required"

    user_guess = int(request.form['guess'])
    attempts += 1

    if user_guess < secret_number:
        return "Too Low 😢"

    elif user_guess > secret_number:
        return "Too High 😲"

    else:
        time_taken = time.time() - start_time

        score = Score(
            user_id=session['user'],
            attempts=attempts,
            time_taken=time_taken
        )
        db.session.add(score)
        db.session.commit()

        secret_number = random.randint(1, 100)
        attempts = 0
        start_time = time.time()

        return "🎉 Correct!"

# LEADERBOARD
@app.route('/leaderboard')
def leaderboard():
    if 'user' not in session:
        return redirect('/login')

    scores = Score.query.order_by(Score.attempts).limit(10).all()
    return render_template('leaderboard.html', scores=scores)

# RUN
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)