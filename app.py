import streamlit as st
import mysql.connector
import pandas as pd
from streamlit_lottie import st_lottie
import requests

def loti(url):
    r = requests.get(url)
    if r.status_code != 200:
       return None
    else:
        return r.json()

def create_connection():
    db = mysql.connector.connect(user= 'root',
    password= 'Mysql@28',
    host= 'localhost',
    port= 3306,
    database='transportdb',
    auth_plugin='mysql_native_password')
    return db

def load_animations():
    bus_animation = loti("https://lottie.host/68473936-1ac3-4778-985d-3bd906349f2d/55yARaR4bt.json")
    return bus_animation

def create_buses_table(db):
    cursor = db.cursor()
    create_buses_query = """
    CREATE TABLE IF NOT EXISTS buses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        bus_number VARCHAR(20) UNIQUE,
        capacity INT,
        driver_name VARCHAR(255),
        route VARCHAR(255),
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_buses_query)
    db.commit()
    cursor.close()

def create_bookings_table(db):
    cursor = db.cursor()
    create_bookings_query = """
    CREATE TABLE IF NOT EXISTS bookings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        bus_id INT,
        passenger_name VARCHAR(255),
        booking_date DATE,
        booking_time TIME,
        contact_number VARCHAR(20),
        status VARCHAR(50),
        FOREIGN KEY (bus_id) REFERENCES buses(id)
    )
    """
    cursor.execute(create_bookings_query)
    db.commit()
    cursor.close()

def insert_bus(db, bus_number, capacity, driver_name, route):
    cursor = db.cursor()
    cursor.execute("USE transportdb")

    check_duplicate_query = "SELECT * FROM buses WHERE bus_number = %s"
    cursor.execute(check_duplicate_query, (bus_number,))
    if cursor.fetchone():
        st.warning("A bus with this number already exists.")
    else:
        insert_bus_query = """
        INSERT INTO buses (bus_number, capacity, driver_name, route)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_bus_query, (bus_number, capacity, driver_name, route))
        db.commit()
        st.success("Bus record inserted successfully.")
    cursor.close()

def fetch_all_buses(db):
    cursor = db.cursor()
    cursor.execute("USE transportdb")
    cursor.execute("SELECT * FROM buses")
    buses = cursor.fetchall()
    cursor.close()
    return buses

def fetch_bus_by_criteria(db, criterion, value):
    cursor = db.cursor()
    cursor.execute("USE transportdb")

    if criterion == "ID":
        cursor.execute("SELECT * FROM buses WHERE id = %s", (value,))
    elif criterion == "Bus Number":
        cursor.execute("SELECT * FROM buses WHERE bus_number = %s", (value,))
    elif criterion == "Driver Name":
        cursor.execute("SELECT * FROM buses WHERE driver_name = %s", (value,))
    
    bus = cursor.fetchone()
    cursor.close()
    return bus

def delete_bus(db, delete_option, delete_value):
    cursor = db.cursor()
    cursor.execute("USE transportdb")

    if delete_option == "ID":
        cursor.execute("DELETE FROM buses WHERE id = %s", (delete_value,))
    elif delete_option == "Bus Number":
        cursor.execute("DELETE FROM buses WHERE bus_number = %s", (delete_value,))
    
    db.commit()
    st.success("Bus record deleted successfully.")
    cursor.close()

