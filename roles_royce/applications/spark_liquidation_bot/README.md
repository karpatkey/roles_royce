### Readme for info on development. (for Santi)
I've been trying to follow the structure you had for the anti liquidation bot, so for you would be easier to work with it. 
I've created a different utils file with the config just in case, but I believe it's better to have it all in one file. (the one 
used in the anti liquidation bot). There are only a couple of variables to add. 

The logic is that runs every x minutes (configurable) and checks if there are any positions that are below the liquidation price. 
Atm it only sends an alert, then implement whatever you need to do! 

I also left a bunch of things like the logger and messengers, so we can use them. 
 