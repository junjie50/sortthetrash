import tkinter as tk
import os
import random
from libdw import pyrebase
import tkinter.messagebox
import hashlib

#Only support in game sound for windows
from sys import platform
if platform == "win32":
    import winsound

#-------------------------------UTILITY----------------------------------#
class Utility():
    """Class to provide utility function for the application such as joining the file paths and password hashing."""
    def join_class_path(*args):
        """Joining class path regardless of operating system.

        Args:
            (path1, path2, path3...)

        Returns:
            path1/path2/path3 (Unix)
            path1\path2\path3 (Windows)
        """
        res = ""
        for arg in args:
            res += arg + os.sep
        return res[:-1]
    
    def password_hash(password):
        """To hash the password for safe storage in database.

        Args:
            password: length > 0
        
        Returns:
            The hashed value from hashing the password.

        """
        return hashlib.sha3_256(password.encode('utf-8')).hexdigest()
    
    def alert(text):
        """Alert function for the application.
        
        Args:
            text: Message to be shown to the user.
        """
        tkinter.messagebox.showinfo(message=text)

#-------------------------------UTILITY----------------------------------#

#-------------------------------DATABASE---------------------------------#
class DataBase():
    """Class to provide data management for the application.
    The class manages the connection to the Firebase using libdw module."""
    def __init__(self):
        dburl = "xxx"
        email = "xxx"
        password = "xxx" 
        apikey = "xxx"
        authdomain = dburl.replace("https://","")

        config = {
            "apiKey": apikey,
            "authDomain": authdomain,
            "databaseURL": dburl,
        }

        firebase = pyrebase.initialize_app(config)
        auth = firebase.auth()
        user = auth.sign_in_with_email_and_password(email, password)
        self._db = firebase.database()
        self._user = auth.refresh(user['refreshToken'])
    
    def get_high_score(self):
        """The function returns the high score retrieved from the database."""
        return self._db.child("Score").get(self._user['idToken']).val()

    def update_high_score(self, score):
        """The function to update the high score in the database.
        
        Args:
            score: The score to be used to update the database.
        """
        self._db.child("Score").set(str(score), self._user['idToken'])

    def update_record_holder(self, user):
        """The function to update the record holder in the database.
        
        Args:
            user: The username of the player who achieved the new high score.
        """
        self._db.child("Number1").set(str(user), self._user['idToken'])
    
    def get_record_holder(self):
        """The function returns the record holder username retrieved from the database."""
        return self._db.child("Number1").get(self._user['idToken']).val()

    def get_key(self, key):
        """Returns the value associated with key from the databse.

        Args:
            key: the identifier in the database.

        Returns:
            Value of key in database and None if key is not in the database.
        """
        return self._db.child(key).get(self._user['idToken']).val()

    def set_key(self, key, data):
        """Set the value of key to be data in the database.

        Args:
            key: The key of the data.
            data: The value associated with key.
        """
        self._db.child(key).set(data, self._user['idToken'])
    
    def get_pictures():
        """ The function returns the picture locations of the different recycling category.

        Returns:
            item_picture: Location of item pictures locally.
            bin_pictures: Location of bin pictures locally.
        """
        item_pictures = {
            "Paper": ["paper_newspaper.png", "paper_notebook.png", "paper_crumple.png","paper_box.png"],
            "Metal": ["metal_coke.png", "metal_biscuit_tin.png", "metal_container.png", "metal_pan.png", "metal_tin.png"],
            "Plastic": ["plastic_bottle.png", "plastic_bag.png", "plastic_containers.png", "plastic_container.png"],
            "Glass": ["glass_bottle2.png", "glass_beer_bottles.png", "glass_medicine_bottles.png"]
        }
        bin_pictures = {
            "Paper": "Paper.png",
            "Metal": "Metal.png",
            "Plastic": "Plastic.png",
            "Glass": "Glass.png"
        }

        for key in item_pictures:
            bin_pictures[key] = "imgs" + os.sep + bin_pictures[key]
            for i in range(len(item_pictures[key])):
                item_pictures[key][i] = Utility.join_class_path("imgs", item_pictures[key][i])

        return item_pictures, bin_pictures
    
    def get_minimum_score():
        """The function returns a list the minimum score required to advance for each stage. Starting
        from stage 1 and maximum 10.

        Returns:
            [score1, score2...]
        """
        minimum_score = []
        curr = 0
        addition = 5
        for i in range(10):
            minimum_score.append(curr + addition)
            curr += addition
            addition += 2
        return minimum_score

