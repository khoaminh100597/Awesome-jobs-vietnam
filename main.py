'''
Làm một website tuyển dụng.

Lấy dữ liệu các job từ: https://github.com/awesome-jobs/vietnam/issues

Lưu dữ liệu vào một bảng ``jobs`` trong SQLite. Xem ví dụ: https://docs.python.org/3/library/sqlite3.html

Dùng Flask tạo website hiển thị danh sách các jobs khi vào đường dẫn ``/``.
Khi bấm vào mỗi job (1 link), sẽ mở ra trang chi tiết về jobs (giống như trên
các trang web tìm viêc).
'''


import sqlite3
import requests
import os
from bs4 import BeautifulSoup
from flask import Flask
from flask import render_template
from flask import url_for
app = Flask(__name__)


# post_id = 1
@app.route('/<int:post_id>')
def res(post_id):
	link = info_job[post_id - 1][2]
	resp = requests.get(link)
	tree = BeautifulSoup(resp.text)
	node = tree.find('task-lists')
	html_str = """ {} """.format(node)
	with open('./templates/base.html', 'w') as f:
		f.truncate(0)
		f.write(html_str)
	return render_template('base.html')


@app.route('/')
def reqs():
	return render_template('index.html', nodes=info_job)


if __name__ == '__main__':
	resp = requests.get('https://github.com/awesome-jobs/vietnam/issues?page=1')
	tree = BeautifulSoup(resp.text)
	nodes = tree.findAll('a', attrs={'data-hovercard-type':"issue"})
	result = nodes
	i = 1
	while nodes != []:
		i += 1
		link ='https://github.com/awesome-jobs/vietnam/issues?page={}'.format(i)
		resp = requests.get(link)
		tree = BeautifulSoup(resp.text)
		nodes = tree.findAll('a', attrs={'data-hovercard-type':"issue"})
		result += nodes
	info_job = []
	for node in result:
		info_job.append([node.text, 'https://github.com/' + node.get_attribute_list('href')[0]])
	conn = sqlite3.connect('./jobs.db')
	c = conn.cursor()
	if os.path.isfile('./jobs.db'):
		if c.rowcount == -1:
			os.remove('./jobs.db')
		else:
			old_info = []
			for row in c.execute('SELECT * FROM jobs'):
				old_info.append(row)
			if info_job == old_info:
				pass
			else:
				os.remove('./jobs.db')
	index = 0
	for info in info_job:
		index += 1
		info.insert(0, index)
	info_job = tuple(info_job)
	if not os.path.isfile('./jobs.db'):
		conn = sqlite3.connect('./jobs.db')
		c = conn.cursor()
		c.execute("CREATE TABLE jobs (id int PRIMARY KEY, job, link)")
		c.executemany('INSERT INTO jobs VALUES (?, ?, ?)', info_job)
		conn.commit()
		conn.close()
	with app.test_request_context():
		for i in range(1, len(info_job) + 1):
			url_for('res', post_id=i)
	app.run(debug=True)

	