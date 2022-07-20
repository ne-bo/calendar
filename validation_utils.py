import datetime

from email_validate import validate

from backend import CalendarManager

backend = CalendarManager()


def validate_email(email):
    if not validate(email_address=email,
                    check_format=True,
                    check_blacklist=False,
                    check_dns=False,
                    check_smtp=False,
                    smtp_debug=False
                    ):
        return 'Email format is incorrect '
    else:
        return ''


def validate_date_format(date_text):
    try:
        datetime.datetime.strptime(date_text, backend.format)
        return ''
    except ValueError:
        return 'The ' + date_text + ' should have format YYYY-mm-dd-HH-MM '


def validate_time(start, end):
    start_format = validate_date_format(start)
    end_format = validate_date_format(end)
    if start_format == '' and end_format == '':
        if datetime.datetime.strptime(start, backend.format) < datetime.datetime.strptime(end, backend.format):
            return ''
        else:
            return 'The start should be earlier than the end '
    else:
        return start_format + end_format


def validate_the_input_data(title, email, start, end):
    time_output = validate_time(start, end)
    email_output = validate_email(email)
    if time_output != '' or email_output != '':
        return time_output + email_output
    else:
        return ''