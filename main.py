# -*- coding: utf-8 -*-
# Log.py
# Copyright (C) 2018 Too-Naive
#
# This module is part of poj-reptile and is released under
# the AGPL v3 License: https://www.gnu.org/licenses/agpl-3.0.txt
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
from bs4 import BeautifulSoup
import requests
import time
import re, traceback
from libpy3.mysqldb import mysqldb
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

class insert_mysql(mysqldb):
	def insert(self, sql, args):
		try:
			self.execute(sql, args)
			self.commit()
		except Exception as e:
			print(repr(args))
			traceback.print_exc()
			raise e
	@staticmethod
	def get_list(dict_in):
		return (dict_in['id'], dict_in['title'], dict_in['time'], dict_in['memory'], dict_in['description'], dict_in['input'], 
			dict_in['output'], dict_in['sample_input'], dict_in['sample_output'], dict_in.get('hint', ''), dict_in['source'])

def get_time_memory_limit(string):
	r = re.match(r'Time Limit:(\d+)MS.+Memory Limit:(\d+)K', string)
	return {'time': int(r.group(1)), 'memory': int(r.group(2))}

def process_str(string):
	s = process_str_ex2(string.replace('\r\n', '\n').replace('\r', '\n'))#.replace('\n', '\\\\n').replace('\'', '\'\''))
	return s[:-1] if len(s) != 0 and s[-1] == '\n' else s

def process_str_ex2(string):
	try:
		return re.match(r'^\n?(.*)\r?\n?$', string).group(1)
	except:
		return string

def get_dict(problem_id, Session): 
	r = Session.get(config['target']['website'].format(problem_id)) 
	soup = BeautifulSoup(r.content.decode('gbk'), "lxml") 
	data = {}
	try:
		data['id'] = problem_id
		data['title'] = soup.select("html body table")[1].tr.select("p")[0].text
		data.update(get_time_memory_limit(soup.select("html body table")[1].tr.select("p")[1].text))
		data['description'] = soup.select("html body table")[1].tr.select("p")[3].text
		data['input'] = soup.select("html body table")[1].tr.select("p")[5].text
		data['output'] = soup.select("html body table")[1].tr.select("p")[7].text
		data['sample_input'] = soup.select("html body table")[1].tr.select("p")[9].text
		data['sample_output'] = soup.select("html body table")[1].tr.select("p")[11].text
		if 'Hint' in r.content.decode('gbk'):
			data['hint'] = soup.select("html body table")[1].tr.select("p")[13].text
		data['source'] = soup.select("html body table")[1].tr.select("p")[13 if 'Hint' not in r.content.decode('gbk') else 15].text
	except:
		print(r.content)
		traceback.print_exc()
	for key, value in data.items():
		if not isinstance(value, str): continue
		data.update({key: process_str(value)})
	return data

problem_range = range(1000, 3443)


def main():
	#sql = insert_mysql('localhost', config['mysql']['user'], config['mysql']['passwd'], config['mysql']['db'])
	with requests.Session() as Session:
		for x in problem_range:
			d = get_dict(x, Session)
			#sql.insert("INSERT INTO `problems` (`id`, `title`, `time`, `memory`, `description`, `input`, `output`, `samplein`, `sampleout`, `hint`, `source`) VALUES (%d, %s, %d, %d, %s, %s, %s, %s, %s, %s, %s)", sql.get_list(d))
			#sql.insert("INSERT INTO `problems_json` (`id`, `raw`) VALUES (%d, %s)", (d['id'], repr(d)))
			#print(repr(insert_mysql.get_list(d)))
			with open('{}.raw'.format(x), 'w') as fout:
				fout.write(repr(d))
			print(d)
			time.sleep(2)
			#r = Session.get(localwebsite.format(x))
			#soup = BeautifulSoup(r.content.decode('gbk'), 'lxml')
			#print(soup.select("html body table")[1].tr.select("p"))
			#entire_problem = bs.body.find('table').find_next('table')
			#for x in entire_problem.find_all('font'):
			#	if not any((re.match(r'(Source|(Sample )?Input|(Sample )?Output|Description|Hint)', x.text),)):
			#		print(repr(process_str(str(x.text))))
			#print(entire_problem)


if __name__ == '__main__':
	main()
