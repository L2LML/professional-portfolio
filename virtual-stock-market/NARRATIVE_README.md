# Virtual-Stock-Market
 Please see newer README.md file
 
 The version below is a narrative written by one of the team members
 Demo Market 25
 
What was this project and what was the objective?

This is Market 25 - our objective was to create a stock trading game that utilized real and current stock price information from an assortment of stocks that users could buy or sell within a custom date limited interval. We have data for 25 different stocks, hence the name.
Who are the users?
This is a simplified version of stock trading that can be played by anyone who has a casual understanding of how stocks are bought or sold or someone who is learning about stock trading for the first time.
What are our user stories?
We have two for this demo. The first is a user story for someone who has heard about Market 25 and would like to register, organize a game, and invite another user that they know already plays Market 25.
The second user story we will demo is the user who already plays Market 25. They will log in, view and manage their game invitations, check the leaderboard of a game they are involved in, and then proceed to their own portfolio within that game to make trades.

User Story One

Register 
	- go to register screen and create a new user profile
	- login once re-directed to login screen
User Home Page/Splash Page
	- Create a game - Create a uniquely named game that has a custom start and end date, when the end date set by the organizer is reached all stocks are converted back to "cash" and the user at the top of the leaderboard wins.


	- View games - once the game has been created it will appear in the view games section of the User Home Page, it displays their current portfolio value (which starts at 100,000 in "cash"), and the end date set by the organizer. The user may click it to see the current leaderboard.
	- Game Details - once you have clicked into the game from View Games, you can see the leaderboard on the left, and on the right you have the option to invite users to that game, using their email.
	- Once the email has been entered and the invite button has been pressed the text field will clear and the invite will be visible to the user you have invited.
	- to return to the user home page you may press the home button in the upper left, no matter where you are in the game.
	- to logout, click logout in the upper right


	- Login once more
	- User Home Page - in addition to creating and viewing games on the home page you can also see the games that you have been invited to. You are able to decline an invite or accept, should you accept an invite you will see your list of games refresh to show you the game you now have access to.
	- Leaderboard - on the leaderboard or details page you can see your current portfolio value relative to the other users playing in this specific game, as well as when the game will end and all positions will close. You have a different portfolio in each specific game.
	- the button at the bottom of the leaderboard will allow you to view the granular details of your portfolio, and perform trades.


	- Portfolio - this page displays the current funds you can purchase stock with, the total value of the stocks you hold, and the combined portfolio value. On the left, you can see the stocks you hold, how many shares of each you currently hold, and the combined total by stock. On the left you can see a list of 25 stocks and their actual stock prices, at the bottom of the list you will see the last time that it refreshed - we are rate limited by the API we use, but we do get real data.
	- Buy - You can click an entry in the table on the right to populate the stock ticker field as well as the number of shares field. Once you click to buy you will be shunted to the leaderboard page, if you wish to continue trading you may return to the portfolio, but we prefer to give you the option to see your competitor’s value and make a decision.
	- Sell - functions similar to buy, you may select from the column on the left to fill the fields and click "sell" this will also shunt you to the leaderboard page. This feature also prevents users from remaining inside their portfolio and continuing to trade once the time limit for the game has been reached.
	- Game end - when the limit is reached the view portfolio button will disappear and the display will change, all stocks will have been sold and all portfolio values are now final. The user at the top of the leaderboard has won the game!  
	
