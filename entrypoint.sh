
#!/bin/sh

# Initialize the database
python -m src.db.init_db

# Run the application
exec uvicorn src.app:app --host 0.0.0.0 --port 8000
