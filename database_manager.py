import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """
    Create a database connection to the SQLite database specified by db_file
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(f"Error {e} occurred while connecting to database")
    return conn

def create_ticket(conn, contract_address, liquidity_amount, lock_period, eth_address, status):
    """
    Create a new ticket in the database
    """
    sql = ''' INSERT INTO tickets(contract_address, liquidity_amount, lock_period, eth_address, status)
              VALUES(?,?,?,?,?) '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (contract_address, liquidity_amount, lock_period, eth_address, status))
        return cur.lastrowid
    except Error as e:
        print(f"Error {e} occurred while inserting ticket")
        return None

def update_ticket_status(conn, ticket_id, new_status):
    """
    Update the status of a ticket
    """
    sql = ''' UPDATE tickets SET status = ? WHERE id = ? '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (new_status, ticket_id))
        conn.commit()
    except Error as e:
        print(f"Error {e} occurred while updating ticket status")

# Additional functions can be added as needed

# Example usage (can be removed or modified for actual implementation)
if __name__ == "__main__":
    database = "path_to_your_database.db"
    conn = create_connection(database)

    if conn is not None:
        # Example of creating a new ticket
        new_ticket_id = create_ticket(conn, "0xContractAddress", 1000, 6, "0xEthAddress", "Pending")
        print("New ticket created with ID:", new_ticket_id)
        
        # Example of updating a ticket's status
        update_ticket_status(conn, new_ticket_id, "Completed")
        print(f"Ticket ID {new_ticket_id} updated to 'Completed'")
