from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from database_handler import DatabaseHandler

import os


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

db_handler = DatabaseHandler()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            message = "Les mots de passe ne correspondent pas."
            return render_template('register.html', error=message)

        if db_handler.check_user_exists(username):
            message = "Le nom d'utilisateur existe déjà."
            return render_template('register.html', error=message)

        try:
            db_handler.add_user(username, email, password)
            message = "Enregistrement réussi. Veuillez vous connecter."
            return render_template('login.html', success=message)
        except:
            message = "Erreur, veuillez réessayer."
            return render_template('register.html', error=message)

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if db_handler.check_user_exists(username) and db_handler.check_password(username, password):
            session['username'] = username
            return redirect('homepage')
        else:
            message = "Identifiant ou mot de passe incorrect."
            return render_template('login.html', error=message)

    return render_template('login.html')


@app.route('/homepage')
def homepage():

    if 'username' in session:

        username = session['username']
        print(username)
        current_interventions = db_handler.get_user_interventions(username)
        print(current_interventions)   
        return render_template('homepage.html', interventions=current_interventions)
    else:
        return redirect(url_for('login'))


@app.route('/add_intervention', methods=['GET', 'POST'])
def add_intervention():

    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = session['username']
        date = request.form['date']
        hour = request.form['hour']
        location = request.form['location']
        type = request.form['type']
        description = request.form['description']
        arrived = ""
        cr = ""
        endhour = ""

        try:
            db_handler.add_intervention(username, date, hour, location, type, description, arrived, cr, endhour)
            message = "Intervention ajoutée avec succès."
            redirect_url = url_for('homepage', success=message)
            return redirect(redirect_url)
        except:
            message = "Une erreur s'est produite lors de l'ajout de l'intervention."
            redirect_url = url_for('homepage', error=message)
            return redirect(redirect_url)

    return render_template('add_intervention.html')



if __name__ == '__main__':

    db_handler.init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)