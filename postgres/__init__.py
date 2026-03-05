import psycopg2

from postgres.config import host, password, database, user, port


connection = psycopg2.connect(host=host,
                              database=database,
                              user=user,
                              password=password,
                              port=port)

cursor = connection.cursor()
