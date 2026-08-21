# Skillverse Dadar Web CRM

This Flask application is the focused web version of the desktop CRM. It contains user login, enquiries and follow-ups only. A lead becomes available through the `joined_students` database view when its status changes to `Joined`.

## First-time setup

1. Run `supabase_web_migration.sql` in the Supabase SQL editor.
2. Add a strong `FLASK_SECRET_KEY` to `.env`. For a deployed server, use the backend/service Supabase key as `SUPABASE_KEY` and never expose that key in browser code.
3. Install dependencies:

   ```powershell
   .\venv\Scripts\python.exe -m pip install -r requirements-web.txt
   ```

4. Create the first administrator:

   ```powershell
   .\venv\Scripts\python.exe -m flask --app app create-user --role admin
   ```

5. Start locally:



Open `http://127.0.0.1:5000`. The first administrator can create counsellor accounts from the Users page.

## Existing enquiries

Old enquiries have no `assigned_user_id`. Admins can see them, but counsellors cannot until they are assigned. Use the commented SQL at the bottom of the migration for a one-time bulk assignment, or edit individual leads as an administrator.
