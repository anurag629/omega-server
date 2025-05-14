# Troubleshooting Guide

This guide provides solutions to common issues that may arise when working with the Codercops Omega application.

## Authentication Issues

### Unable to Log In

**Symptoms:**
- Login fails with "Invalid email or password" message
- Login fails with "Email not verified" message
- Login fails with "Account not approved" message

**Solutions:**

1. **Invalid Credentials:**
   - Ensure you're using the correct email and password
   - Try resetting your password through the admin interface
   - Check for typos in your email address

2. **Email Not Verified:**
   - Check your email for the verification link
   - If no email was received, request a new verification email
   - Admin can manually verify an email in the admin interface by setting `email_verified = True`

3. **Account Not Approved:**
   - Wait for an administrator to approve your account
   - Administrator can approve accounts in the Django admin interface
   - Contact the administrator if approval is taking too long

### Token Refresh Issues

**Symptoms:**
- API requests fail with 401 Unauthorized after working for a while
- Unable to refresh access token

**Solutions:**
- Ensure your refresh token is valid and not expired
- If refresh token is expired, you need to log in again
- Check that you're passing the correct refresh token to the token refresh endpoint

## Manim Script Generation Issues

### Script Generation Fails

**Symptoms:**
- Error message when trying to generate a script
- Empty script response
- API returns 500 Internal Server Error

**Solutions:**

1. **API Key Issues:**
   - Check if your AI provider API keys are valid
   - Verify API keys are set correctly in the `.env` file
   - Check for API rate limiting or quota issues

2. **Invalid Prompt:**
   - Ensure your prompt is clear and specific
   - Try simplifying your prompt
   - Check prompt length (very long prompts may fail)

3. **Network Issues:**
   - Check your internet connection
   - Verify the AI provider service is operational
   - Check for firewall or proxy issues

### Script Execution Fails

**Symptoms:**
- Script is generated but execution fails
- Error message during execution
- Video output is not generated

**Solutions:**

1. **Script Syntax Errors:**
   - Check the generated script for Python syntax errors
   - Some complex animations may not be properly generated
   - Try simplifying your prompt to get a simpler script

2. **Docker Container Issues:**
   - Ensure the Manim Docker container is running
   - Check Docker logs: `docker-compose logs manim`
   - Restart the Manim container: `docker-compose restart manim`

3. **Media Directory Permissions:**
   - Check if the media directory has write permissions
   - Ensure the Docker container can write to the media directory
   - Fix permissions if needed: `chmod -R 777 media/` (for development only)

## Docker and Deployment Issues

### Docker Container Fails to Start

**Symptoms:**
- Docker container exits immediately after starting
- Error messages in Docker logs
- Service unavailable

**Solutions:**

1. **Port Conflicts:**
   - Check if another service is using the same port
   - Change the port mapping in `docker-compose.yml`
   - Stop conflicting services

2. **Environment Variables:**
   - Verify `.env` file exists and is properly formatted
   - Check for missing required environment variables
   - Fix any syntax errors in `.env` file

3. **Database Connection:**
   - Ensure PostgreSQL container is running
   - Check database credentials in `.env`
   - Wait for the database to initialize before starting the web container

### Media Files Not Displaying

**Symptoms:**
- Videos or images not showing up
- 404 errors when accessing media URLs
- Broken media links

**Solutions:**

1. **Media URL Configuration:**
   - Check `MEDIA_URL` and `MEDIA_ROOT` in `settings.py`
   - Ensure `BASE_URL` is set correctly in `.env`
   - Verify that the URLs are properly constructed

2. **File Permissions:**
   - Check file permissions in the media directory
   - Ensure files are readable by the web server
   - Set appropriate permissions on media files

3. **Nginx Configuration (for production):**
   - Verify Nginx is configured to serve media files
   - Check media location directives in Nginx config
   - Restart Nginx after configuration changes

## Database Issues

### Migration Errors

**Symptoms:**
- Migration errors during deployment
- Database table conflicts
- Missing tables or columns

**Solutions:**

1. **Migration Conflicts:**
   - Check migration files for conflicts
   - Consider rolling back problematic migrations
   - Create a new migration to resolve conflicts

2. **Database Synchronization:**
   - Run `python manage.py migrate --fake-initial` if tables already exist
   - For major issues, consider rebuilding the database from scratch
   - Backup data before attempting migration fixes

3. **PostgreSQL Version Compatibility:**
   - Ensure your PostgreSQL version is compatible with Django
   - Check for PostgreSQL-specific syntax in migrations
   - Update PostgreSQL if needed

## Performance Issues

### Slow Script Generation

**Symptoms:**
- Script generation takes a long time
- Timeout errors during generation
- Browser hangs during generation request

**Solutions:**

1. **AI Provider Latency:**
   - Some AI providers may have higher latency
   - Consider switching to a faster provider
   - Optimize prompt to reduce complexity

2. **Server Resources:**
   - Check server CPU and memory usage
   - Consider scaling up server resources
   - Optimize request handling in the application

### Slow Animation Rendering

**Symptoms:**
- Animation execution takes a very long time
- Timeouts during animation rendering
- Incomplete video output

**Solutions:**

1. **Manim Configuration:**
   - Check Manim rendering settings
   - Consider reducing video quality or resolution
   - Split complex animations into simpler ones

2. **Container Resources:**
   - Ensure Docker container has sufficient resources
   - Increase CPU and memory limits in Docker configuration
   - Consider using a more powerful host for rendering

## Email Delivery Issues

**Symptoms:**
- Verification emails not received
- Invitation emails not delivered
- Password reset emails missing

**Solutions:**

1. **Email Configuration:**
   - Verify email settings in `.env` and `settings.py`
   - Check `EMAIL_BACKEND`, `EMAIL_HOST`, and other email settings
   - For development, use console email backend to see emails in console

2. **SMTP Server Issues:**
   - Ensure SMTP server is operational
   - Check for authentication errors in logs
   - Verify port and TLS/SSL settings

3. **Email Deliverability:**
   - Check spam/junk folders
   - Ensure sending domain has proper SPF and DKIM records
   - Use a reliable email service provider

## Getting Help

If you're still experiencing issues after trying these troubleshooting steps, you can:

1. Check the application logs for more detailed error information:
   ```bash
   docker-compose logs web
   docker-compose logs manim
   ```

2. Look for similar issues in the project's issue tracker

3. Contact the system administrator or development team with:
   - Detailed description of the issue
   - Steps to reproduce the problem
   - Error messages and logs
   - Environment information (browser, OS, etc.) 