#The locations of the different pictures locally.
recycling_pictures, recycling_bin_pictures = DataBase.get_pictures()
#Creating minimum advance points for each stage.
minimum_score = DataBase.get_minimum_score()

#Game constants.
window_width = 800
window_height = 600
bin_height = 100
bin_width = window_width / 4
start_item_interval = 3000
start_item_duration = 4000
start_game_duration = 30000
back_ground_color = '#d9d9d9'
button_menu_color = '#568203'
label_sky_color = '#829cd9'
start_stage = 1
end_stage = 6
start_score = 0
recycling_types = ["Paper", "Metal", "Plastic", "Glass"]
#-------------------------------DATABASE---------------------------------#


#-------------------------------CONTROL----------------------------------#
class GameControl():
    """Class to manage the data of the current game and interaction with data base.
    """
    def __init__(self):
        self._db = DataBase()
        self.reset()
        self._bins = recycling_types
        self._user = None
    
    def reset(self):
        """Reset the game data for a new game play."""
        self._stage = start_stage
        self._item_interval = start_item_interval
        self._item_duration = start_item_duration
        self._game_duration = start_game_duration
        self._score = start_score
        self._time = int(start_game_duration/1000)
        self._high_score = int(self._db.get_high_score())
    
    def increase_stage(self):
        """Increase the difficulty after each stage. 
        Item will appear faster after every stage and disappear quicker."""
        self._item_interval = int(self._item_interval * 0.80)
        self._item_duration = int(self._item_duration  * 0.90)
        self._stage += 1
    
    def get_stage(self):
        """Returns the current stage of the game."""
        return self._stage
    
    def get_game_duration(self):
        """Returns the gmae duration of the current game."""
        return self._game_duration

    def get_item_interval(self):
        """Returns the item interval of the current game."""
        return self._item_interval

    def get_item_duration(self):
        """Returns the item duration of the current game."""
        return self._item_duration

    def get_score(self):
        """Returns the score of the current game."""
        return self._score
    
    def increase_score(self, incre = 1):
        """Increase the score of the current game by 1 (default).
        
        args:
            increment: Default value is 1
        """
        self._score += incre
        self._score = max(0, self._score)
    
    def get_high_score(self):
        """Returns the high_score retried from the database API.
        """
        return self._db.get_high_score()
    
    def get_record_holder(self):
        """Returns the record_holder retried from the database API.
        """
        return self._db.get_record_holder()


    def get_min_score(self):
        """Returns the minimum score required to advance to the next stage of the game..
        """
        return minimum_score[self._stage - 1]
    
    def able_to_advance(self):
        """Check if the player is able to advance to the next stage.
        """
        return self._score >= minimum_score[self._stage - 1]

    def final_page(self):
        """Check if the player is at the final stage of the game.
        """
        return self._stage == end_stage

    def get_time(self):
        """Return the game time of the game.
        """
        return self._time
    
    def update_high_score(self):
        """Updates the high score of the game. Records the high score and the username to the database.
        """
        if self._score > int(self._db.get_high_score()):
            self._db.update_high_score(self._score)
            self._db.update_record_holder(self._user)

    def authenticate(self, username, password):
        """Authenticates the login details of the user. Stores the detail of user upon successful login.

        Args:
            username, password

        Returns:
        True if username and password are valid else False
        """
        #Length check
        if len(username) == 0 or len(password) == 0:
            return False
        
        #Existence check
        res = self._db.get_key(username)
        if res == None:
            return False
        
        #Password check
        if Utility.password_hash(password) != res:
            return False
        self._user = username
        return True

    def get_key(self, key):
        """
        Returns the value associated with key. None is returned if key is not in database.
        """
        return self._db.get_key(key)
    
    def create_user(self, username, password):
        """ Create the user in the database.

        Args:
            username, password
        """
        pass_hash = Utility.password_hash(password)
        self._db.set_key(username, pass_hash)
    
    def get_curr_user(self):
        """ Return the curr user that is playing the game.
        """
        return self._user
        
