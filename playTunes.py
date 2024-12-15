import os
import tkinter as tk
import tkinter.font as tkFont
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
import pygame
import json

# Initialize pygame.mixer
pygame.mixer.init()
# Initialize the video system
pygame.display.init()

# COLORS
white = "#ffffff"
purple = "#410245"
dg = "#aba8a8"
lavender = "#b2e3f8"
black = "#000000"
red = "#8e0913"
yellow = "#faed08"
blue = "#050c62"
gray = "#828182"
lime = "#46fd2f"
green = "#15ff00"
dkgreen = "#1f8c09"
dkbtn = "#828182"
dkgray = "#333333"

#########
# Globals
##########
playlist = []
current_song_index = -1
CATCHPHRASE = "\n \"That\'s no way to treat an\n expensive musical instrument!\"\n"
LOGO_TEXT = "\n Kaos Tunes, by Kaotickj \n"


# Functions
def play_music(event=None):
    global current_song_index
    selected = listbox.curselection()
    if not selected:
        messagebox.showinfo("No song chosen", "Oops! You need to choose a song to play first.\n\nHint: Open a music "
                                              "file or load a playlist from the \"file\" menu to get started, "
                                              "then choose a song in the playlist before clicking play")
        return  # No item is selected, exit the function

    current_song_index = selected[0]

    running = playlist[current_song_index]
    running_song['text'] = running
    pygame.mixer.music.load(running)
    pygame.mixer.music.play()

    # Bind the 'music_end' event to the next_song function
    pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
    root.after(1000, check_music_end)


# Function to handle the end of a song
def handle_song_end():
    next_music()


# Update the check_music_end function
def check_music_end():
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT + 1:
            handle_song_end()
    root.after(1000, check_music_end)


def pause_music():
    pygame.mixer.music.pause()


def continue_music():
    pygame.mixer.music.unpause()


def stop_music():
    global current_song_index
    prev_song_index = current_song_index - 1  # Get the index of the previously playing song

    pygame.mixer.music.stop()
    listbox.select_clear(0, END)

    # Reset the current song index to the previously playing song index
    if prev_song_index >= 0:
        current_song_index = prev_song_index

    listbox.select_set(current_song_index)
    listbox.activate(current_song_index)
    running_song['text'] = listbox.get(current_song_index)


def next_music():
    global current_song_index
    current_song_index += 1
    print("Current song index:", current_song_index)
    print("Number of songs:", len(playlist))
    if current_song_index >= len(playlist):
        current_song_index = 0

    playing = playlist[current_song_index]
    pygame.mixer.music.load(playing)
    pygame.mixer.music.play()

    listbox.select_clear(0, END)
    listbox.select_set(current_song_index)
    listbox.activate(current_song_index)
    running_song['text'] = playing


def previous_music():
    global current_song_index

    if current_song_index is None:
        return

    current_song_index -= 1
    if current_song_index < 0:
        current_song_index = len(playlist) - 1

    if current_song_index >= len(playlist):
        return

    playing = playlist[current_song_index]
    pygame.mixer.music.load(playing)
    pygame.mixer.music.play()

    listbox.select_clear(0, END)
    listbox.select_set(current_song_index)
    listbox.activate(current_song_index)
    running_song['text'] = playing


def remove_song():
    global current_song_index

    selected = listbox.curselection()
    if not selected:
        return  # No item is selected, exit the function

    index = selected[0]
    listbox.delete(index)
    playlist.pop(index)

    if index < current_song_index:
        current_song_index -= 1  # Decrement the current song index if the removed song is before it
    elif index == current_song_index:
        stop_music()  # Stop the music if the removed song is the current song

    if current_song_index >= 0:
        listbox.select_set(current_song_index)
        listbox.activate(current_song_index)
        running_song['text'] = listbox.get(current_song_index)


def load_file():
    filetypes = (
        ("MP3 files", "*.mp3"),
        ("WAV files", "*.wav"),
        ("FLAC files", "*.flac"),
        ("OGG files", "*.ogg"),
        ("All files", "*.*")
    )
    filepath = filedialog.askopenfilename(
        title="Select Music File",
        filetypes=filetypes
    )
    valid_extensions = (".mp3", ".wav", ".flac", ".ogg")
    if filepath and os.path.isfile(filepath) and filepath.endswith(valid_extensions):
        #listbox.delete(0, END)  # Clear the current playlist
        #playlist.clear()  # Clear the playlist list
        listbox.insert(END, filepath)
        playlist.append(filepath)


