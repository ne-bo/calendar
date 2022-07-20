from flask import Flask, render_template, request, flash, url_for, redirect

from backend import CalendarManager
from validation_utils import validate_the_input_data

frontend = Flask(__name__)
frontend.config['SECRET_KEY'] = 'your secret key'

backend = CalendarManager()
# if you don't have availabilities in your database we create one for you, feel free to change this part
# the web interface for availabilities creation is coming
if len(backend.get_all_availabilities()) == 0:
    backend.create_availability('2022-11-01-15-00', '2022-11-02-15-00')


@frontend.route('/')
def index():
    backend = CalendarManager()
    return render_template('index.html',
                           availabilities=backend.get_all_availabilities(),
                           reservations=backend.get_all_reservations())


@frontend.route('/create', methods=('GET', 'POST'))
def create():
    backend = CalendarManager()

    if request.method == 'POST':
        title = request.form['title']
        email = request.form['email']
        start = request.form['start']
        end = request.form['end']

        validation_output = validate_the_input_data(title, email, start, end)

        if not validation_output == '':
            flash(validation_output)
        else:
            try:
                with backend.database:
                    backend.create_reservation(start, end, title, email)
                return redirect(url_for('index'))
            except ValueError as e:
                flash(e)
    return render_template('create.html',
                           availabilities=backend.get_all_availabilities(),
                           reservations=backend.get_all_reservations())


@frontend.route('/remove', methods=('GET', 'POST'))
def remove():
    backend = CalendarManager()

    if request.method == 'POST':
        email = request.form['email']
        start = request.form['start']
        end = request.form['end']

        validation_output = validate_the_input_data('', email, start, end)

        if not validation_output == '':
            flash(validation_output)
        else:
            try:
                with backend.database:
                    backend.remove_reservation(start, end, email)
                return redirect(url_for('index'))
            except ValueError as e:
                flash(e)
    return render_template('remove.html',
                           availabilities=backend.get_all_availabilities(),
                           reservations=backend.get_all_reservations())
