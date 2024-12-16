from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import db_settings
from database.models import Base, User, BlockedUser, Problem

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
    problem_to_delete = session.query(Problem).filter_by(message_id=mess_id).first()
    if problem_to_delete:
        session.delete(problem_to_delete)
        session.commit()

def spisok_problem():
    session = Session()
    problems = session.query(Problem).all()
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