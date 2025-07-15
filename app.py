from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'devkey')

# Database connection
conn = psycopg2.connect(
    dbname='blogdb', user='postgres', password='newpassword', host='localhost', port='5432'
)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM users WHERE username=%s", (username,))
            if cur.fetchone():
                flash('Username already exists')
            else:
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                conn.commit()
                flash('Signup successful! Please login.')
                return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            flash(f'Error: {e}')
        finally:
            cur.close()
    return render_template('signup.html')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/aboutme')
def aboutme():
    return render_template('aboutme.html')

@app.route('/blogs')
def blogs():
    cur = conn.cursor()
    cur.execute("SELECT username, title, content FROM blogs ORDER BY id DESC")
    blog_posts = cur.fetchall()
    cur.close()
    return render_template('blogs.html', blog_posts=blog_posts)

## Removed /services route and template as requested

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    message = None
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO blogs (username, title, content) VALUES (%s, %s, %s)", (session['username'], title, content))
            conn.commit()
            message = 'Blog added successfully!'
        except Exception as e:
            conn.rollback()
            message = f'Error: {e}'
        finally:
            cur.close()
    return render_template('dashboard.html', username=session['username'], message=message)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