def insert_booking(db, bus_id, passenger_name, booking_date, booking_time, contact_number, status):
    cursor = db.cursor()
    cursor.execute("USE transportdb")

    insert_booking_query = """
    INSERT INTO bookings (bus_id, passenger_name, booking_date, booking_time, contact_number, status)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_booking_query, (bus_id, passenger_name, booking_date.strftime("%Y-%m-%d"),
                                          booking_time.strftime("%H:%M:%S"), contact_number, status))
    db.commit()
    st.success("Booking record added successfully.")
    cursor.close()

def fetch_all_bookings(db):
    cursor = db.cursor()
    cursor.execute("USE transportdb")
    cursor.execute("SELECT * FROM bookings")
    bookings = cursor.fetchall()
    cursor.close()
    return bookings

def search_booking_by_criteria(db, criterion, value):
    cursor = db.cursor()
    cursor.execute("USE transportdb")

    if criterion == "ID":
        cursor.execute("SELECT * FROM bookings WHERE id = %s", (value,))
    elif criterion == "Passenger Name":
        cursor.execute("SELECT * FROM bookings WHERE passenger_name = %s", (value,))
    elif criterion == "Contact Number":
        cursor.execute("SELECT * FROM bookings WHERE contact_number = %s", (value,))
    
    booking = cursor.fetchone()
    cursor.close()
    return booking

def edit_booking(db, booking_id, new_date, new_time, new_status):
    cursor = db.cursor()
    cursor.execute("USE transportdb")

    update_booking_query = """
    UPDATE bookings
    SET booking_date = %s, booking_time = %s, status = %s
    WHERE id = %s
    """
    cursor.execute(update_booking_query, (new_date, new_time, new_status, booking_id))
    db.commit()
    st.success("Booking record updated successfully.")
    cursor.close()

def main():
    st.title("Bus Booking Management System")

    db = create_connection()
    create_buses_table(db)
    create_bookings_table(db)

    bus_animation = load_animations()

    menu = ["Home", "Add Bus", "View All Buses", "Search and Edit Bus", "Delete Bus", 
            "Add Booking", "View All Bookings", "Search and Edit Booking"]
    choice = st.sidebar.selectbox("Select an Option", menu)

    if choice == "Home":
        st_lottie(bus_animation, height=300)

    elif choice == "Add Bus":
        st.subheader("Enter Bus Details")
        bus_number = st.text_input("Bus Number")
        capacity = st.number_input("Capacity", min_value=1)
        driver_name = st.text_input("Driver Name")
        route = st.text_input("Route")
        
        if st.button("Add Bus"):
            insert_bus(db, bus_number, capacity, driver_name, route)

    elif choice == "View All Buses":
        buses = fetch_all_buses(db)
        if buses:
            df = pd.DataFrame(buses, columns=['ID', 'Bus Number', 'Capacity', 'Driver Name', 'Route', 'Date Added'])
            st.dataframe(df)
        else:
            st.write("No buses found.")

    elif choice == "Search and Edit Bus":
        search_criteria = st.selectbox("Search by", ["ID", "Bus Number", "Driver Name"])
        search_value = st.text_input("Enter value")

        if st.button("Search"):
            bus = fetch_bus_by_criteria(db, search_criteria, search_value)
            if bus:
                st.write("Bus Details")
                df = pd.DataFrame([bus], columns=['ID', 'Bus Number', 'Capacity', 'Driver Name', 'Route', 'Date Added'])
                st.dataframe(df)
                st.session_state.edit_bus = bus
            else:
                st.write("Bus not found.")

        if 'edit_bus' in st.session_state:
            bus = st.session_state.edit_bus
            st.write("Edit Bus Details")
            new_driver_name = st.text_input("Driver Name", value=bus[3])
            new_route = st.text_input("Route", value=bus[4])

            if st.button("Update Bus"):
                edit_bus(db, bus[0], new_driver_name, new_route)

    elif choice == "Delete Bus":
        delete_option = st.selectbox("Delete by", ["ID", "Bus Number"])
        delete_value = st.text_input("Enter value")

        if st.button("Delete"):
            delete_bus(db, delete_option, delete_value)

    elif choice == "Add Booking":
        st.subheader("Enter Booking Details")
        bus_id = st.number_input("Bus ID", min_value=1)
        passenger_name = st.text_input("Passenger Name")
        booking_date = st.date_input("Booking Date")
        booking_time = st.time_input("Booking Time")
        contact_number = st.text_input("Contact Number")
        status = st.selectbox("Status", ["Confirmed", "Pending", "Cancelled"])

        if st.button("Add Booking"):
            insert_booking(db, bus_id, passenger_name, booking_date, booking_time, contact_number, status)

    elif choice == "View All Bookings":
        bookings = fetch_all_bookings(db)
        if bookings:
            df = pd.DataFrame(bookings, columns=['ID', 'Bus ID', 'Passenger Name', 'Booking Date', 
                                                 'Booking Time', 'Contact Number', 'Status'])
            st.dataframe(df)
        else:
            st.write("No bookings found.")

    elif choice == "Search and Edit Booking":
        search_criteria = st.selectbox("Search by", ["ID", "Passenger Name", "Contact Number"])
        search_value = st.text_input("Enter value")

        if st.button("Search"):
            booking = search_booking_by_criteria(db, search_criteria, search_value)
            if booking:
                st.write("Booking Details")
                df = pd.DataFrame([booking], columns=['ID', 'Bus ID', 'Passenger Name', 'Booking Date', 
                                                      'Booking Time', 'Contact Number', 'Status'])
                st.dataframe(df)
                st.session_state.edit_booking = booking
            else:
                st.write("Booking not found.")

        if 'edit_booking' in st.session_state:
            booking = st.session_state.edit_booking
            st.write("Edit Booking Details")
            new_date = st.date_input("Booking Date", value=booking[3])
            new_time = st.time_input("Booking Time", value=booking[4])
            new_status = st.selectbox("Status", ["Confirmed", "Pending", "Cancelled"], index=["Confirmed", "Pending", "Cancelled"].index(booking[6]))

            if st.button("Update Booking"):
                edit_booking(db, booking[0], new_date, new_time, new_status)

    db.close()

if __name__ == "__main__":
    main()

