# Gym Management Dashboard
#### Video Demo: <https://youtu.be/alM8JxZ2nCI>
#### Description:

My final project for CS50x is a **Gym Management Dashboard**, a web application built with Python, Flask, and SQLite. 

The idea came from a question of my trainer asking if i know about an app to record and track monthly pays of their clients. Many still rely on paper and pen here where i live, which makes it really easy to lose track of late payments or confuse dates.

This app gives gym owners a simple place to manage their clients, record membership payments, and check their monthly and overall earnings in real time.

---

### How the App Works & What I Built

When a user visits the site for the first time, they land on a simple welcome page that explains what the app does, with quick links to log in or register a new account. 

Once logged in, the user is taken to the main Dashboard. Here, they can see three main cards:
1. **Active Clients:** How many people currently have an active membership.
2. **Monthly Earnings:** Total money collected during the current month.
3. **Total Revenue:** Total money collected since the account was created.

From the navigation bar or the quick action buttons, gym owners can:
- Add new clients with their contact details.
- View the full client list with color-coded badges showing if their membership is **Active** (green) or **Overdue** (red).
- Edit client details if their phone number or name changes.
- Record new payments choosing from a list of registered clients.
- Review a full payment history showing who paid, how much, and on what date.

---

### Design Decisions

While building this project, I had to make several decisions about how to structure the data and the user interface:

#### 1. Calculating Active Status on the Fly (Instead of Static Flags)
At first, I thought about adding a column in the database like `status = "Active"`. But I realized that if a month passes, that text wouldn't update by itself unless I manually wrote extra code to check it every day. 

Instead, I decided to calculate whether a client is active dynamically every time the page loads. The SQL query checks the date of the client's last payment and compares it to today's date using SQLite's `julianday()` function. If the last payment was made within the last 30 days, the app shows them as **Active**. If it's been more than 30 days (or if they haven't paid yet), they show up as **Overdue**.

#### 2. Keeping User Data Private & Separated
Since different gym owners might use the application, I needed to make sure that User A could never see or modify the clients or payments of User B. To solve this, every single table (`clients` and `payments`) holds a `user_id` linked to the logged-in user's session. Every SQL `SELECT`, `INSERT`, or `UPDATE` explicitly checks `WHERE user_id = session["user_id"]`.

#### 3. Preventing Errors when No Clients Exist
I wanted the app to feel smooth and not crash with weird SQL errors. For example, if a user clicks on "Register Payment" right after creating their account when they have 0 clients, the backend catches this, shows a friendly alert message, and automatically redirects them to the "Add Client" page first.

#### 4. Welcome Page vs. Forcing Login
Instead of sending unauthenticated visitors straight to a cold login form, the root route (`/`) detects if there is an active session. If not, it displays a public landing page explaining the features of the app before asking them to log in or sign up.

#### 5. Flexible Amount Entry for Payments
When registering a payment, the application dynamically pre-fills the suggested fee based on the client's current status and the business settings. However, the amount input remains fully editable. This ensures gym owners have the operational flexibility to adjust prices manually—for instance, waiving late fees for new members, applying special promotional discounts, or adjusting charges on a case-by-case basis before confirming the transaction.

---

### File Structure & Description

* **`app.py`**: The main Python file containing all the Flask routes (`/`, `/login`, `/register`, `/clients`, `/add_payment`, `/payments`, etc.). It manages user sessions, form submissions, and database queries.
* **`init_db.py`**: A Python script used to set up the SQLite database (`gym.db`). It creates the `users`, `clients`, and `payments` tables with foreign keys. It uses `DROP TABLE IF EXISTS` at the beginning so it can be re-run anytime to start with a fresh, clean database.
* **`templates/`**:
  * **`layout.html`**: The main HTML layout using Bootstrap 5. It includes the navigation bar, container for flash messages, and Jinja2 block tags so other templates can extend it.
  * **`welcome.html`**: Public landing page for non-logged-in visitors.
  * **`index.html`**: The main control panel featuring the grid of metrics and quick action buttons.
  * **`clients.html`**: Table listing all registered clients alongside their active/overdue status.
  * **`add_client.html` & `edit_client.html`**: Forms for adding and updating client contact information.
  * **`add_payment.html`**: Form to select a client and record a membership payment.
  * **`payments.html`**: Log showing all past payments ordered by date.
  * **`settings.html`**: Form which the owner of the gym can establish and change the monthly fee, due day and the late fee.
  * **`static/css/main.css`**: Custom CSS rules that tweak card hover animations and background colors alongside Bootstrap.

---

### How I Tested the Project

To make sure everything worked as expected, I ran through a series of manual integration tests starting from a completely blank database:
1. I ran `python init_db.py` to wipe the database clean.
2. I tried opening `/clients` directly without logging in to verify that I was blocked and sent to the login page.
3. I registered a new account and checked that the dashboard showed `$0.00` earnings and `0` active clients.
4. I created a client and verified their initial status was **Overdue**.
5. I added a `$50.00` payment for that client and confirmed that their status instantly changed to **Active**, while the dashboard metrics updated to `$50.00`.
6. I edited the client's phone number to make sure updates worked without breaking past payment records.

---

### Future Ideas

If I keep working on this project in the future, here are a few things I would like to add:
**Automatic WhatsApp/Email Reminders:** Send a automated message to clients when their 30-day membership is 3 days away from expiring.
**Export to CSV:** A button on the payment history page so gym owners can download their monthly records for accounting.
**Payment Gateway Integration:** Connecting Mercado Pago so clients can pay online through a link.
---

### Academic Honesty & AI Statement

In line with CS50x policies for the Final Project, I used AI (only Google Gemini) as a helpful assistant to speed up my work. Specifically, I used it to help me debug Jinja2 template errors, fix layout issues with Bootstrap, and write the SQLite date comparison queries using `julianday()`. All core architecture, database design, feature choices, and code implementation were guided and written by me.