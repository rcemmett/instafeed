Instafeed
=========

Instafeed is a class project that was designed to teach the inner working of software engineering and working in a
software team. It is a webapp that allows users to aggregate feed information from their social media websites. It has 
now become a small side project. 

Dev Notes for Internal
-----

Views needed by front end javascript

######Posting to Twitter:
* Javascript sends up message
* Returns nothing

######Posting to Facebook:
* Javascript sends up message
* Returns nothing

######Load Feeds from Twitter:
* Javascript sends up nothing
* Returns JSON object containing list of posts each with a message, author and date/time

######Load Feeds from Facebook:
* Javascript sends up nothing
* Return JSON object containing list of posts each with a message, author and date/time

#####Connect to our heroku database:
* psql -hec2-54-243-38-139.compute-1.amazonaws.com -U xtehbsbwkfjqdx -d decjmjca0u8vjf -p 5432 -W
* Password: EGjuqbG445JkPEIcpHtZRDs0lc


######Scheduled update:
* Javascript sends up a message that looks like this:
    * {'post_site': "1,2,or 3", 'message': "post", 'year': "year", 'month': "month", 'day': "day", 'hour': "hour", 'second': "second", 'microsecond': "microsecond"}
    * AJAX call to /scheduled_update
