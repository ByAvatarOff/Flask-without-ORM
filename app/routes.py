"""
Flask app
version: 1.0
"""
import functools
from datetime import date

from flask import render_template, redirect, flash, session, g
from werkzeug.security import check_password_hash, generate_password_hash

import app.db as new_db
from app import app
from app.forms import LoginForm, RegisterForm, AddPositionForm, AddDepartmentForm, AddEmployeeForm, UpdateEmployeeForm


def login_required(view):
    """
    Decorator func for check if user is a login
    :param view:
    :return: func
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        """
        Wrapped func
        :param kwargs:
        :return: redirecting
        """
        if g.user is None:
            return redirect('/login')
        return view(**kwargs)
    return wrapped_view


@app.route('/register', methods=('GET', 'POST'))
def register():
    """
    Register user and generate password hash
    :return:
    """
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_db.create_update_delete_request('INSERT INTO user (username, password) VALUES (?, ?)',
                                            (username, generate_password_hash(password)))
        return redirect('/login')
    return render_template('auth/register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """
    Login user and redirect to main page
    :return: template
    """
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        db = new_db.get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        if not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect('/index')
        flash(error)
    return render_template('auth/login.html', form=form)


@app.before_request
def load_logged_in_user():
    """
    Checks if a user id is stored in the session and gets that user’s data from the database
    :return: None
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = new_db.get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@app.route('/logout')
def logout() -> Response:
    """
    Logout user
    :return: redirecting
    """
    session.clear()
    return redirect('/login')


@app.route('/index')
@login_required
def index():
    """
    View main page
    :return:
    """
    return render_template('index.html')


@app.route('/position/add', methods=['GET', 'POST'])
@login_required
def add_position():
    """
    Add position to Position table on db
    :return: template
    """
    form = AddPositionForm()
    if form.validate_on_submit():
        new_db.create_update_delete_request('INSERT INTO position (position_name, description)'
                                            'VALUES (?, ?)',
                                            (form.position_name.data, form.description.data))
        flash('You successful add position')
    return render_template('add view/add_delete_new_position.html', form=form)


@app.route('/position/delete/<int:position_id>', methods=['GET', 'POST'])
@login_required
def delete_position(position_id):
    # TODO: correct response if haven't a position
    """
    Delete position from Position table by position_id
    :param position_id: integer
    :return:
    """
    delete_request = new_db.create_update_delete_request('DELETE FROM position WHERE id = ?',
                                                         (position_id, ))
    if delete_request:
        return flash('You successful delete employee!')
    # return render_template('add delete view/add_delete_new_position.html')


@app.route('/department/add', methods=['GET', 'POST'])
@login_required
def add_department():
    """
    Add department to Department table on db
    :return: template
    """
    dep = new_db.select_requests('SELECT * FROM department')
    form = AddDepartmentForm()
    if form.validate_on_submit():
        new_db.create_update_delete_request('INSERT INTO department (department_name, parent_id)'
                                            'VALUES (?, ?)',
                                            (form.department_name.data, form.parent_id.data))
        flash('You successful add department')
    return render_template('add view/add_delete_new_department.html', form=form, department=dep)


@app.route('/department/delete/<int:department_id>', methods=['GET', 'POST'])
@login_required
def delete_department(department_id):
    """
    Delete position from Position table by position_id
    :param department_id: integer
    :return:
    """
    delete_request = new_db.create_update_delete_request('DELETE FROM department WHERE id = ?', (department_id, ))
    if delete_request:
        return flash('You successful delete department!')


@app.route('/employee/add',  methods=['GET', 'POST'])
@login_required
def add_employee():
    """
    Add new employee to Employee table on db
    :return: template
    """
    form = AddEmployeeForm()
    if form.validate_on_submit():
        new_db.create_update_delete_request('INSERT INTO employee (fio, position_id, department_id, date_start)'
                                            'VALUES (?, ?, ?, ?)',
                                            (form.fio.data, form.position_id.data, form.department_id.data,
                                             date.today()))
        flash('You successful add employee')
    return render_template('add view/add_delete_new_employees.html', form=form)


@app.route('/employee/delete/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def delete_employee(employee_id):
    """
    Delete position from Position table by position_id
    :param employee_id: integer
    :return:
    """
    delete_request = new_db.create_update_delete_request('DELETE FROM employee WHERE id = ?', (employee_id, ))
    if delete_request:
        return flash('You successful delete employee!')


def count_add(value_position, value_department, employee_id, form):
    if int(value_position) != int(form.position_id.data):
        new_db.create_update_delete_request('UPDATE count_dep_pos_employee SET count_dep = count_dep + 1 '
                                            'WHERE employee_id = ?', (employee_id,))
    if int(value_department) != int(form.department_id.data):
        new_db.create_update_delete_request('UPDATE count_dep_pos_employee SET count_pos = count_pos + 1 '
                                            'WHERE employee_id = ?', (employee_id,))


@app.route('/employee/update/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def update_employee(employee_id):
    """
    Update fields in Employee table
    :param employee_id: integer
    :return: template
    """
    # TODO: add check validate to form, if value return None - error - fix
    form = UpdateEmployeeForm()
    value = new_db.get_employee(employee_id)
    value_position = value['position_id']
    value_department = value['department_id']
    if form.validate_on_submit():
        new_db.create_update_delete_request('UPDATE employee SET department_id = ?, position_id = ? WHERE id = ?',
                                            (form.department_id.data, form.position_id.data, employee_id))
        if new_db.get_db().execute('SELECT employee_id FROM count_dep_pos_employee WHERE employee_id = ?',
                                   (employee_id, )).fetchone() is not None:
            count_add(value_position, value_department, employee_id, form)
        else:
            new_db.create_update_delete_request('INSERT INTO count_dep_pos_employee (employee_id)'
                                                'VALUES (?)', (employee_id, ))
            count_add(value_position, value_department, employee_id, form)
    return render_template('add view/update_employee.html', form=form)


@app.route('/positions')
@login_required
def list_positions():
    """
    View list of all positions
    :return: template
    """
    position = new_db.select_requests('SELECT * FROM position')
    return render_template('list view/list_position.html', position=position)


@app.route('/employees')
@login_required
def list_employees():
    """
    View list of all employees
    :return: template
    """
    result_join = new_db.select_requests('SELECT employee.fio, department.department_name, '
                                         'position.position_name, employee.date_start, '
                                         'count_dep_pos_employee.count_dep, count_dep_pos_employee.count_pos, '
                                         'date("now") - date_start as diff_year FROM employee '
                                         'INNER JOIN department ON employee.department_id = department.id '
                                         'INNER JOIN position on employee.position_id = position.id '
                                         'INNER JOIN count_dep_pos_employee ON '
                                         'count_dep_pos_employee.employee_id = employee.id')
    return render_template('list view/list_employees.html', year=date.today(), result_join=result_join)