#-------------------------------CONTROL----------------------------------#

#--------------------------------VIEW------------------------------------#
class GameView(tk.Tk):
    """The GamePlay Class manages the view and interaction of users by 
    interacting with the GameModel class
    """
    game_font = lambda self, x: ("Helvetica", x, "bold")

    def __init__(self, game):
        super().__init__()
        self.title("SortTheTrash")
        self.resizable(False, False)
        self.geometry("{}x{}".format(window_width, window_height))
        p1 = tk.PhotoImage(file=Utility.join_class_path('imgs','app_logo.png'))
        self.iconphoto(True, p1)
        self.configure(bg=back_ground_color)
        self._game = game
        self._prev_category = None
        self._play_music = True
        self._main_menu = self.login_page()
    
    def register_page(self):
        """Provides the display for users to register their account.
        """
        def register(username, password1, password2):
            #Direct user to login page after account has been created.
            if password1.get() != password2.get():
                Utility.alert("Password must match each other.")
            elif len(username.get()) < 3:
                Utility.alert("Length of username must be more or equal to 3.")
            elif len(password1.get()) < 3:
                Utility.alert("Length of password must be more or equal to 3.")
            elif self._game.get_key(username.get()) != None:
                Utility.alert("Username already exists, please choose another username.")
            else:
                self._game.create_user(username.get(), password1.get())
                self.login_page()

        #Background image 
        background_img = tk.PhotoImage(file=Utility.join_class_path('imgs','evergreen_back.png'))
        bg_label = tk.Label(image=background_img)
        bg_label.image=background_img
        bg_label.configure(image=background_img)
        bg_label.place(relx=0.5,rely=0.5,anchor='center')

        username_label = tk.Label(text=f"Username", font=self.game_font(20),bg=button_menu_color)
        username_label.place(relx=0.5,rely=0.40, anchor="center")
        username = tk.Entry(width = 15, bg=back_ground_color)
        username.place(relx=0.5,rely=0.45, anchor="center")
        password1_label = tk.Label(text=f"Password", font=self.game_font(20),bg=button_menu_color)
        password1_label.place(relx=0.5,rely=0.5, anchor="center")
        password1 = tk.Entry( show="*", width=15, bg=back_ground_color)
        password1.place(relx=0.5,rely=0.55, anchor="center")
        password2 = tk.Entry( show="*", width=15, bg=back_ground_color)
        password2.place(relx=0.5,rely=0.6, anchor="center")
        register_button = tk.Button(text="register", command=lambda:register(username, password1, password2))
        register_button.place(relx=0.5,rely=0.65, anchor="center")
        exit_button = tk.Button(text="Exit", command=self.login_page)
        exit_button.place(relx=0.5, rely=0.7, anchor='center')
        self.create_setting_button(label_sky_color)

    def login_page(self):
        """Provides the login display for the user."""
        def login_helper(username, password):
            if self._game.authenticate(username.get(), password.get()):
                self.create_main_menu()
            else:
                tkinter.messagebox.showinfo(message="Password or username is wrong. Please try again.")

        #Background image for menu
        background_img = tk.PhotoImage(file=Utility.join_class_path('imgs','evergreen_back.png'))
        bg_label = tk.Label(image=background_img)
        bg_label.image=background_img
        bg_label.configure(image=background_img)
        bg_label.place(relx=0.5,rely=0.5,anchor='center')

        username_label = tk.Label(text=f"Username", font=self.game_font(20),bg=button_menu_color)
        username_label.place(relx=0.5,rely=0.40, anchor="center")
        username = tk.Entry(width = 15, bg=back_ground_color)
        username.place(relx=0.5,rely=0.45, anchor="center")
        password_label = tk.Label(text=f"Password", font=self.game_font(20),bg=button_menu_color)
        password_label.place(relx=0.5,rely=0.5, anchor="center")
        password = tk.Entry( show="*", width=15, bg=back_ground_color)
        password.place(relx=0.5,rely=0.55, anchor="center")
        login_button = tk.Button(text="login", command=lambda:login_helper(username, password))
        login_button.place(relx=0.5,rely=0.60, anchor="center")
        register_button = tk.Button(text="register", command=self.register_page)
        register_button.place(relx=0.5,rely=0.65, anchor="center")
        self.create_setting_button(label_sky_color)
    
    # Game Music only works on windows.
    def play_sound(self):
        """Plays the background music. Only works for windows as winsound is used."""
        self._play_music = True
        if self._play_music and platform == "win32":
            winsound.PlaySound(Utility.join_class_path('sound',"acoustic1d.wav"), 
            winsound.SND_FILENAME | winsound.SND_ASYNC)

    # Game Music only works on windows.
    def stop_sound(self):
        """Stops the background music. Only works on windows as winsound is used."""
        self._play_music = False
        if platform == "win32":
            winsound.PlaySound(None, winsound.SND_ASYNC)
            
    def create_setting_button(self, colour, filename="setting_button.png"):
        """Creates the setting button for the application on the top right hand corner."""
        def button_toggle(button):
            sound1 = tk.Button(text="Play Music", command=self.play_sound, highlightbackground=colour, bg=colour,
                highlightthickness=2, width=5)
            sound1.place(relx=0.95, rely=0.13, anchor='center')
            stop_btn = tk.Button(text="Stop Music", command=self.stop_sound, highlightbackground=colour, bg=colour,
                highlightthickness=2, width=5)
            stop_btn.place(relx=0.95, rely=0.18, anchor='center')
            exit_button = tk.Button(text="QUIT", width=5,
                    font=self.game_font(10), command=self.create_main_menu, highlightbackground=colour, bg=colour)
            exit_button.place(relx = 0.95, rely = 0.23, anchor = 'center')
            button.configure(command=lambda:button_toggle_off(button, sound1, stop_btn, exit_button))

        def button_toggle_off(button, *args):
            for item in args:
                item.destroy()
            button.configure(command=lambda:button_toggle(button))

        setting_img = tk.PhotoImage(file=Utility.join_class_path('imgs', filename))
        button = tk.Button(highlightthickness = 2, command=lambda:button_toggle(button))
        button.image = setting_img
        button.configure(image=setting_img)
        button.config(highlightbackground=colour)
        button.place(relx=0.95, rely=0.05, anchor="center")

    def create_main_menu(self):
        """Main menu display of the game."""

        #If user is not logged in, direct to the login page.
        if self._game.get_curr_user() == None:
            self.login_page()
            return
        width = 10
        paddingy = 15
        corner_radius = 5
        self.clear_frame()

        #Reset the current game data
        self._game.reset()

        #Background image for menu
        background_img = tk.PhotoImage(file=Utility.join_class_path('imgs','evergreen_back.png'))
        bg_label = tk.Label(image=background_img)
        bg_label.image=background_img
        bg_label.configure(image=background_img)
        bg_label.place(relx=0.5,rely=0.5,anchor='center')

        new_game_button = tk.Button(text="New Game", width=width,
                font=self.game_font(20), pady=paddingy, command=self.start_game, highlightbackground=button_menu_color, bg=button_menu_color)
        new_game_button.place(relx = 0.5, rely = 0.46, anchor = 'center')
        help_button = tk.Button(text="Help", width=width,
                font=self.game_font(20), pady=paddingy, command=self.help_page, highlightbackground=button_menu_color, bg=button_menu_color)
        help_button.place(relx = 0.5, rely = 0.59, anchor = 'center')
        billboard_btn = tk.Button(text="Billboard", width=width, pady=paddingy,
                font=self.game_font(20), command=self.billboard, highlightbackground=button_menu_color, bg=button_menu_color)
        billboard_btn.place(relx = 0.5, rely = 0.72, anchor = 'center')
        exit_button = tk.Button(text="Exit", width=width,
                font=self.game_font(20), pady=paddingy, command=quit, highlightbackground=button_menu_color, bg=button_menu_color)
        exit_button.place(relx=0.5, rely=0.85, anchor='center')
        self.create_setting_button(label_sky_color)


    def help_page(self):
        """Help display to provide instructions for the game."""
        width = 10
        paddingy = 15
        self.clear_frame()

        #Background image for menu
        background_img = tk.PhotoImage(file=Utility.join_class_path('imgs','evergreen_back_help.png'))
        bg_label = tk.Label(image=background_img)
        bg_label.image=background_img
        bg_label.configure(image=background_img)
        bg_label.place(relx=0.5,rely=0.5,anchor='center')

        exit_button = tk.Button(text="Return", width=width,
                font=self.game_font(20), pady=paddingy, command=self.create_main_menu, highlightbackground=button_menu_color, bg=button_menu_color)
        exit_button.place(relx = 0.5, rely = 0.90, anchor = 'center')
        self.create_setting_button(label_sky_color)
    
    def billboard(self):
        """Provides the leaderboard dispaly for the game."""
        width = 10
        paddingy = 20
        self.clear_frame()

        #Background image for menu
        background_img = tk.PhotoImage(file=Utility.join_class_path('imgs','evergreen_back.png'))
        bg_label = tk.Label(image=background_img)
        bg_label.image=background_img
        bg_label.configure(image=background_img)
        bg_label.place(relx=0.5,rely=0.5,anchor='center')

        stage = tk.Label(text=f"BILLBOARD", font=self.game_font(40), bg=label_sky_color)
        stage.place(relx = 0.5, rely = 0.05, anchor = 'center')
        message = tk.Label(text=f"HIGH SCORE:  {self._game.get_high_score()}", font=self.game_font(20))
        message.place(relx = 0.5, rely = 0.5, anchor = 'center')
        message = tk.Label(text=f"USER:  {self._game.get_record_holder()}", font=self.game_font(20))
        message.place(relx = 0.5, rely = 0.6, anchor = 'center')
        main_button = tk.Button(text="MAIN MENU", width=10,
                font=self.game_font(10), pady=20, command=self.create_main_menu,bg=button_menu_color, highlightbackground=button_menu_color)
        main_button.place(relx = 0.5, rely = 0.7, anchor = 'center')
        self.create_setting_button(label_sky_color)

    def start_game(self):
        """Starting the next stage. Clears the current frame and create a new frame for the next game."""
        self.clear_frame()
        self.create_game_play()

    def clear_frame(self):
        """Reset tkinter display and music. Used before every change of display."""
        for widget in self.winfo_children():
            widget.destroy()
        if self._play_music:
            self.play_sound()
    
    def enter_bin(self, event):
        """UI for bin. Upon mouse entering bin, change the background colour of the bin."""
        event.widget.config(bg="#E8E8E8")
    
    def leave_bin(self, event):
        """UI for bin. Upon mouse leaving bin, change the background colour of the bin."""
        event.widget.config(bg=back_ground_color)
  
    def countdown(self,time, time_left):
        """Function to decrease the timer. Once time is up, direct player to staging area."""
        if time > 0:
            time_left.configure(text=f"TIME LEFT : {time} ")
            self._score.after(1000, self.countdown, time - 1, time_left)
        else:
            self.staging_area()
            
    def create_game_play(self):
        """Creates the game graphics and user interaction."""
        #Background image for menu
        background_img = tk.PhotoImage(file=Utility.join_class_path('imgs','in_game_background.png'))
        bg_label = tk.Label(image=background_img)
        bg_label.image=background_img
        bg_label.configure(image=background_img)
        bg_label.place(relx=0.5,rely=0.5,anchor='center')

        #Labels
        stage = tk.Label(text=f"STAGE {self._game.get_stage()}/{end_stage}", font=self.game_font(40),bg=back_ground_color)
        stage.place(relx = 0.5, rely = 0.05, anchor = 'center')
        self._score = tk.Label(text=f"SCORE {self._game.get_score()}", font=self.game_font(20),bg=back_ground_color)
        self._score.place(relx = 0.5, rely = 0.15, anchor = 'center')
        high_score = self._game.get_high_score()
        self._high_score = tk.Label(text=f"HIGH SCORE: {high_score}", font=self.game_font(10), bg=back_ground_color)
        self._high_score.place(relx = 0.1, rely = 0.05, anchor = 'center')

        #Create 4 bins at the bottom
        x = 0
        width = int(window_width / 4)
        height = int(0.2 * window_height)
        self._bins = []
        for key, data in recycling_bin_pictures.items():
            img = tk.PhotoImage(file=recycling_bin_pictures[key]).subsample(3)
            bin = tk.Label(width=width, height=height, bg=back_ground_color)
            bin.image = img
            bin.configure(image=img)
            bin.bind("<Enter>", self.enter_bin)
            bin.bind("<Leave>", self.leave_bin)
            bin.place(relx=x, rely = 0.8)
            x += 0.25
            self._bins.append(bin)
        self.generate_random_item()

        # timer
        time = self._game.get_time()
        time_left = tk.Label(font=self.game_font(20), bg=back_ground_color)
        time_left.place(relx=0.5, rely=0.2, anchor="center")
        self.countdown(time, time_left)

        #Setting
        self.create_setting_button(back_ground_color, "setting_button_game.png")
    
    
    def fail_area(self):
        """Creates the graphics in the event that a player fails to advance to the next stage."""
        width = 10
        paddingy = 20
        self.clear_frame()
        #Background image for menu
        background_img = tk.PhotoImage(file=Utility.join_class_path('imgs','evergreen_back.png'))
        bg_label = tk.Label(image=background_img)
        bg_label.image=background_img
        bg_label.configure(image=background_img)
        bg_label.place(relx=0.5,rely=0.5,anchor='center')

        high_score = self._game.get_high_score()
        stage = tk.Label(text=f"STAGE {self._game.get_stage()}", font=self.game_font(40), bg=label_sky_color)
        stage.place(relx = 0.5, rely = 0.05, anchor = 'center')
        self._score = tk.Label(text=f"SCORE {self._game.get_score()}", font=self.game_font(20),bg=label_sky_color)
        self._score.place(relx = 0.5, rely = 0.15, anchor = 'center')
        high_score = tk.Label(text=f"HIGH SCORE: {high_score}", font=self.game_font(10), bg=label_sky_color)
        high_score.place(relx = 0.1, rely = 0.05, anchor = 'center')
        message = tk.Label(text=f"Unable to advance to next stage",
                    font=self.game_font(20), bg=back_ground_color)
        message.place(relx = 0.5, rely = 0.5, anchor = 'center')
        message2 = tk.Label(text=f" Minimum score required is {self._game.get_min_score()}", 
                    font=self.game_font(20), bg=back_ground_color)
        message2.place(relx = 0.5, rely = 0.57, anchor = 'center')
        main_button = tk.Button(text="Main Menu", width=10,
                font=self.game_font(10), pady=20, command=self.create_main_menu, highlightbackground=button_menu_color, bg=button_menu_color)
        main_button.place(relx = 0.5, rely = 0.7, anchor = 'center')

        self.create_setting_button(label_sky_color)

    def result_page(self):
        """Result page of the game after completing all the stages."""
        width = 10
        paddingy = 20
        self.clear_frame()
        #Background image for menu
        background_img = tk.PhotoImage(file=Utility.join_class_path('imgs','evergreen_back.png'))
        bg_label = tk.Label(image=background_img)
        bg_label.image=background_img
        bg_label.configure(image=background_img)
        bg_label.place(relx=0.5,rely=0.5,anchor='center')

        high_score = self._game.get_high_score()
        stage = tk.Label(text=f"RESULT", font=self.game_font(40), bg=label_sky_color)
        stage.place(relx = 0.5, rely = 0.05, anchor = 'center')
        self._score = tk.Label(text=f"SCORE {self._game.get_score()}", font=self.game_font(20), bg=label_sky_color)
        self._score.place(relx = 0.5, rely = 0.15, anchor = 'center')
        high_score = tk.Label(text=f"HIGH SCORE: {high_score}", font=self.game_font(10), bg=label_sky_color)
        high_score.place(relx = 0.1, rely = 0.05, anchor = 'center')
        message = tk.Label(text=f"Congrats! Your Final score is {self._game.get_score()}", font=self.game_font(20))
        message.place(relx = 0.5, rely = 0.5, anchor = 'center')
        main_button = tk.Button(text="MAIN MENU", width=10,
                font=self.game_font(10), pady=20, command=self.create_main_menu,highlightbackground=button_menu_color, bg=button_menu_color)
        main_button.place(relx = 0.5, rely = 0.6, anchor = 'center')
        self.create_setting_button(label_sky_color)

        #Record the score of user
        self._game.update_high_score()

    def staging_area(self):
        """
        Area used to stage players after completing a stage.
        Players will be directed to fail stage and result stage
        accordingly.
        """
        if not self._game.able_to_advance():
            self.fail_area()
            return
        if self._game.final_page(): 
            self.result_page()
            return
        
        width = 10
        paddingy = 20
        self.clear_frame()

        #Background image for menu
        background_img = tk.PhotoImage(file=Utility.join_class_path('imgs','evergreen_back.png'))
        bg_label = tk.Label(image=background_img)
        bg_label.image=background_img
        bg_label.configure(image=background_img)
        bg_label.place(relx=0.5,rely=0.5,anchor='center')

        high_score = self._game.get_high_score()
        self._score = tk.Label(text=f"SCORE {self._game.get_score()}", font=self.game_font(20), bg=label_sky_color)
        self._score.place(relx = 0.5, rely = 0.05, anchor = 'center')
        high_score = tk.Label(text=f"HIGH SCORE: {high_score}", font=self.game_font(10), bg=label_sky_color)
        high_score.place(relx = 0.1, rely = 0.05, anchor = 'center')
        stage_number = tk.Label(text=f"Stage {self._game.get_stage()}", font=self.game_font(40), bg=back_ground_color)
        stage_number.place(relx = 0.5, rely = 0.5, anchor = 'center')
        continue_game_button = tk.Button(text="CONTINUE", width=width, 
                font=self.game_font(20), pady=paddingy, command=self.start_game, bg=button_menu_color, highlightbackground=button_menu_color)
        continue_game_button.place(relx = 0.5, rely = 0.65, anchor = 'center')
        quit_button = tk.Button(text="QUIT", width=width,
                font=self.game_font(20), pady=paddingy, command=self.create_main_menu, bg=button_menu_color, highlightbackground=button_menu_color)
        quit_button.place(relx = 0.5, rely = 0.78, anchor = 'center')
        self._game.increase_stage()

        self.create_setting_button(label_sky_color)

    def on_drop(self, event, category):
        """Function to update the score after dropping the item at the bin."""
        widget = event.widget
        if widget.winfo_y() >= 0.7*window_height:
            drop_bin_type = recycling_types[widget.winfo_x() // 200]
            if category == drop_bin_type:
                self._game.increase_score(1)
            else:
                self._game.increase_score(-1)
            self._score.configure(text=f"SCORE {self._game.get_score()}")
            widget.destroy()

    def on_drag_start(self, event):
        """Helps to animate the drag motion."""
        widget = event.widget
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y

    def drag(self, event):
        """Helps to animate the drag motion."""
        widget = event.widget
        x = widget.winfo_x() - widget._drag_start_x + event.x
        y = widget.winfo_y() - widget._drag_start_y + event.y
        x = max(0, min(x, 650))
        y = max(140, min(y, 450))
        widget.place(x=x, y=y)
        #background bin
        for bin in self._bins:
            bin.config(bg=back_ground_color)
        if widget.winfo_y() >= 0.7*window_height:
            self._bins[widget.winfo_x() // 200].config(bg="#E8E8E8")
    
    def generate_random_item(self):
        """Function to generate random items around the map."""

        length = 70
        category = random.choice(recycling_types)
        while category == self._prev_category:
            category = random.choice(recycling_types)
        self._prev_category = category
        click_btn = tk.PhotoImage(file=random.choice(recycling_pictures[category]))
        button = tk.Button(highlightthickness = 0, bd = 0)
        button.image = click_btn
        button.configure(image=click_btn)
        button.config(bg=back_ground_color)
        button.place(x=int(random.uniform(0.05, 0.8) * window_width), y=int(random.uniform(0.2, 0.55)*window_height))
        button.bind("<Button-1>", self.on_drag_start)
        button.bind("<B1-Motion>", self.drag)
        button.bind("<ButtonRelease-1>", lambda event: self.on_drop(event, category))
        button.after(self._game.get_item_duration(), button.destroy)
        tk.Label().after(self._game.get_item_interval(), self.generate_random_item)
    
#--------------------------------VIEW------------------------------------#

#--------------------------------START-----------------------------------#
if __name__ == "__main__":
    window = GameView(GameControl())
    window.mainloop()
#---------------------------------END------------------------------------#