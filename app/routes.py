"""
Flask app
version: 1.0
"""

from flask import render_template, redirect, flash, session, g, url_for
from werkzeug.security import check_password_hash, generate_password_hash


from app.forms import LoginForm, RegisterForm, AddPositionForm,\
    AddDepartmentForm, AddEmployeeForm, UpdateEmployeeForm, DepartmentViewForm
from app import app
from werkzeug.wrappers import Response
from datetime import date

import app.db as new_db
import functools
import typing


def login_required(view: typing.Any) -> typing.Any:
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
def register() -> Response:
    """
    Register user and generate password hash
    :return:
    """
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_db.create_update_request('INSERT INTO user (username, password) VALUES (?, ?)',
                                     (username, generate_password_hash(password)))
        return redirect('/login')
    return render_template('auth/register.html', form=form, username=form.username.data, password=form.password.data)


@app.route('/login', methods=['GET', 'POST'])
def login() -> Response:
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
        if user is None:
            flash('User does not match')
        else:
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
def index() -> Response:
    """
    View main page
    :return:
    """
    return render_template('index.html')


@app.route('/position/add', methods=['GET', 'POST'])
@login_required
def add_position() -> Response:
    """
    Add position to Position table on db
    :return: template
    """
    form = AddPositionForm()
    if form.validate_on_submit():
        new_db.create_update_request('INSERT INTO position (position_name, description)'
                                     'VALUES (?, ?)',
                                     (form.position_name.data, form.description.data))
        flash('You successful add position')
    return render_template('add view/add_delete_new_position.html', form=form)


@app.route('/position/delete/<int:position_id>', methods=['GET', 'POST'])
@login_required
def delete_position(position_id: int) -> Response:
    """
    Delete position from Position table by position_id
    :param position_id: integer
    :return:
    """
    new_db.create_update_request('DELETE FROM position WHERE id = ?',
                                 (position_id, ))
    return redirect(url_for('list_positions'))


@app.route('/department/add', methods=['GET', 'POST'])
@login_required
def add_department() -> Response:
    """
    Add department to Department table on db
    :return: template
    """
    dep = new_db.select_requests('SELECT * FROM department')
    form = AddDepartmentForm()
    if form.validate_on_submit():
        new_db.create_update_request('INSERT INTO department (department_name, parent_id)'
                                     'VALUES (?, ?)',
                                     (form.department_name.data, form.parent_id.data))
        flash('You successful add department')
    return render_template('add view/add_delete_new_department.html', form=form, department=dep)


@app.route('/department/delete/<int:department_id>', methods=['GET', 'POST'])
@login_required
def delete_department(department_id: int) -> Response:
    """
    Delete position from Position table by position_id
    :param department_id: integer
    :return:
    """
    new_db.create_update_request('DELETE FROM department WHERE id = ?', (department_id, ))
    return redirect(url_for('index'))


@app.route('/employee/add',  methods=['GET', 'POST'])
@login_required
def add_employee() -> Response:
    """
    Add new employee to Employee table on db
    :return: template
    """
    form = AddEmployeeForm()
    if form.validate_on_submit():
        if new_db.get_db().execute(
                'SELECT fio FROM employee WHERE fio = ?', (form.fio.data, )
        ).fetchone() is not None:
            flash('Please enter a different fio')
        else:
            new_db.create_update_request('INSERT INTO employee (fio, position_id, department_id, date_start)'
                                         'VALUES (?, ?, ?, ?)',
                                         (form.fio.data, form.position_id.data, form.department_id.data, date.today()))
            flash('You successful add employee')

    return render_template('add view/add_delete_new_employees.html', form=form)


@app.route('/employee/delete/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def delete_employee(employee_id: int) -> Response:
    """
    Delete position from Position table by position_id
    :param employee_id: integer
    :return:
    """
    new_db.create_update_request('DELETE FROM employee WHERE id = ?', (employee_id, ))
    return redirect(url_for('list_employees'))


def count_add(value_position: int, value_department: int, employee_id: int, form: typing.Dict):
    if int(value_position) != int(form.position_id.data):
        new_db.create_update_request('UPDATE count_dep_pos_employee SET count_dep = count_dep + 1 '
                                     'WHERE employee_id = ?', (employee_id,))
    if int(value_department) != int(form.department_id.data):
        new_db.create_update_request('UPDATE count_dep_pos_employee SET count_pos = count_pos + 1 '
                                     'WHERE employee_id = ?', (employee_id,))


@app.route('/employee/update/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def update_employee(employee_id: int) -> Response:
    """
    Update fields in Employee table
    :param employee_id: integer
    :return: template
    """
    # TODO: If value return None - error - fix
    form = UpdateEmployeeForm()
    value = new_db.get_employee(employee_id)
    value_position = value['position_id']
    value_department = value['department_id']
    if form.validate_on_submit():
        new_db.create_update_request('UPDATE employee SET department_id = ?, position_id = ? WHERE id = ?',
                                     (form.department_id.data, form.position_id.data, employee_id))
        if new_db.get_db().execute('SELECT employee_id FROM count_dep_pos_employee WHERE employee_id = ?',
                                   (employee_id, )).fetchone() is not None:
            count_add(value_position, value_department, employee_id, form)
        else:
            new_db.create_update_request('INSERT INTO count_dep_pos_employee (employee_id)'
                                         'VALUES (?)', (employee_id, ))
            count_add(value_position, value_department, employee_id, form)
    return render_template('add view/update_employee.html', form=form)


@app.route('/positions')
@login_required
def list_positions() -> Response:
    """
    View list of all positions
    :return: template
    """
    position = new_db.select_requests('SELECT * FROM position')
    return render_template('list view/list_position.html', position=position)


@app.route('/employees')
@login_required
def list_employees() -> Response:
    """
    View list of all employees
    :return: template
    """
    result_join = new_db.select_requests('SELECT employee.id, employee.fio, department.department_name, '
                                         'position.position_name, employee.date_start, '
                                         'CASE WHEN count_dep IS NULL THEN 1 WHEN count_dep IS NOT NULL '
                                         'THEN count_dep end as count_dep, '
                                         'CASE WHEN count_pos IS NULL THEN 1 WHEN count_pos IS NOT NULL '
                                         'THEN count_pos end as count_pos, '
                                         'date("now") - date_start as diff_year FROM employee '
                                         'INNER JOIN department ON employee.department_id = department.id '
                                         'INNER JOIN position on employee.position_id = position.id '
                                         'LEFT JOIN count_dep_pos_employee ON '
                                         'employee.id = count_dep_pos_employee.employee_id')
    return render_template('list view/list_employees.html', year=date.today(), result_join=result_join)


@app.route('/department/stats')
def statistic_department() -> Response:
    """
    Statistic about department and count working people in it
    :return:
    """
    form = DepartmentViewForm()
    select = new_db.select_requests('WITH RECURSIVE CTE_TEST(id, department_name, parent_id, LevelParent)'
                                    ' AS (select id, department_name, parent_id, 0 as LevelParent'
                                    ' from department where parent_id IS NULL'
                                    ' union all'
                                    ' select t1.id, t1.department_name, t1.parent_id, LevelParent + 1'
                                    ' from department t1'
                                    ' join CTE_TEST t2 on t1.parent_id=t2.id)'
                                    ' select * from CTE_TEST order by LevelParent')

    return render_template('list view/list_department.html', department=select, form=form)
