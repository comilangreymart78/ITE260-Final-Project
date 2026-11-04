
from datetime import datetime, date, timedelta

students, appointments = [], []

TIME_SLOTS = ["10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM",
              "1:30 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM"]

PURPOSES = {
    "1": "Request Documents",
    "2": "Registration Concern",
    "3": "Ask for Assistance",
    "4": "Other Registrar Concern"}


# DISPLAY TABLE
def table(headers, rows):
    if not rows:
        print("No records found.")
        return

    rows = [[str(x) for x in r] for r in rows]
    widths = [max(len(str(h)), *(len(r[i]) for r in rows))
              for i, h in enumerate(headers)]
    line = "+-" + "-+-".join("-" * w for w in widths) + "-+"

    print(line)
    print("| " + " | ".join(str(h).ljust(widths[i])
                             for i, h in enumerate(headers)) + " |")
    print(line)

    for r in rows:
        print("| " + " | ".join(r[i].ljust(widths[i])
                                 for i in range(len(headers))) + " |")
    print(line)


def purpose_info(a):
    return a[4], a[6] if len(a) > 6 and a[6] else "-"


# STUDENT REGISTRATION
def register():
    print("\n===== STUDENT REGISTRATION =====")

    while True:
        sid = input("Student ID (02-0000-000000): ")
        if (len(sid) == 14 and sid[:2] == "02" and sid[2] == "-"
                and sid[7] == "-" and sid[3:7].isdigit()
                and sid[8:].isdigit()):
            if any(s[0] == sid for s in students):
                print("Student ID already registered.")
                return
            break
        print("INVALID: Use 02-0000-000000 format.")

    while True:
        name = input("Full Name: ").strip()
        if name and name.replace(" ", "").isalpha() and len(name.split()) >= 2:
            name = " ".join(w.capitalize() for w in name.split())
            break
        print("INVALID: Enter a valid first and last name.")

    while True:
        username = input("Username: ")
        if not username.isalpha():
            print("INVALID: Letters only.")
        elif any(s[2] == username for s in students):
            print("Username already taken.")
            return
        else:
            break

    while True:
        password = input("Password: ")
        if (len(password) >= 8 and any(c.isalpha() for c in password)
                and any(c.isdigit() for c in password)):
            break
        print("Password needs 8+ characters, a letter, and a number.")

    while input("Confirm Password: ") != password:
        print("INVALID: Passwords do not match.")

    students.append([sid, name, username, password])
    print("Registration successful!")


# STUDENT LOGIN
def login():
    u, p = input("Username: "), input("Password: ")
    for s in students:
        if s[2] == u and s[3] == p:
            print("Welcome,", s[1])
            student_menu(s)
            return
    print("INVALID: Incorrect username or password.")


def booked(d, t=None):
    return any(a[2] == d and (t is None or a[3] == t)
               and a[5] != "Cancelled" for a in appointments)


# BOOK APPOINTMENT
def book(s):
    print("\n===== BOOK APPOINTMENT =====")

    while True:
        try:
            appt = datetime.strptime(input("Date (MM/DD/YYYY): "),
                                     "%m/%d/%Y").date()
        except ValueError:
            print("INVALID: Enter a valid date.")
            continue

        d = appt.strftime("%m/%d/%Y")
        if appt <= date.today():
            print("INVALID: Date must be tomorrow or later.")
        elif appt > date.today() + timedelta(days=14):
            print("INVALID: Booking is limited to 14 days.")
        elif appt.weekday() == 6:
            print("INVALID: Sunday is unavailable.")
        elif any(a[0] == s[0] and a[2] == d and a[5] != "Cancelled"
                 for a in appointments):
            print("INVALID: You already have an appointment on this date.")
        else:
            break

    table(["No.", "Time", "Status"],
          [[i, t, "BOOKED" if booked(d, t) else "AVAILABLE"]
           for i, t in enumerate(TIME_SLOTS, 1)])

    while True:
        c = input("Choose time slot (1-9): ")
        if c.isdigit() and 1 <= int(c) <= 9:
            t = TIME_SLOTS[int(c) - 1]
            if not booked(d, t):
                break
            print("INVALID: Time already booked.")
        else:
            print("INVALID: Choose 1-9.")

    for k, v in PURPOSES.items():
        print(k + ".", v)

    while True:
        c = input("Choose purpose (1-4): ")
        if c in PURPOSES:
            break
        print("INVALID: Choose 1-4.")

    concern = ""
    if c == "4":
        while not concern:
            concern = input("State your specific concern: ").strip()
            if not concern:
                print("INVALID: Concern cannot be empty.")

    appointments.append([s[0], s[1], d, t, PURPOSES[c],
                         "Scheduled", concern])
    print("Appointment booked successfully!")


# STUDENT APPOINTMENTS
def view_appointment(s):
    rows = [[a[0], a[2], a[3], *purpose_info(a), a[5]]
            for a in appointments if a[0] == s[0]]
    table(["Student ID", "Date", "Time", "Purpose", "Concern", "Status"],
          rows)


