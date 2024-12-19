from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import db_settings
from database.models import Base, User, BlockedUser, Problem, Otziv
from datetime import datetime
from openpyxl import Workbook

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

def spisok_otziv():
    session = Session()
    otzivs = session.query(Otziv).filter_by(complete=False).all()
    return otzivs

def vse_problems():
    session = Session()
    problems = session.query(Problem).all()
    # Запись в текстовый файл
    txt_file_path = "problems.txt"
    with open(txt_file_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(
            "ID | Username | Date | TG ID | Message ID | Problem Text | Complete | Complete Date | Complete Text\n")
        txt_file.write("-" * 100 + "\n")
        for problem in problems:
            txt_file.write(
                f"{problem.id} | {problem.username or 'N/A'} | {problem.date} | {problem.tg_id} | {problem.message_id} | "
                f"{problem.problem_text or 'N/A'} | {problem.complete} | {problem.complete_date or 'N/A'} | {problem.complete_text or 'N/A'}\n"
            )

    # Запись в Excel файл
    excel_file_path = "problems.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Проблемы"

    # Добавляем заголовки
    ws.append(
        ["ID", "Username", "Date", "TG ID", "ID сообщения", "Текст проблемы", "Завершено", "Дата завершения", "Ответ поддержки"])

    # Записываем данные
    for problem in problems:
        ws.append([
            problem.id,
            problem.username or "",
            problem.date.strftime("%Y-%m-%d %H:%M:%S"),
            problem.tg_id,
            problem.message_id,
            problem.problem_text or "Нет текста",
            problem.complete,
            problem.complete_date.strftime("%Y-%m-%d %H:%M:%S") if problem.complete_date else "-",
            problem.complete_text or "Нет текста"
        ])

    wb.save(excel_file_path)
    return txt_file_path, excel_file_path

def vse_otziv():
    session = Session()
    problems = session.query(Otziv).all()
    # Запись в текстовый файл
    txt_file_path = "otziv.txt"
    with open(txt_file_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(
            "ID | Username | Date | TG ID | Message ID | Otziv Text | Complete | Complete Date | Complete Text\n")
        txt_file.write("-" * 100 + "\n")
        for problem in problems:
            txt_file.write(
                f"{problem.id} | {problem.username or 'N/A'} | {problem.date} | {problem.tg_id} | {problem.message_id} | "
                f"{problem.otziv_text or 'N/A'} | {problem.complete} | {problem.complete_date or 'N/A'} | {problem.complete_text or 'N/A'}\n"
            )

    # Запись в Excel файл
    excel_file_path = "otziv.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Отзывы"

    # Добавляем заголовки
    ws.append(
        ["ID", "Username", "Дата", "TG ID", "ID сообщения", "Текст отзыва", "Завершено", "Дата завершения", "Ответ поддержки"])

    # Записываем данные
    for problem in problems:
        ws.append([
            problem.id,
            problem.username or "",
            problem.date.strftime("%Y-%m-%d %H:%M:%S"),
            problem.tg_id,
            problem.message_id,
            problem.otziv_text or "Нет текста",
            problem.complete,
            problem.complete_date.strftime("%Y-%m-%d %H:%M:%S") if problem.complete_date else "-",
            problem.complete_text or "Нет текста"
        ])

    wb.save(excel_file_path)
    return txt_file_path, excel_file_path
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