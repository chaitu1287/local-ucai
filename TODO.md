- Make sure client and server are communicating with an Auth token
- Once taxonomy is fully in the database - if risk, attack or product don't exist throw an error instead of creating
- Cleanup all dependencies
- Setup proper logging for the modal workers. Instead of using the file system logging

NOTES:
- Config list endpoints don't load relationships for performance intentionally.