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


@app.route('/disconnect')
def disconnect():

    session.clear()
    return redirect(url_for('login'))


@app.route('/homepage')
def homepage():

    if 'username' in session:

        username = session['username']
        current_interventions = db_handler.get_user_interventions(username)

        if 'success' in request.args:
            return render_template('homepage.html', interventions=current_interventions, success=request.args.get('success'))
        elif 'error' in request.args:
            return render_template('homepage.html', interventions=current_interventions, error=request.args.get('error'))
        else:
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


@app.route('/complete', methods=['GET', 'POST'])
def complete():

    if 'username' not in session:
                return redirect(url_for('login'))

    if request.method == 'GET':

        intervention_id = request.args.get('intervention_id')
        success = request.args.get('success')
        error = request.args.get('error')

        intervention = db_handler.get_intervention_by_id(intervention_id)
        persons_count = len(db_handler.get_person_interventions(intervention_id))

        return render_template('complete_page.html', intervention=intervention, persons=persons_count, success=success, error=error)

    if request.method == 'POST':

        intervention_id = request.form['intervention_id']
        arrived = request.form['arrived']
        cr = request.form['cr']
        endhour = request.form['endhour']

        print(intervention_id, arrived, cr, endhour)

        try:
            if db_handler.update_intervention(intervention_id, arrived, cr, endhour):
                message = "Intervention complétée avec succès."
                redirect_url = url_for('homepage', success=message)
                return redirect(redirect_url)
            else:
                message = "Une erreur est survenue."
                redirect_url = url_for('homepage', error=message)
                return redirect(redirect_url)
        except:
            message = "Une erreur est survenue."
            redirect_url = url_for('homepage', error=message)
            return redirect(redirect_url)
         

@app.route('/add_person', methods=['GET', 'POST'])
def add_person():

    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        
        intervention_id = request.args.get('intervention_id')
        return render_template('add_person.html', intervention_id=intervention_id)

    if request.method == 'POST':

        intervention_id = request.form['intervention_id']
        fullname = request.form['fullname']
        birthdate = request.form['birthdate']
        place_of_birth = request.form['place_of_birth']
        location = request.form['location']
        phone = request.form['phone']
        complement = request.form['complement']

        try:
            db_handler.add_person(intervention_id, fullname, birthdate, place_of_birth, location, phone, complement)
            message = "Personne ajoutée avec succès."
            redirect_url = url_for('complete', success=message, intervention_id=intervention_id)
            return redirect(redirect_url)
        except:
            message = "Une erreur est survenue."
            redirect_url = url_for('homepage', error=message)
            return redirect(redirect_url)


@app.route('/view_persons')
def view_persons():

    if 'username' not in session:
            return redirect(url_for('login'))

    if request.method == 'GET':
        if 'success' in request.args:
            intervention_id = request.args.get('intervention_id')
            success = request.args.get('success')
            if len(db_handler.get_person_interventions(intervention_id)) > 0:
                persons_list = db_handler.get_person_interventions(intervention_id)
                return render_template('view_persons.html', intervention_id=intervention_id, persons_list=persons_list, success=success)
            else:
                return render_template('view_persons.html', intervention_id=intervention_id, success=success)
            
        elif 'error' in request.args:
            intervention_id = request.args.get('intervention_id')
            error = request.args.get('error')
            if len(db_handler.get_person_interventions(intervention_id)) > 0:
                persons_list = db_handler.get_person_interventions(intervention_id)
                return render_template('view_persons.html', intervention_id=intervention_id, persons_list=persons_list, error=error)
            else:
                return render_template('view_persons.html', intervention_id=intervention_id, error=error)

        else:
            intervention_id = request.args.get('intervention_id')
            if len(db_handler.get_person_interventions(intervention_id)) > 0:
                persons_list = db_handler.get_person_interventions(intervention_id)
                return render_template('view_persons.html', intervention_id=intervention_id, persons_list=persons_list)
            else:
                return render_template('view_persons.html', intervention_id=intervention_id)
            


@app.route('/delete_page')
def delete_page():

    if 'username' not in session:
            return redirect(url_for('login'))

    intervention_id = request.args.get('intervention_id')
    return render_template('delete_page.html', id=intervention_id)


@app.route('/delete')
def delete():

    if 'username' not in session:
                return redirect(url_for('login'))

    id = request.args.get('id')
    print(id)

    try:
        db_handler.delete_intervention_persons(id)
        
        if db_handler.delete_user_intervention(id):
            message = "Intervention supprimée."
            redirect_url = url_for('homepage', success=message)
            return redirect(redirect_url)
        else:
            message = "Intervention inexistante."
            redirect_url = url_for('homepage', error=message)
            return redirect(redirect_url)
        
    except:
        message = "Une erreur est survenue"
        redirect_url = url_for('homepage', error=message)
        return redirect(redirect_url)


@app.route('/delete_person')
def delete_person():

    if 'username' not in session:
        return redirect(url_for('login'))

    if 'inter_id' in request.args:
        inter_id = request.args.get('inter_id')
        redirect_url = url_for('view_persons', intervention_id=inter_id)
        return redirect(redirect_url)
    
    elif 'del_person' in request.args:
        person_name = request.args.get('del_person')
        intervention_id = request.args.get('reload_inter_id')

        try:
            if db_handler.delete_persons(person_name):
                message = "Personne supprimée avec succes."
                redirect_url = url_for('view_persons', success=message, intervention_id=intervention_id)
                return redirect(redirect_url)
            else:
                message = "Personne introuvable."
                redirect_url = url_for('view_persons', error=message, intervention_id=intervention_id)
                return redirect(redirect_url)
        except:
            message = "Personne introuvable."
            redirect_url = url_for('view_persons', error=message, intervention_id=intervention_id)
            return redirect(redirect_url)
            

    else:
        person_name = request.args.get('person_name')
        intervention_id = request.args.get('intervention_id')
        return render_template('delete_person.html', person_name=person_name, intervention_id=intervention_id)




if __name__ == '__main__':

    db_handler.init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)