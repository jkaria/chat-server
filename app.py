import flask
import pymysql
import pymysql.cursors

app = flask.Flask(__name__)

db = pymysql.connect(user='root',
                     password='root',
                     host='localhost',
                     database='chatserver')

@app.route('/messages', methods=['GET', 'POST'])
def add_messages():
    if flask.request.method == 'POST':
        req_data = flask.request.get_json()
        with db.cursor() as cur:
            query = f"INSERT INTO messages(from_user, to_user, content) VALUES('{req_data['from']}', '{req_data['to']}', '{req_data['content']}');"
            # print(query)
            cur.execute(query)
            db.commit()
        return 'Success'
    else:
        #TODO: support pagination, for now fetch and return last 10 messages
        to_user = flask.request.args['to']
        with db.cursor() as cur:
            query = f"SELECT dt, content, from_user FROM messages WHERE to_user='{to_user}' ORDER BY dt DESC LIMIT 10;"
            # print(query)
            cur.execute(query)
            msgs = cur.fetchall()
        return flask.jsonify({'messages': msgs})