# CANCEL APPOINTMENT: AT LEAST 2 DAYS BEFORE
def cancel(s):
    active = [a for a in appointments
              if a[0] == s[0] and a[5] == "Scheduled"]

    table(["Date", "Time", "Purpose", "Concern"],
          [[a[2], a[3], *purpose_info(a)] for a in active])

    if not active:
        print("No scheduled appointment found.")
        return

    while True:
        d = input("Appointment date to cancel (MM/DD/YYYY): ")
        try:
            appt = datetime.strptime(d, "%m/%d/%Y").date()
            d = appt.strftime("%m/%d/%Y")
        except ValueError:
            print("INVALID: Enter a valid date.")
            continue

        if appt <= date.today() + timedelta(days=1):
            print("INVALID: Cancellation must be at least 2 days before.")
            return

        choices = [a for a in active if a[2] == d]
        if not choices:
            print("INVALID: No scheduled appointment on that date.")
            continue
        break

    if len(choices) > 1:
        for i, a in enumerate(choices, 1):
            print(f"{i}. {a[3]}")
        while True:
            c = input("Choose time: ")
            if c.isdigit() and 1 <= int(c) <= len(choices):
                a = choices[int(c) - 1]
                break
            print("INVALID: Choose a listed number.")
    else:
        a = choices[0]

    while True:
        ans = input("Request cancellation? (Y/N): ")
        if ans == "Y":
            a[5] = "Cancellation Requested"
            print("Cancellation request sent.")
            return
        elif ans == "N":
            print("Cancellation request withdrawn.")
            return
        print("INVALID: Enter uppercase Y or N.")


# REGISTRAR SCHEDULE: DISPLAY ALL DATES
def view_schedule():
    print("\n===== REGISTRAR SCHEDULE =====")
    rows = []

    ordered = sorted(
        appointments,
        key=lambda a: (
            datetime.strptime(a[2], "%m/%d/%Y").date(),
            TIME_SLOTS.index(a[3])
        )
    )

    for a in ordered:
        purpose, concern = purpose_info(a)
        rows.append([a[2], a[3], a[0], a[1],
                     purpose, concern, a[5]])

    table(["Date", "Time", "Student ID", "Name",
           "Purpose", "Concern", "Status"], rows)


# STUDENT MENU
def student_menu(s):
    while True:
        print("\n===== STUDENT MENU =====")
        print("1. Book Appointment\n2. View Appointment")
        print("3. Cancel Appointment\n4. Logout")
        c = input("Choose: ")

        if c == "1":
            book(s)
        elif c == "2":
            view_appointment(s)
        elif c == "3":
            cancel(s)
        elif c == "4":
            return
        else:
            print("INVALID: Choose 1-4.")


# REGISTRAR MENU
def registrar():
    print("\n===== REGISTRAR LOGIN =====")
    u = input("Username: ")
    p = input("Password: ")

    if u != "registrar" or p != "1234":
        print("INVALID: Incorrect username or password.")
        return

    while True:
        print("\n===== REGISTRAR MENU =====")
        print("1. View Appointments\n2. Manage Appointment")
        print("3. View Schedule\n4. Logout")
        c = input("Choose: ")

        if c == "1":
            table(["Student ID", "Name", "Date", "Time",
                   "Purpose", "Concern", "Status"],
                  [[a[0], a[1], a[2], a[3], *purpose_info(a), a[5]]
                   for a in appointments])

        elif c == "2":
            sid = input("Student ID: ")
            matches = [a for a in appointments if a[0] == sid
                       and a[5] in ("Scheduled", "Cancellation Requested")]

            table(["Date", "Time", "Purpose", "Concern", "Status"],
                  [[a[2], a[3], *purpose_info(a), a[5]] for a in matches])

            if not matches:
                print("No manageable appointments found.")
                continue

            while True:
                d = input("Appointment date (MM/DD/YYYY): ")
                try:
                    d = datetime.strptime(d, "%m/%d/%Y").strftime("%m/%d/%Y")
                except ValueError:
                    print("INVALID: Enter a valid date.")
                    continue

                choices = [a for a in matches if a[2] == d]
                if choices:
                    break
                print("INVALID: No appointment on that date.")

            if len(choices) > 1:
                for i, a in enumerate(choices, 1):
                    print(f"{i}. {a[3]} - {a[5]}")
                while True:
                    x = input("Choose appointment: ")
                    if x.isdigit() and 1 <= int(x) <= len(choices):
                        a = choices[int(x) - 1]
                        break
                    print("INVALID: Choose a listed number.")
            else:
                a = choices[0]

            if a[5] == "Cancellation Requested":
                print("1. Approve Cancellation\n2. Decline Cancellation")
                x = input("Choose: ")
                if x == "1":
                    a[5] = "Cancelled"
                    print("Cancellation approved.")
                elif x == "2":
                    a[5] = "Scheduled"
                    print("Cancellation declined.")
                else:
                    print("INVALID: No changes made.")
            else:
                print("1. Complete\n2. Cancel")
                x = input("Choose: ")
                if x == "1":
                    a[5] = "Completed"
                    print("Appointment completed.")
                elif x == "2":
                    a[5] = "Cancelled"
                    print("Appointment cancelled.")
                else:
                    print("INVALID: No changes made.")

        elif c == "3":
            view_schedule()
        elif c == "4":
            print("Registrar logged out.")
            return
        else:
            print("INVALID: Choose 1-4. Try again.")


# MAIN MENU
while True:
    print("\n===== STUDENT REGISTRAR SYSTEM =====")
    print("1. Student Registration\n2. Student Login")
    print("3. Registrar Login\n4. Exit")
    choice = input("Choose: ")

    if choice == "1":
        register()
    elif choice == "2":
        login()
    elif choice == "3":
        registrar()
    elif choice == "4":
        print("Thank you for using the system.")
        break
    else:
        print("INVALID: Choose 1-4.")