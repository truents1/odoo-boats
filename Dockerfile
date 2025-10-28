# Dockerfile
FROM odoo:17

# Temporarily switch to root user to ensure installation permissions
USER root

# Install required Python packages. --no-cache-dir saves space.
RUN pip install "setuptools<81" email-validator --upgrade --no-cache-dir

# Switch back to the non-root 'odoo' user for security
USER odoo
