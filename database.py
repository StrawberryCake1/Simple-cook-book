
import sqlite3
#variable storing database path
DATABASE = 'data/my_database.db'
class dbFunctions:
    @staticmethod
    #Method that gets password by username
    def passwordChecker(tableName, columnName, userName):
        try:
            #Connecting to my database
            connection = sqlite3.connect(DATABASE)
            cursor = connection.cursor()
            
            #selecting password
            query = f"SELECT password FROM {tableName} WHERE {columnName} = ?"
            cursor.execute(query, (userName,))
            
            #geting password and storing it in variable result
            result = cursor.fetchone()
            #Disconnecting form database
            connection.close()

            #If result is empty return None(null)
            print(result)
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Database error!: {e}")
            return None  
    @staticmethod  
    #Method that checks if password is correct for the userName  
    def loginChercker(userName, password):    
        storedPassword = dbFunctions.passwordChecker("users", "username", userName)
        if(storedPassword == password):
            return True
        else:
            return False
    @staticmethod   
    #Returns all column values 
    def get_column_values(table_name, column_name):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT {column_name} FROM {table_name};")
            results = cursor.fetchall()
            conn.close()
            # returns all column values
            return [row[0] for row in results]
        except sqlite3.Error as e:
            print(f"Error while getting values from table!: {e}")
            return []      
    @staticmethod
    #Returns number of recipes for every unique location
    def count_by_location(table_name):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT location, COUNT(*) FROM {table_name} GROUP BY location;")
            results = cursor.fetchall()
            conn.close()
            #Returns dictionary {location: number}
            return {row[0]: row[1] for row in results}
        except sqlite3.Error as e:
            print(f"Error loading table: {e}")
            return {}
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

#User database
class UserDatabase:
    @staticmethod
    #Method that creates user table
    def create_table():
        #Connecting to db using mwthod
        conn = get_db_connection()
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                );
            """)
        conn.close()
    #Deletes table by name
    @staticmethod
    def delete_table():
        try:
            conn = get_db_connection()
            with conn:
                conn.execute(f"DROP TABLE IF EXISTS users;")
            conn.close()
        except sqlite3.Error as e:
            print(f"Chyba pri mazaní tabuľky: {e}")
    @staticmethod
    #Inserting user
    def insert_user(username, password):
        conn = get_db_connection()
        with conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.close()

#Recipe database
class RecipeDatabase:
    @staticmethod
    def create_table(table_name):
        #Creates table with unique name
        conn = get_db_connection()
        with conn:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    ingredients TEXT NOT NULL,
                    instructions TEXT NOT NULL,
                    location TEXT NOT NULL
                );
            """)
        conn.close()

    @staticmethod
    def delete_table(table_name):
        #Deletes table by nameľ
        try:
            conn = get_db_connection()
            with conn:
                conn.execute(f"DROP TABLE IF EXISTS {table_name};")
            conn.close()
        except sqlite3.Error as e:
            print(f"Chyba pri mazaní tabuľky: {e}")

    @staticmethod
    def insert_recipe(table_name, title, ingredients, instructions, location):
        #Inserts recipe
        conn = get_db_connection()
        with conn:
            conn.execute(
                f"INSERT INTO {table_name} (title, ingredients, instructions, location) VALUES (?, ?, ?, ?)",
                (title, ingredients, instructions, location)
            )
        conn.close()
   

