import os.path
import sqlite3
import sqlite3 as sl
from datetime import datetime


class CalendarManager:
    def __init__(self):
        self.name = 'My calendar'
        if os.path.exists('my-test.db'):
            self.database = sl.connect('my-test.db')
        else:
            con = sl.connect('my-test.db')
            with con:
                con.execute("""
                    CREATE TABLE availabilities (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        start timestamp,
                        end timestamp,
                        start_formatted TEXT,
                        end_formatted TEXT
                    );
                """)

                con.execute("""
                    CREATE TABLE reservations (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        start timestamp,
                        end timestamp,
                        start_formatted TEXT,
                        end_formatted TEXT,
                        title TEXT,
                        email TEXT
                    );
                """)
        self.format = "%Y-%m-%d-%H-%M"
        self.database.row_factory = sqlite3.Row

    def create_availability(self, start, end):
        start_timestamp, end_timestamp = self.convert_and_check_start_and_end(start, end)
        all_possible_slots = self.check_if_this_time_intersects(start, end).fetchall()

        sql = 'INSERT INTO availabilities (start, end, start_formatted, end_formatted) values(?, ?, ?, ?)'
        # add new availability in case it doesn't intersect with existing
        if len(all_possible_slots) == 0:
            data = [
                (start_timestamp, end_timestamp, start, end),
            ]
            with self.database:
                self.database.executemany(sql, data)
        else:  # otherwise extend the existing slot
            new_start = start_timestamp
            new_end = end_timestamp
            for slot in all_possible_slots:
                new_start = min(new_start, slot['start'])
                new_end = max(new_end, slot['end'])
                # remove all intersected slots
                self.remove_availability(slot['id'])
            # insert a new huge slot
            data = [
                (new_start, new_end,
                 datetime.fromtimestamp(new_start).strftime(self.format),
                 datetime.fromtimestamp(new_end).strftime(self.format)),
            ]
            with self.database:
                self.database.executemany(sql, data)

    def remove_availability(self, id):
        sql = 'DELETE FROM availabilities WHERE id = ?'
        data = (id,)
        with self.database:
            self.database.execute(sql, data)

    def list_availabilities(self):
        for slot in self.get_all_availabilities():
            print('\n')
            for k, v in slot.items():
                print(k + ' ' + v, end=' ')

    def get_all_availabilities(self):
        with self.database:
            return self.database.execute('SELECT * FROM availabilities').fetchall()

    def get_all_reservations(self):
        with self.database:
            return self.database.execute('SELECT * FROM reservations').fetchall()

    def create_reservation(self, start, end, title, email):
        start_timestamp, end_timestamp = self.convert_and_check_start_and_end(start, end)
        all_possible_slots = self.check_if_this_time_available(start, end).fetchall()
        if len(all_possible_slots) > 0:
            # insert new reservation
            sql = 'INSERT INTO reservations ' \
                  '(start, end, start_formatted, end_formatted, title, email) ' \
                  'values(?, ?, ?, ?, ?, ?)'
            data = [
                (start_timestamp, end_timestamp, start, end, title, email),
            ]
            with self.database:
                self.database.executemany(sql, data)
            # for affected availabilities
            for slot in all_possible_slots:
                # split affected availability
                self.remove_availability(slot['id'])
                if slot['start'] < start_timestamp:
                    self.create_availability(slot['start_formatted'], start)
                if end_timestamp < slot['end']:
                    self.create_availability(end, slot['end_formatted'])
        else:
            raise ValueError('This reservation can\'t be made because of the time slot is busy')

    def remove_reservation(self, start, end, email):
        verification_sql = 'SELECT * FROM reservations WHERE start_formatted = ? and end_formatted = ?'
        data = (start, end)
        with self.database:
            reservation_to_delete = self.database.execute(verification_sql, data).fetchall()
            if len(reservation_to_delete) == 1:
                reservation_to_delete = reservation_to_delete[0]
                if reservation_to_delete['email'] == email:
                    sql = 'DELETE FROM reservations WHERE id = ?'
                    self.database.execute(sql, (reservation_to_delete['id'],))
                    # create availability instead of the removed reservation
                    self.create_availability(reservation_to_delete['start_formatted'],
                                             reservation_to_delete['end_formatted'])
                else:
                    raise ValueError('The email is incorrect')
            else:
                raise ValueError('There is no reservation with this start/end')

    def convert_and_check_start_and_end(self, start, end):
        start_timestamp = datetime.strptime(start, self.format).timestamp()
        end_timestamp = datetime.strptime(end, self.format).timestamp()
        assert start_timestamp < end_timestamp, f'You create slot with {start} >= {end}'
        return start_timestamp, end_timestamp

    def check_if_this_time_available(self, start, end):
        start_timestamp, end_timestamp = self.convert_and_check_start_and_end(start, end)
        with self.database:
            sql = 'SELECT * FROM availabilities WHERE start <= ? and end >= ?'
            data = (start_timestamp, end_timestamp)
            all_possible_slots = self.database.execute(sql, data)
            return all_possible_slots

    def check_if_this_time_intersects(self, start, end):
        start_timestamp, end_timestamp = self.convert_and_check_start_and_end(start, end)
        with self.database:
            sql = 'SELECT * FROM availabilities WHERE (start <= ? and end >= ?) or (start <= ? and end >= ?) '
            data = (start_timestamp, start_timestamp, end_timestamp, end_timestamp)
            all_possible_slots = self.database.execute(sql, data)
            return all_possible_slots
