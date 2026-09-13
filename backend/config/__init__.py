"""Usa PyMySQL como driver MySQL compatível com Django (mysqlclient)."""
import pymysql

# Django 6 exige mysqlclient ≥ 2.2.1 na checagem; PyMySQL expõe 1.4.x como MySQLdb.
pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.install_as_MySQLdb()
