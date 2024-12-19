import mysql.connector
from mysql.connector import Error
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ExpenseMonitor.settings")
django.setup("DJANGO_SETTINGS_MODULE")

import ExpenseMonitor.settings as settings
from scheduler import my_daily_task


def delete_table_rows():
    try:
        # Replace with your database credentials
        db = settings.DATABASES.get("default")
        connection = mysql.connector.connect(
            host=db.get("HOST"),
            user=db.get("USER"),
            password=db.get("PASSWORD"),
            database=db.get("NAME"),
        )

        if connection.is_connected():
            # Replace 'your_table_name' with the actual name of the table
            table_name = "authtoken_token"

            # Create a cursor object
            cursor = connection.cursor()

            # Execute the delete query
            delete_query = f"DELETE FROM {table_name};"
            cursor.execute(delete_query)

            # Commit the changes
            connection.commit()

            # print(f'Rows deleted from {table_name} successfully.')

        # send mail of budget
        my_daily_task()

    except Error as e:
        print(f"Error: {e}")

    finally:
        # Close the cursor and connection
        if connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == "__main__":
    delete_table_rows()
