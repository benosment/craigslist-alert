craigslist-alert
================

Alerts when new Craigslist posts which match certain criteria have been posted
 - search using a query, filter out words using a blacklist
 - a history is retained so you are only emailed for new posts
 - typically used with cron to run, say, every 1 hour to check for
   new posts

Example:
    $ craigslist-alert/craigslist_alert.py lego --location 'raleigh' --category 'taa

Note:
 - in order for email to work correctly, you need to put your
   credentials in your environment (e.g. .bashrc file has to have
   MAIL_USERNAME and MAIL_PASSWORD defined)


TODO
 - Create an HTML version of the email
 - Bold/distinguish new items that have certain attributes
