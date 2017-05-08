Reddit
============================

This application provides a server to get reddit comments and submission between two given timestamps.
It also has a script to fetch this data and store it into a local database.

Each of these is Dockerized. To start everything run:
```
sudo docker-compose up
```

This uses port 27017 for the database and 5000 for the webserver.