def load_playlist():
    global playlist

    filepath = filedialog.askopenfilename(initialdir="playlists/", title="Select Playlist",
                                          filetypes=(("Playlist files", "*.json"), ("All files", "*.*")))

    if filepath:
        with open(filepath, "r") as file:
            playlist_data = json.load(file)
            loaded_playlist = playlist_data.get("playlist", [])

        listbox.delete(0, END)  # Clear the current playlist
        playlist.clear()  # Clear the playlist list

        for item in loaded_playlist:
            listbox.insert(END, item)
            playlist.append(item)

        # Set the first song in the playlist as the current song
        current_song_index = 0
        running_song['text'] = "Pick a tune from the Playlist"


def save_playlist():
    filetypes = [("Playlist files", "*.json")]
    directory = os.path.join(os.getcwd(), "../playlists")
    if not os.path.exists(directory):
        os.makedirs(directory)
    root.withdraw()  # Hide the main window temporarily
    filepath = filedialog.asksaveasfilename(
        initialdir=directory,
        title="Save Playlist",
        filetypes=filetypes,
        defaultextension=".json"
    )
    root.deiconify()  # Show the main window again

    if filepath:
        playlist = listbox.get(0, END)
        playlist_data = {"playlist": playlist}

        with open(filepath, "w") as file:
            json.dump(playlist_data, file)

        messagebox.showinfo("Playlist saved",
                            "Playlist was saved successfully.")


def clear_playlist():
    listbox.delete(0, END)
    messagebox.showinfo("Playlist cleared.",
                        "Playlist has been cleared."
                        )


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        self.id = None
        self.x = self.y = 0

    def showtip(self):
        "Display the tooltip"
        self.tip = tk.Toplevel(self.widget)
        self.tip.attributes('-topmost', True)
        self.tip.overrideredirect(True)
        self.tip.withdraw()
        label = tk.Label(self.tip, text=self.text, justify=tk.LEFT,
                         bg=dkgray, fg=white, relief=tk.SOLID, borderwidth=1,
                         font=("Arial", "11", "normal"))
        label.pack(ipadx=1)
        self.tip.update_idletasks()
        self.tipwidth = self.tip.winfo_reqwidth()
        self.tipheight = self.tip.winfo_reqheight()
        self.x = self.widget.winfo_rootx() + self.widget.winfo_width()
        self.y = self.widget.winfo_rooty() + self.widget.winfo_height()
        self.tip.geometry("+{}+{}".format(self.x, self.y))
        self.tip.deiconify()

    def hidetip(self):
        "Hide the tooltip"
        if self.tip:
            self.tip.withdraw()
            self.tip.destroy()
            self.tip = None


def create_tooltip(widget, text):
    tip = ToolTip(widget, text)

    def enter(event):
        tip.showtip()

    def leave(event):
        tip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


def close_app():
    if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
        root.destroy()


def about_kaos():
    messagebox.showinfo(
        "About Kaos Tunes",
        "Kaos Tunes is a simple music player application.\n"
        "Version: 1.0\n"
        "Developed by: KaotickJ\n"
        "Website: www.github.com/kaotickj"
    )


def show():
    listbox.delete(0, END)  # Clear the current contents of the listbox

    for i, song in enumerate(playlist):
        listbox.insert(END, song)

    if playlist:
        global current_song_index
        current_song_index = 0 if len(playlist) > 0 else -1  # Update current_song_index based on the loaded playlist


def shuffle():
    pass


def loop():
    pass


root = Tk()
root.title(" KaoS Tunes 🎸")
# setting window size
width = 700
height = 500
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
root.geometry(alignstr)
root.resizable(width=False, height=False)
root.configure(bg=black)
root.resizable(width=FALSE, height=FALSE)

# Load the image for the window icon
icon_image = Image.open("assets/play.png")
icon_photo = ImageTk.PhotoImage(icon_image)

