# -*- coding: utf-8 -*-

import re
import MySQLdb
from flask import Flask, request, session, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.secret_key = '\x81\\j\xa2\xd4\x1d\x01^\xc0y\x0el\xec|1S\xe6\x1b\x0f\xe53\x85?\xd7'
app.debug = True

def get_db():
    "连接数据库"
    conn = MySQLdb.connect(user="root",passwd="mysqladmin",host="localhost",db='message_board')
    return conn
	
@app.route('/')
def show_message():
        "显示最新的数据"
	db = get_db()
	cursor = db.cursor()
	cursor.execute('select name,email,message from users left join emails on users.user_id = emails.user_id order by users.user_id desc limit 10 ')
	allInfo= [dict(name = row[0],email = row[1] ,text = row[2]) for row in cursor.fetchall()]
	cursor.close()
	db.close()
	return render_template('show_message.html', allInfo = allInfo) #调用show_message.html来渲染
	
@app.route('/check',methods = ['POST'''])
def  check_input():
        "检查输入数据是否有效"
	isRight = True
	warning = "waring: "

	#正则表达式来检查邮箱格式是否正确
	if len(request.form['email'])!=0 and re.match('\w+@\w+\.(com|net|org)',request.form['email']) is None :
		warning += "the email form is flase"
		isRight = False
	elif len(request.form['text']) < 50 or len(request.form['text']) > 500 :
		warning += "the message must long than 50 and short than 500!"
		isRight = False
	if isRight:
		add_to_db()
		flash('New message was successfully posted')
	else:
		flash(warning)
	return redirect(url_for('show_message'))

def add_to_db():
        "添加数据到数据库"
	db = get_db()
	db.begin()
	cursor = db.cursor()
	cursor.execute('''insert into users (name,message) values ("%s","%s")'''%(request.form['name'], request.form['text']))
	if  len(request.form['email']) != 0: 
		cursor.execute('SELECT LAST_INSERT_ID()')   #取该数据在users表中的user_id
		for row in cursor.fetchall():
			cursor.execute("insert into emails values(%d,'%s')"%(row[0],request.form['email']))   #将该数据在users表中的user_id插入emails表中 
	cursor.close()
	db.commit()
	db.close()
	session['add_message'] = False
	
@app.route('/go_back')
def go_back():
        "隐藏表单"
	session.pop('add_message',None)
	return redirect(url_for('show_message'))

@app.route('/add_message',methods=['GET', 'POST'])
def add_message():
        "显示表单,然用户输入数据"
	session['add_message'] = True
	flash('write down your new message')
	return redirect(url_for('show_message'))


if __name__ == '__main__':
    app.run()
