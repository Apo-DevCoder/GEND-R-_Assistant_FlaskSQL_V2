import sqlite3
from tools import hash_password, check_password


class DatabaseHandler:
    def __init__(self):

        self.path = "database.db"


    def init_db(self):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                date TEXT NOT NULL,
                hour TEXT NOT NULL,
                location TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT NOT NULL,
                arrived TEXT,
                cr TEXT,
                endhour TEXT
                )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intervention_id INTEGER NOT NULL,
                fullname TEXT NOT NULL,
                birthdate TEXT NOT NULL,
                place_of_birth TEXT NOT NULL,
                location TEXT NOT NULL,
                phone TEXT NOT NULL,
                complement TEXT
                )''')
        
        conn.commit()
        conn.close()


    def add_user(self, username, email, password):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password))
        conn.commit()
        conn.close()


    def get_user(self, username):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return user


    def check_user_exists(self, username):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return user is not None


    def check_password(self, username, password):
        user = self.get_user(username)
        if user:
            user_password = user[3]
            return check_password(password, user_password)
        return False


    def add_intervention(self, username, date, hour, location, type, description, arrived, cr, endhour):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO interventions (username, date, hour, location, type, description, arrived, cr, endhour) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (username, date, hour, location, type, description, arrived, cr, endhour,))
        conn.commit()
        conn.close()


    def get_user_interventions(self, username):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM interventions WHERE username = ? ORDER BY date ASC, hour ASC", (username,))
        interventions = cursor.fetchall()
        conn.close()
        return interventions


    def delete_user_intervention(self, intervention_id):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM interventions WHERE id = ?', (intervention_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0


    def get_intervention_by_id(self, intervention_id):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM interventions WHERE id = ?', (intervention_id,))
        intervention = cursor.fetchone()
        conn.close()
        return intervention


    def update_intervention(self, intervention_id, arrived, cr, endhour):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('UPDATE interventions SET arrived = ?, cr = ?, endhour = ? WHERE id = ?', (arrived, cr, endhour, intervention_id))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0


    def add_person(self, intervention_id, fullname, birthdate, place_of_birth, location, phone, complement):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO persons (intervention_id, fullname, birthdate, place_of_birth, location, phone, complement) VALUES (?, ?, ?, ?, ?, ?, ?)',
                            (intervention_id, fullname, birthdate, place_of_birth, location, phone, complement,))
        conn.commit()
        conn.close()


    def get_person_interventions(self, intervention_id):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM persons WHERE intervention_id = ?", (intervention_id,))
        persons = cursor.fetchall()
        conn.close()
        return persons


    def delete_intervention_persons(self, intervention_id):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM persons WHERE intervention_id = ?', (intervention_id,))
        conn.commit()
        conn.close()


    def get_person(self, person_name):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM persons WHERE fullname = ?', (person_name,))
        person = cursor.fetchone()
        conn.close()
        return person


    def update_person(self, fullname, birthdate, place_of_birth, location, phone, complement, person_id):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('UPDATE persons SET fullname = ?, birthdate = ?, place_of_birth = ?, location = ?, phone = ?, complement = ? WHERE id = ?', (fullname, birthdate, place_of_birth, location, phone, complement, person_id))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0


    def delete_persons(self, person_name):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM persons WHERE fullname = ?', (person_name,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0
