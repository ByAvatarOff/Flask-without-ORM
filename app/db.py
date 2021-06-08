import sqlite3
from flask import g, current_app
from app import app
import typing


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext  # close connection after any wev request
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def select_requests(command: str) -> typing.List[sqlite3.Row]:
    data = get_db()
    select = data.execute(command).fetchall()
    return select


def create_update_delete_request(command: str, parameters: typing.Union[str, int]) -> bool:
    data = get_db()
    if data.execute(command, parameters) is not None:
        data.commit()
        return True
    return False


def get_employee(employee_id: int) -> sqlite3.Row:
    data = get_db()
    select = data.execute('''SELECT department_id, position_id FROM employee WHERE employee.id = ?''',
                     (employee_id, )).fetchone()
    return select


def list_position() -> typing.List[typing.Tuple[int, int]]:
    with app.app_context():
        pos_choices = []
        select = select_requests('SELECT * FROM position')
        if select:
            for row in select:
                pos_choices.append((row['id'], row['position_name']))
        return pos_choices


def list_department() -> typing.List[typing.Tuple[int, int]]:
    with app.app_context():
        dep_choices = []
        select = select_requests('SELECT * FROM department')
        if select:
            for row in select:
                dep_choices.append((row['id'], row['department_name']))
        return dep_choices
