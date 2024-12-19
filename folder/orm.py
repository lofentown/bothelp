from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import db_settings
from database.models import Base, User, BlockedUser, Problem, Otziv
from datetime import datetime

engine = create_engine(db_settings.URL, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def add_user(tg_id, username):
    session = Session()
    user = session.query(User).filter(User.tg_id == str(tg_id)).first()
    if user is None:
        new_user = User(tg_id=tg_id, username=username)
        session.add(new_user)
        session.commit()
        return 1
    else:
        return -1

def add_problem(tg_id, username, text, mess_id):
    session = Session()
    new_problem = Problem(tg_id=tg_id, username=username, problem_text=text, message_id=mess_id)
    session.add(new_problem)
    session.commit()

def add_otziv(tg_id, username, text, mess_id):
    session = Session()
    new_otziv = Otziv(tg_id=tg_id, username=username, otziv_text=text, message_id=mess_id)
    session.add(new_otziv)
    session.commit()

#def add_problem(tg_id, text):
#    session = Session()
#    user = session.query(User).filter(User.tg_id == str(tg_id)).first()
#    if user:
#        user.problem_text = text
#        session.commit()
#       return 1
#    else:
#       return -1
def delete_problem(mess_id):
    session = Session()
    complete = session.query(Problem).filter_by(message_id=mess_id).first()
    if complete:
        complete.complete_date = datetime.now()
        complete.complete = True
        session.commit()

def delete_otziv(mess_id):
    session = Session()
    complete = session.query(Otziv).filter_by(message_id=mess_id).first()
    if complete:
        complete.complete_date = datetime.now()
        complete.complete = True
        session.commit()
def get_problem(mess_id):
    session = Session()
    complete = session.query(Problem).filter_by(message_id=mess_id).first()
    if complete:
        text = complete.problem_text
        user_id = complete.tg_id
        username = complete.username
        return text, user_id, username

def get_otziv(mess_id):
    session = Session()
    complete = session.query(Otziv).filter_by(message_id=mess_id).first()
    if complete:
        text = complete.otziv_text
        user_id = complete.tg_id
        username = complete.username
        return text, user_id, username
def add_reshenie(mess_id, text):
    session = Session()
    try:
        # Ищем запись с указанным message_id
        otziv = session.query(Otziv).filter_by(message_id=mess_id).first()
        if otziv:
            # Обновляем текст решения
            otziv.complete_text = text
            session.commit()
            return True
        else:
            print(f"Задача с message_id {mess_id} не найдена.")
            return False
    except Exception as e:
        print(f"Ошибка при обновлении complete_text: {e}")
        session.rollback()  # Откат транзакции при ошибке
        return False
    finally:
        session.commit()

def add_otvet(mess_id, text):
    session = Session()
    try:
        # Ищем запись с указанным message_id
        problem = session.query(Problem).filter_by(message_id=mess_id).first()
        if problem:
            # Обновляем текст решения
            problem.complete_text = text
            session.commit()
            return True
        else:
            print(f"Задача с message_id {mess_id} не найдена.")
            return False
    except Exception as e:
        print(f"Ошибка при обновлении complete_text: {e}")
        session.rollback()  # Откат транзакции при ошибке
        return False
    finally:
        session.commit()
def spisok_problem():
    session = Session()
    problems = session.query(Problem).filter_by(complete=False).all()
    return problems
def get_admins():
    session = Session()
    users = session.query(User).filter_by(admin=True).all()
    return users

def check_admin(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == str(tg_id)).first()
    if user.admin == True:
        return 1
    else:
        return -1

def add_blocked(count):
    session = Session()
    number = session.query(BlockedUser).first()
    number.block_count = count
    session.commit()

def get_all_users():
    session = Session()
    users = session.query(User).all()
    return users

def stat():
    session = Session()
    users = session.query(User).count()
    blocked = session.query(BlockedUser).count()
    return [users, blocked]