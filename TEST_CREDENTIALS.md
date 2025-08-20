# Test User Credentials

This file contains the login credentials for testing the application after running seed data.

## Admin Account
- **Email:** `admin@test.com`
- **Password:** `admin123`
- **Role:** Website Admin (Superuser)
- **Permissions:** Full access to admin panel and all features

## Regular Users
- **Email Pattern:** `user1@test.com`, `user2@test.com`, `user3@test.com`, etc.
- **Password:** `123456` (same for all users)
- **Roles:** Mix of regular users and website admins

## Quick Login Instructions

1. **For Admin Panel:**
   - Go to `/admin/`
   - Email: `admin@test.com`
   - Password: `admin123`

2. **For Public Site:**
   - Go to `/accounts/login/`
   - Use any of the user emails above
   - Password: `123456` for all users

## Testing Author/Artist Requests

You can test the author/artist request feature by:

1. Login as a regular user (e.g., `user1@test.com` / `123456`)
2. Go to novel upload page
3. Select "Create new author/artist" options
4. Login as admin (`admin@test.com` / `admin123`) to approve/reject requests

## Regenerating Data

To regenerate the seed data with fresh credentials:

```bash
python manage.py clear_seed_data --confirm
python manage.py seed_data --users 5 --authors 3 --novels 5
```

The credentials will remain the same pattern as described above.

## Notes

- Login uses **email addresses**, not usernames
- All users have active profiles and are ready for testing
- The admin account has superuser privileges for full access
- Regular users have the necessary permissions for novel management
