import mariadb

def connect_to_mariadb():
    return mariadb.connect(
        user="http",
        password="terpankerpanhorseradishblot",
        host="localhost",
 #       port=3306,
        database="burnsomninet"

    )

def sql_get_simple(table, column, match_column, match_value):
    connection = connect_to_mariadb()
    cursor = connection.cursor()

    output = None
    query = f"SELECT `{column}` FROM {table} WHERE `{match_column}` = ?;"
    cursor.execute(query, [match_value])
    rows = cursor.fetchall()

    if rows:
        output = rows[0][0]

    connection.close()

    return output

def sql_get_inverse_regex(table, column, match_column, match_value):
    connection = connect_to_mariadb()
    cursor = connection.cursor()

    output = None
    query = f"SELECT `{column}` FROM {table} WHERE ? REGEXP `{match_column}`;"

    cursor.execute(query, [match_value])
    rows = cursor.fetchall()

    if rows:
        output = rows[0][0]

    connection.close()

    return output
