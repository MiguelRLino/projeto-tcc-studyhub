"""Usa PyMySQL como driver MySQL compatível com Django (mysqlclient)."""
import pymysql

pymysql.install_as_MySQLdb()
