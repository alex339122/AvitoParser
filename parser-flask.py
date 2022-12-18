from flask import Flask, render_template, request, session, redirect, send_from_directory, jsonify
from avitoparser import full_parsing
from avitoparser import parsing_without_phones                            # escape - 
from mysql_wrapper import UseDataBase
from mysql.connector import Error
from functools import wraps
from datetime import datetime
import csv


app = Flask(__name__)


class AjaxPage():
    default_step = 100
    old_step = 0
    new_step = 0
    step = 50
    def do_refresh(self):
        if self.new_step != 0:
            self.old_step = self.new_step
        else:
            self.old_step = self.default_step
        self.new_step = self.old_step + self.step
    def do_reload(self):
        self.old_step = 0
        self.new_step = 0

page = AjaxPage()
parser_db = UseDataBase()


def exception_handler(err):
    time = 'Time: ' + str(datetime.now())
    ip = 'ip: ' + str(request.remote_addr)
    browser = 'Browser: ' + str(request.user_agent.browser)
    error = 'Error: ' + str(err)

    try:
        with open('errors.log', 'a') as errors:
            print(time, ip, browser, error, sep=' || ', file=errors)
    except:
        print(time, ip, browser, error, sep=' || ')


def check_status(func):
    @wraps(func)
    def wrapper(*args, **kwargs):        
        if 'logged_in' in session:
            return func(*args, **kwargs)
        return redirect('/login')
    return wrapper
app.secret_key = '#$Aqk^&45$$2oPfgHnmKloU5i99fG%$#'


def ask_DB(*args):
    try:
        cursor = parser_db.create_connection()    
        parser_db.query_insert(*args)
        contents = cursor.fetchall()
        parser_db.close()

        if len(contents) == 0:
            return False
        return contents
    except Error as e:
        exception_handler(e)


@app.route('/signin')
def do_signin():
    return render_template('signin.html')


@app.route('/login')
def do_login():
    return  render_template('login.html')


@app.route('/logout')
def do_logout():
    try:
        session.pop('logged_in')
        session.pop('name')
    except:
        text = 'Вы не в системе'
        return render_template('registration.html', the_text = text)
    text = 'Вы вышли из ситемы'
    return render_template('registration.html', the_text = text)


@app.route('/login_registration', methods = ['GET','POST'])
def check_registration():    
    if request.method == 'POST':
        username = request.form['login']
        password = request.form['password']

        _SQL = 'SELECT username FROM users WHERE username=%s'
        dbuser = ask_DB(_SQL, (username,))

        _SQL = 'SELECT password FROM users WHERE username=%s'
        dbpassword = ask_DB(_SQL, (username,))

        if dbuser:
            if password == dbpassword[0][0]:
                session['logged_in'] = True
                session['name'] = username
                return redirect('/entry')
            else:             
                text = 'Имя или пароль не верны'
                return render_template('registration.html', the_text = text)
        else:
            text = 'Такого пользователя не существует'
            return render_template('registration.html', the_text = text)

    return render_template('registration.html')


@app.route('/signin_registration', methods = ['GET','POST'])
def check_signin():
    if request.method == 'POST':
        username = request.form['login']
        password = request.form['password']

        if len(password) < 4 or len(username) < 4:
            text = 'Логин и пароль должны содержать не менее 4х символов'
            return render_template('signin.html',the_text=text)

        cursor = parser_db.create_connection()
        _SQL = 'SELECT username FROM users WHERE username=%s'
        parser_db.query_insert(_SQL, (username,))
        dbuser = cursor.fetchall()

        if dbuser:
            text = 'Имя "%s" занято' %username
            cursor.close()
            return render_template('signin.html',the_text=text)
            
        _SQL = 'INSERT INTO users (username, password) VALUES (%s, %s)'
        parser_db.query_insert(_SQL, (username, password))
        parser_db.close()

        session['logged_in'] = True 
        session['name'] = username

    return redirect('/entry')


@app.route('/')
@app.route('/entry')
@check_status
def entry_page():    
    return render_template('entry.html')


@app.route('/results', methods = ['POST','GET']) 
@check_status
def do_search():
    city = request.form['city']
    phrase = request.form['phrase']
    togle = request.form.get('phone_checkbox')

    if request.method == 'POST':
        if togle:
            try:
                full_parsing(city, phrase)
            except Exception as e:
                exception_handler(e)
                return "Error"
        else:
            try:
                parsing_without_phones(city, phrase)
            except Exception as e:
                exception_handler(e)
                return "Error"

    return render_template('results.html',  the_phrase = phrase.upper(),
                                            the_city = city.upper(),)


@app.route('/viewresults')
@check_status
def view_the_parse():
    titles = ('ID', 'Заголовок', 'Цена', 'Время', 'Место', 'Телефон', 'URL')

    cursor = parser_db.create_connection()
    _SQL_time = 'UPDATE parse SET time="Время размещения неизвестно" WHERE LENGTH(time) > 60'
    _SQL_phone = 'UPDATE parse SET phone="Неизвестно" WHERE LENGTH(phone) > 60'
    _SQL = 'SELECT * FROM parse WHERE id <= %s' %(page.default_step)

    parser_db.query_insert(_SQL_time)
    parser_db.query_insert(_SQL_phone)
    parser_db.query_insert(_SQL)

    data = cursor.fetchall()
    parser_db.close()

    page.do_reload()
    try:
        return render_template('viewresults.html', the_row_titles = titles,
                                                   the_data = data)
    except Exception as e:
        exception_handler(e)
        return 'Error'


@app.route('/viewresultsajax', methods = ['GET'])
def get_ajax_request():
    page.do_refresh()
    titles = ('ID', 'Заголовок', 'Цена', 'Время', 'Место', 'Номер телефона', 'URL')

    _SQL = 'SELECT * FROM parse WHERE id BETWEEN %s AND %s' %(page.old_step + 1, page.new_step)
    data = ask_DB(_SQL)

    if data:
        return render_template('new_ajax_results.html', the_row_titles = titles,
                                                        the_data = data,)
    page.do_reload()
    return jsonify(False)


@app.route('/downloads/<path:filename>')
@check_status
def download_results(filename):
    _SQL = 'SELECT phone FROM parse WHERE id=1'
    answer = ask_DB(_SQL)[0][0]

    if answer:
        titles = ('ID', 'Заголовок', 'Цена', 'Время', 'Место', 'Номер телефона', 'URL')
    else:
        titles = ('ID', 'Заголовок', 'Цена', 'Время', 'Место', 'URL')
        
    _SQL = 'SELECT * FROM parse'

    with open('results.csv', 'w') as results:
        writer = csv.writer(results, dialect='excel')
        writer.writerow(titles)
        writer.writerows(ask_DB(_SQL))

    return send_from_directory('', 'results.csv')


if __name__ == '__main__':
    app.run(debug=True)