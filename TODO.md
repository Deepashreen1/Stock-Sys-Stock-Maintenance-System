# TODO: Password Strength Validation for Signup

## Steps to Complete:

- [x] Update static/style.css: Add CSS classes for password strength indicator (e.g., .password-strength, .weak, .medium, .strong).
- [x] Update templates/signup.html: Add div for strength display below password input, and inline JavaScript for real-time validation (check length >=8 and special char presence; update indicator with text/color; prevent submit if weak).
- [x] Update app.py: In /signup POST route, add server-side password validation (length >=8 and at least one special char using regex); flash error and redirect if invalid; proceed with user creation only if valid.
- [x] Test: Completed. Server-side validation confirmed: Weak password redirects back to signup with error; strong password creates user and redirects to login. Client-side JS should be verified manually in browser for real-time indicator.