# Set the window icon
root.iconphoto(True, icon_photo)

playlist_frame = tk.Frame(root)
playlist_frame["bg"] = dkgray
playlist_frame.place(x=20, y=30, width=309, height=339)

artwork_frame = tk.Label(root)
artwork_frame["bg"] = blue
artwork_frame.place(x=330, y=30, width=349, height=339)

controls_frame = tk.Frame(root)
controls_frame["bg"] = black
controls_frame.place(x=20, y=370, width=660, height=126)

# ***** SETUP IMAGES *****
# now playing
img_nowplaying = Image.open('assets/logo.png')
img_nowplaying = img_nowplaying.resize((280, 280))
img_nowplaying = ImageTk.PhotoImage(img_nowplaying)
np_image = tk.Label(artwork_frame, height=280, image=img_nowplaying, bg=black, padx=10)
np_image.place(x=30, y=20)

# remove from playlist
img_playlist_del = Image.open('assets/del-from-list-wht.png')
img_playlist_del = img_playlist_del.resize((20, 20))
img_playlist_del = ImageTk.PhotoImage(img_playlist_del)

# previous
img_back = Image.open('assets/back.png')
img_back = img_back.resize((40, 40))
img_back = ImageTk.PhotoImage(img_back)

# play
img_play = Image.open('assets/play.png')
img_play = img_play.resize((40, 40))
img_play = ImageTk.PhotoImage(img_play)

# pause
img_pause = Image.open('assets/pause.png')
img_pause = img_pause.resize((40, 40))
img_pause = ImageTk.PhotoImage(img_pause)

# resume
img_resume = Image.open('assets/resume.png')
img_resume = img_resume.resize((40, 40))
img_resume = ImageTk.PhotoImage(img_resume)

# stop
img_stop = Image.open('assets/stop.png')
img_stop = img_stop.resize((40, 40))
img_stop = ImageTk.PhotoImage(img_stop)

# next
img_forward = Image.open('assets/skip.png')
img_forward = img_forward.resize((40, 40))
img_forward = ImageTk.PhotoImage(img_forward)

'''
# The Llama's Head
img_llamas_head = Image.open('assets/koz-logo.png')
img_llamas_head = img_llamas_head.resize((80, 80))
img_llamas_head = ImageTk.PhotoImage(img_llamas_head)
'''

# The Llama's Ass
img_llamas_ass = Image.open('assets/koz-logo.png')
img_llamas_ass = img_llamas_ass.resize((80, 80))
img_llamas_ass = ImageTk.PhotoImage(img_llamas_ass)

# Currently playing song label
running_song = tk.Label(controls_frame)
running_song["bg"] = dkgray
ft = tkFont.Font(family='Arial', size=11)
running_song["font"] = ft
running_song["borderwidth"] = "1px"
running_song["fg"] = green
running_song["anchor"] = W
running_song["text"] = " Load a song or playlist to listen"
running_song["relief"] = "sunken"
running_song.place(x=0, y=0, width=661, height=32)

# **** SETUP BUTTONS *****
# Remove from playlist button
remove_button = tk.Button(root)
remove_button["bg"] = black #"#e9e9ed"
remove_button["justify"] = "center"
remove_button["image"] = img_playlist_del
remove_button.place(x=650, y=372, width=30, height=30)
create_tooltip(remove_button,
               "Delete the highlighted playlist entry from the queue")
remove_button["command"] = remove_song

# Previous button
back_button = tk.Button(root)
back_button["bg"] = dkbtn
back_button["fg"] = black
back_button["justify"] = "center"
back_button["image"] = img_back
back_button.place(x=170, y=420, width=60, height=60)
back_button["command"] = previous_music

# play button
play_button = tk.Button(root)
play_button["bg"] = dkbtn
play_button["fg"] = black
play_button["justify"] = "center"
play_button["image"] = img_play
play_button.place(x=230, y=420, width=60, height=60)
play_button["command"] = play_music

# Pause button
pause_button = tk.Button(root)
pause_button["bg"] = dkbtn
pause_button["fg"] = black
pause_button["justify"] = "center"
pause_button["image"] = img_pause
pause_button.place(x=290, y=420, width=60, height=60)
pause_button["command"] = pause_music

