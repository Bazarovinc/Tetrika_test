import sqlite3


def parse(f_n, lines):
    if f_n == "users.txt":
        table_list = []
        try:
            cur.execute("CREATE TABLE users (id TEXT PRIMARY KEY NOT NULL, role TEXT NOT NULL);")
            conn.commit()
        except sqlite3.OperationalError:
            cur.execute("DROP TABLE users;")
            cur.execute("CREATE TABLE users (id TEXT PRIMARY KEY NOT NULL, role TEXT NOT NULL);")
            conn.commit()
        for i in range(2, len(lines) - 3):
            str = lines[i].split()
            if str[0] not in table_list:
                table_list.append(str[0])
                query = "INSERT INTO users VALUES (?, ?);"
                cur.execute(query, (str[0], str[2]))
        conn.commit()
        """cur.execute("SELECT * FROM users;")
        table = cur.fetchall()
        conn.commit()
        for pl in table:
            print(pl)"""
    elif f_n == 'lessons.txt':
        try:
            cur.execute("CREATE TABLE lessons (id TEXT PRIMARY KEY NOT NULL, event_id INT NOT NULL, "
                        "subject TEXT NOT NULL, date DATE, time TIME);")
            conn.commit()
        except sqlite3.OperationalError:
            cur.execute("DROP TABLE lessons;")
            cur.execute("CREATE TABLE lessons (id TEXT PRIMARY KEY NOT NULL, event_id INT NOT NULL, "
                        "subject TEXT NOT NULL, date DATE, time TIME);")
            conn.commit()
        for i in range(2, len(lines) - 2):
            str = lines[i].split()
            query = "INSERT INTO lessons VALUES (?, ?, ?, ?, ?);"
            cur.execute(query, (str[0], int(str[2]), str[4], str[6], str[7]))
        conn.commit()
    elif f_n == 'participants.txt':
        try:
            cur.execute("CREATE TABLE participants (event_id INT NOT NULL, user_id TEXT NOT NULL,"
                        "PRIMARY KEY (event_id, user_id),"
                        "FOREIGN KEY (event_id) REFERENCES lessons (event_id),"
                        "FOREIGN KEY (user_id) REFERENCES users(id));")
            conn.commit()
        except sqlite3.OperationalError:
            cur.execute("DROP TABLE participants;")
            cur.execute("CREATE TABLE participants (event_id INT NOT NULL, user_id TEXT NOT NULL,"
                        "PRIMARY KEY (event_id, user_id),"
                        "FOREIGN KEY (event_id) REFERENCES lessons(event_id),"
                        "FOREIGN KEY (user_id) REFERENCES users(id));")
            conn.commit()
        table = {}
        for i in range(2, len(lines) - 2):
            str = lines[i].split()
            query = "INSERT INTO participants VALUES (?, ?);"
            if str[0] not in table:
                table[str[0]] = []
                table[str[0]].append(str[2])
                cur.execute(query, (int(str[0]), str[2]))
            else:
                if str[2] not in table[str[0]]:
                    table[str[0]].append(str[2])
                    cur.execute(query, (str[0], str[2]))
        conn.commit()
    elif f_n == "quality.txt":
        try:
            cur.execute("CREATE TABLE quality (lesson_id TEXT NOT NULL, mark INT,"
                        "FOREIGN KEY (lesson_id) REFERENCES lessons(id));")
            conn.commit()
        except sqlite3.OperationalError:
            cur.execute("DROP TABLE quality;")
            cur.execute("CREATE TABLE quality (lesson_id TEXT NOT NULL, mark INT,"
                        "FOREIGN KEY (lesson_id) REFERENCES lessons(id));")
            conn.commit()
        for i in range(2, len(lines) - 2):
            str = lines[i].split()
            query = "INSERT INTO quality VALUES (?, ?);"
            if len(str) == 2:
                cur.execute(query, (str[0], 'NULL'))
            else:
                cur.execute(query, (str[0], int(str[2])))
        conn.commit()


def read_from_file(file_name):
    with open(file_name, 'r') as file_obj:
        lines = file_obj.readlines()
    parse(file_name, lines)


conn = sqlite3.connect('school.s3db')
cur = conn.cursor()
users_file = "users.txt"
lessons_file = "lessons.txt"
participants_file = "participants.txt"
quality_file = "quality.txt"
read_from_file(users_file)
read_from_file(lessons_file)
read_from_file(participants_file)
read_from_file(quality_file)
cur.execute("SELECT l.event_id, l.date, l.time, q.mark "
            "FROM quality q "
            "INNER JOIN lessons l ON l.id = q.lesson_id "
            "WHERE l.subject = 'phys'"
            "AND q.mark != 'NULL';")
table_with_marks = cur.fetchall()
try:
    cur.execute("CREATE VIEW les AS "
            "SELECT l.event_id, l.date, l.time, q.mark "
            "FROM quality q "
            "INNER JOIN lessons l ON l.id = q.lesson_id "
            "WHERE l.subject = 'phys'"
            "AND q.mark != 'NULL';")
except sqlite3.OperationalError:
    cur.execute("DROP VIEW les;")
    cur.execute("CREATE VIEW les AS "
                "SELECT l.event_id, l.date, l.time, q.mark "
                "FROM quality q "
                "INNER JOIN lessons l ON l.id = q.lesson_id "
                "WHERE l.subject = 'phys'"
                "AND q.mark != 'NULL';")
conn.commit()
try:
    cur.execute("CREATE TABLE daily_mark (tutor_id TEXT, date DATE, mark DOUBLE, ev_id INT);")
except sqlite3.OperationalError:
    cur.execute("DROP TABLE daily_mark;")
    cur.execute("CREATE TABLE daily_mark (tutor_id TEXT, date DATE, mark DOUBLE, ev_id INT);")
    conn.commit()
last_tutors = []
for mean in table_with_marks:
    req = "SELECT u.id, l.event_id, l.date FROM users u " \
          "INNER JOIN participants p on u.id = p.user_id " \
          "LEFT JOIN lessons l on p.event_id = l.event_id " \
          f"WHERE l.event_id = {mean[0]} " \
          "AND u.role = 'tutor';"
    cur.execute(req)
    tutors_id = cur.fetchall()
    insert = "INSERT INTO daily_mark VALUES (?, ?, (SELECT AVG(mark) FROM les l WHERE l.date = ? AND l.event_id = ?), ?);"
    for tutor in tutors_id:
        insert_1 = "SELECT * FROM les l WHERE l.date = ? AND l.event_id = ?"
        cur.execute(insert_1, (tutor[2], tutor[1]))
        if tutor not in last_tutors and len(cur.fetchall()) != 0:
            cur.execute(insert, (tutor[0], tutor[2], tutor[2], tutor[1], tutor[1]))
            last_tutors.append(tutor)
cur.execute("SELECT daily_mark.date, tutor_id, mark FROM daily_mark WHERE mark = (SELECT MIN(mark) FROM daily_mark );")
result = cur.fetchall()
result = result[0]
conn.commit()
print(f"Day: {result[0]}; Tutor_id: {result[1]}; Average score: {result[2]}")
