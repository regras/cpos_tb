import mysql.connector
cnx = mysql.connector.connect(user='root', password='mat271286', host='127.0.0.1')
cnx.execute("CREATE DATABASE blockchain DEFAULT CHARACTER SET 'utf8'")

cnx.close()