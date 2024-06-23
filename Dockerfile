FROM alpine:latest

# Install Apache2 and PHP
RUN apk --no-cache add apache2 php-apache2 php php-curl

# Configure Apache
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN mkdir -p /run/apache2

# Make apache listen to port 8080 instead of 80
RUN sed -i 's/Listen 80/Listen 8080/g' /etc/apache2/httpd.conf

# Expose port 8080
EXPOSE 8080

# Create a small sample php file
RUN echo "<?php phpinfo(); ?>" > /var/www/localhost/htdocs/index.php

# Handle configuration through environment variables
RUN echo "PassEnv SYSTEME_IO_API_KEY" >> /etc/apache2/httpd.conf
RUN echo "PassEnv SYSTEME_IO_BASE_URL" >> /etc/apache2/httpd.conf

# Start Apache
CMD ["httpd", "-D", "FOREGROUND"]
