This is a toy project for the calendar reservations booking.

How it supposed to work:

# Problem statement

Imagine people want to meet with you and are always asking for available slots in your calendar. For the first couple of times you check you agenda and answer yourself, but the more people ask the more you realize how easy it would be to just publish your availabilities and let people book their meetings with you themselves. This is what we'd like you to implement 

# Requirements

The service should be implemented as a web application with:

### Database that stores availabilities and reservations

- `availabilities` table should contain `start` and `end` columns that define the duration of a time slot.
- `reservations` table should contain the following columns:
    - `start` - start time of the reserved event
    - `end` - end time of the event
    - `title` - title of the event
    - `email` - email of a person making the reservation

> For the sake of simplicity you can choose to use a SQLite DB, or any dockerized DB you like.
> 

Feel free to add more columns to these tables add more tables if you find it necessary

### Backend

The backend of an application should have an API to:

- **create** and **delete** availabilities
- **create** reservations (Note that reservations can be shorter than available time slots)
- **delete** reservations (email should be provided with the request to validate if it matches the one specified at event creation)
- **list** currently available slots

### Frontend

From the frontend you should be able to 

- see slots available for reservations
- provide a `start`, `end`, `title` and `email` for a new reservation and save it

# Run the code

Use `requiremnts.txt` to install all required packages

If you want to create your own availabilities open `frontend.py` 
and add corresponding code at the line 13. 
Interface for availability creation is not described in the requirements, so it's not implemented.

If you think you can be satisfied with pre-created availabilities just do nothing.

To run the frontend:

`export FLASK_APP=frontend`

`flask run`

Go to http://127.0.0.1:5000/ and try the interface. 
I added reservation removal interface for the convenience, despite it wasn't required.