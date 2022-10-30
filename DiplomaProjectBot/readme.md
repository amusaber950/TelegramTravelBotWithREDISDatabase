Telegram bot

Parts of the project:

1. Telegram-бот, named travel-data-bot.
2. main.py , contains body of bot, all working functional
3. hotels_api.py works with requests fron server, additional functions
4. redis_base.py initializes redis

Starting the bot:

Telegram must be downloaded. Clonning repository 
and installing libraries.
Bot start working after entering "/".

Requests:

Open accessed API Hotels,  rapidapi.com. To work with this API, user must: 
1. Register on rapidapi.com. 
2. Get rapidapi key  
3. Enter api key  in the field (x_rapidapi_key) in hotels_apy. Py submodule
4. Start redis database. For windows though bash ubuntu terminal: sudo service redis-server start

Bot functions

User can make next operations with commands:

1. Find top cheap hotels (/lowprice).
2. Find top high-priced hotels (/highprice). 
3. Find hotels according to price and distance from center  (/bestdeal). 
4. Open history of requests (/history) 
 

Commands description:

/lowprice:

After pressing user must be asked about: 

1. Town. 
2. Number of hotels to show, limited. 
3. Possibility to see images of hotels (“yes/no”) a. If yes, user will be asked about number of images. 
4. Result: names of hotels, address, price per night and rating, n number of photos.

/highprice

After pressing user must be asked about:

1. Town. 
2. Number of hotels to show, limited. 
3. Possibility to see images of hotels (“yes/no”) a. If yes, user will be asked about number of images. 
4. Result: names of hotels, address, price per night and rating, n number of photos.

/bestdeal

After pressing user must be asked about:

1. Town. 
2. Price.
3. Distance from center. 
4. Number of hotels to show, limited. 
5. Possibility to see images of hotels (“yes/no”) a. If yes, user will be asked about number of images. 
6. Result: names of hotels, address, price per night, total price, distance from center and rating, n number of photos.


/history 

After pressing user must get the history of his actions:
 History contains: 
1. Commands entered by user. 
2. Date of the request.
3. Found hotels. 
4. Result: names of hotels, address, price per night, total price, distance from center and rating, n number of photos.


With running  Python-code Telegram-bot can recognise following commands: 

● /help — help button.
● /lowprice — the cheapest hotels. 
● /highprice — high-priced hotels.
● /bestdeal — search hotels with filters.
● /history — history of actions. 