# Resume button
resume_button = tk.Button(root)
resume_button["bg"] = dkbtn
resume_button["fg"] = black
resume_button["justify"] = "center"
resume_button["image"] = img_resume
resume_button.place(x=350, y=420, width=60, height=60)
resume_button["command"] = continue_music

# stop button
stop_button = tk.Button(root)
stop_button["bg"] = dkbtn
stop_button["fg"] = black
stop_button["justify"] = "center"
stop_button["image"] = img_stop
stop_button.place(x=410, y=420, width=60, height=60)
stop_button["command"] = pause_music

# skip/forward button
skip_button = tk.Button(root)
skip_button["bg"] = dkbtn
skip_button["fg"] = black
skip_button["justify"] = "center"
skip_button["image"] = img_forward
skip_button.place(x=470, y=420, width=60, height=60)
skip_button["command"] = next_music

listbox = tk.Listbox(playlist_frame)
listbox["borderwidth"] = "1px"
listbox["relief"] = "sunken"
ft = tkFont.Font(family='Arial', size=12)
listbox["font"] = ft
listbox["bg"] = dkgray
listbox["fg"] = green
listbox["justify"] = "left"
listbox.place(x=0, y=0, width=308, height=339)
def_txt = "  Please load a file/playlist"
a = []
playlist.append(a)
playlist.append(def_txt)

w = Scrollbar(playlist_frame, orient="vertical", command=listbox.yview)
w.grid(row=0, column=1, sticky=NSEW)

listbox.config(yscrollcommand=w.set)
w.pack(side="right", fill="y")

# create the llama's ass
llamas_head = tk.Label(root)
llamas_head["bg"] = "#000000"
llamas_head["fg"] = dkgray
llamas_head["justify"] = "center"
llamas_head["image"] = img_llamas_ass
llamas_head.place(x=40, y=405)
create_tooltip(llamas_head,
               LOGO_TEXT)

# create the llama's ass
llamas_ass = tk.Label(root)
llamas_ass["bg"] = "#000000"
llamas_ass["fg"] = dkgray
llamas_ass["justify"] = "center"
llamas_ass["image"] = img_llamas_ass
llamas_ass.place(x=570, y=410, width=70, height=70)
create_tooltip(llamas_ass,
               CATCHPHRASE)

'''
shuffle = tk.Checkbutton(root)
ft = tkFont.Font(family='Arial', size=10)
shuffle["font"] = ft
shuffle["bg"] = black
shuffle["fg"] = dkgreen
shuffle["justify"] = "center"
shuffle["text"] = "Shuffle"
shuffle.place(x=280, y=405, width=80, height=15)
shuffle["command"] = shuffle

loop = tk.Checkbutton(root)
ft = tkFont.Font(family='Arial', size=10)
loop["font"] = ft
loop["bg"] = black
loop["fg"] = dkgreen
loop["justify"] = "center"
loop["text"] = "Loop"
loop.place(x=350, y=405, width=70, height=15)
loop["command"] = loop
'''

# Create the menubar
menubar = tk.Menu(root)
root.config(menu=menubar)

# Create the file menu
file_menu = tk.Menu(menubar, tearoff=0, bg=black, fg=yellow)
menubar.add_cascade(label="File", menu=file_menu)

# Add file menu options
file_menu.add_command(label="Load Music", command=load_file)
file_menu.add_separator()
file_menu.add_command(label="Load Playlist", command=load_playlist)
file_menu.add_command(label="Save Playlist", command=save_playlist)
file_menu.add_command(label="Clear Playlist", command=clear_playlist)
file_menu.add_separator()
file_menu.add_command(label="Close", command=close_app)

# Create the help menu
help_menu = tk.Menu(menubar, tearoff=0, bg=black, fg=yellow)
menubar.add_cascade(label="Help", menu=help_menu)

# Add help menu options
help_menu.add_command(label="About Kaos Tunes", command=about_kaos)

os.chdir(r'music')
songs = os.listdir()

music_state = StringVar()
music_state.set("Choose one!")
show()

if __name__ == "__main__":
    root.mainloop()
