# Database Configuration Specifications

## Required Environment Variables

### Database Connection Details

- **DB_HOST**: `localhost` (PostgreSQL server hostname)
- **DB_NAME**: `job_scraper_db` (Database name)
- **DB_USER**: `joeythe33rd` (Database username)
- **DB_PASSWORD**: `your_secure_password` (Database password - replace with actual)
- **DB_PORT**: `5432` (PostgreSQL default port)

### Authentication Security

- **SECRET_KEY**: `your_very_strong_secret_key_here` (JWT signing key - must be strong and unique)

## Usage Instructions

1. **Create .env file**:

   ```bash
   cp .env.example .env
   ```

2. **Update .env with your actual values**:

   ```
   DB_HOST=localhost
   DB_NAME=job_scraper_db
   DB_USER=joeythe33rd
   DB_PASSWORD=your_actual_password_here
   DB_PORT=5432
   SECRET_KEY=your_very_strong_secret_key_here
   ```

3. **Set file permissions** (optional but recommended):

   ```bash
   chmod 600 .env
   ```

## Security Notes

- Never commit the `.env` file to version control
- Use strong passwords for database credentials
- Consider using a password manager for secure storage
- Rotate passwords regularly
