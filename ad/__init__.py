#!/usr/bin/env python2.7
# 15/12/2017 version 1.0 by Jackie Chen
# - Add feature to search user in AD

from ldap3 import Server, Connection, ALL

class client(object):

	def __init__(self, **kwargs):
		if 'server' not in kwargs:
			raise ValueError("AD server must be given")
		if 'username' not in kwargs:
			raise ValueError("AD username must be given")
		if 'password' not in kwargs:
			raise ValueError("AD password must be given")
		self.server = Server(kwargs['server'], get_info=ALL)
		self.username = kwargs['username']
		self.password = kwargs['password']
		self.connection = Connection(self.server, self.username, self.password, auto_bind=True)	


	def search_user(self, base, username):
		query = '(&(objectclass=person)(sAMAccountName=' + username + '))'
		self.connection.search(base, query, attributes=['sAMAccountName', 'useraccountcontrol'])
		user = self.connection.entries
		if len(user) == 0:
			return False
		else:
			return user

