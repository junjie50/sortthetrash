# **Context**:
This game was created for SUTD term 1 project Computational Design Thinking.  
We are creating a game to help those people who wants to recycle but do not know what can be   recycled in the different recycling categories.Since they do not know what can be recycled, they will throw the trash into the general trash category. Since building a habit start from a young age, this game can be used to teach children and teens more interestingly compared to textbooks.We got our inspiration from this article https://www.todayonline.com/singapore/most-singaporeans-care-about-packaging-waste-dont-know-which-materials-are-recyclable-study-1959081

# **Frameworks**
Tinkter was used as the main library for developing the userbased interface.

# **Game Play**
The software is played as a single player game and players will need to drag random trash into the corresponding recycling bins. One the game starts from Stage1, images of common household trash that are can be recycled will be generated randomly on the screen. Players have a certain amount of time to use the mouse and drag the trash to the corresponding recycling bin. 

![Alt text](imgs/login.png?raw=true "Login Page")

To start the game, you will have to create an account. There is a basic level of authentication checks for this project.  

![Alt text](imgs/login.png?raw=true "Game Play")

The 4 main recycling categories are Metal, Plastic, Paperand Glass. Dragging the trash into the correct recycling bin will earn points while dragging to the wrong bin will have point penalty.There are a total of 6 stages.

![Alt text](imgs/minimum_score.png?raw=true "Game Play")

 To progress to the next stage, you will need to earn minimum pointsof(5, 12, 21, 32, 45, 60)from stage 1 to 6.As the stage progress, the items will appear more often and disappear quicker. This helps to train the players’ judgement of the item’s recycling category.

![Alt text](imgs/high_score.png?raw=true "Game Play")

**Sign up and compete with your friends!**




# **IMPORTANT**
-Ensure that imgs and sound folders are in the same directory as the .py file before you run the code.

From the terminal:
	Type "python3 sortthetrash.py" to run the program.
From the idle:
	Open the file sortthetrash.py and click run.

-Tested the code on Windows, Macos and Linux Python 3.10.8.