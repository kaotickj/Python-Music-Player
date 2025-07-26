import os
import sys
import tkinter as tk
import tkinter.font as tkFont
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
import pygame
import json
import random
import threading
from mutagen import File
from mutagen.id3 import ID3NoHeaderError
from mutagen.mp3 import MP3
import io



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
LOGO_TEXT = "\n Kaos Tunes, by Kaotick Jay \n"
loop_enabled = False
metadata_title_label = None
metadata_artist_label = None
metadata_album_label = None
current_art_image = None 
play_thread = None


# Functions
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def show_default_artwork():
    global current_art_image
    img_nowplaying = Image.open(resource_path('assets/logo.png'))
    img_nowplaying = img_nowplaying.resize((250, 250), Image.LANCZOS)
    current_art_image = ImageTk.PhotoImage(img_nowplaying)
    np_image.config(image=current_art_image)

def get_song_metadata(audio_path):
    """
    Extract title, artist, and album from audio metadata.
    Returns a tuple (title, artist, album and year). Missing fields return empty string.
    """
    title = ""
    artist = ""
    album = ""
    year = ""

    try:
        audio = File(audio_path)
        if audio is None or audio.tags is None:
            return (title, artist, album, year)

        tags = audio.tags

        # Title
        if 'TIT2' in tags:
            title = str(tags['TIT2'].text[0])

        # Artist
        if 'TPE1' in tags:
            artist = str(tags['TPE1'].text[0])

        # Album
        if 'TALB' in tags:
            album = str(tags['TALB'].text[0])

        # Year (prefer TDRC)
        if 'TDRC' in tags:
            year = str(tags['TDRC'].text[0])
        elif 'TYER' in tags:  # fallback
            year = str(tags['TYER'].text[0])

    except Exception as e:
        print(f"[!] Error reading metadata from {audio_path}: {e}")

    return (title, artist, album, year)
def extract_embedded_artwork(audio_path):
    """
    Extract embedded album art from audio file metadata using mutagen.
    Returns a PIL Image object or None if not found.
    """

    try:
        audio = File(audio_path)
        if audio is None:
            return None

        # For MP3 with ID3 tags:
        if hasattr(audio, 'tags') and audio.tags is not None:
            for tag in audio.tags.values():
                if tag.FrameID == 'APIC':  # ID3 album art frame
                    img_data = tag.data
                    image = Image.open(io.BytesIO(img_data))
                    return image

        # For FLAC or other formats:
        if 'metadata_blocks' in dir(audio) and audio.metadata_blocks is not None:
            for block in audio.metadata_blocks:
                if block.__class__.__name__ == 'Picture':
                    img_data = block.data
                    image = Image.open(io.BytesIO(img_data))
                    return image

    except Exception as e:
        print(f"[!] Error extracting embedded artwork: {e}")

    return None

def update_now_playing_artwork_for_song(song_path):
    global img_nowplaying, np_image

    default_art_path = resource_path('assets/logo.png')
    album_dir = os.path.dirname(song_path)

    # Try extracting embedded artwork first
    embedded_image = extract_embedded_artwork(song_path)

    if embedded_image:
        try:
            img_nowplaying = embedded_image.resize((250, 250), Image.LANCZOS)
            img_nowplaying = ImageTk.PhotoImage(img_nowplaying)
            np_image.config(image=img_nowplaying)
            np_image.image = img_nowplaying
            return
        except Exception as e:
            print(f"[!] Failed to use embedded artwork: {e}")

    # Then check for folder.jpg (case insensitive)
    candidate_names = ['folder.jpg', 'Folder.jpg', 'FOLDER.JPG']
    album_art_path = None
    for filename in candidate_names:
        possible_path = os.path.join(album_dir, filename)
        if os.path.isfile(possible_path):
            album_art_path = possible_path
            break

    if album_art_path:
        try:
            img_nowplaying = Image.open(album_art_path)
            img_nowplaying = img_nowplaying.resize((250, 250), Image.LANCZOS)
            img_nowplaying = ImageTk.PhotoImage(img_nowplaying)
            np_image.config(image=img_nowplaying)
            np_image.image = img_nowplaying
            return
        except Exception as e:
            print(f"[!] Failed to load folder.jpg artwork: {e}")

    # Finally fallback to default logo
    try:
        img_nowplaying = Image.open(default_art_path)
        img_nowplaying = img_nowplaying.resize((250, 250), Image.LANCZOS)
        img_nowplaying = ImageTk.PhotoImage(img_nowplaying)
        np_image.config(image=img_nowplaying)
        np_image.image = img_nowplaying
    except Exception as e:
        print(f"[!] Failed to load fallback logo: {e}")

def play_music(event=None):
    global play_thread
    global current_song_index

    if play_thread is None or not play_thread.is_alive():
        play_thread = threading.Thread(target=r, daemon=True)
        play_thread.start()

    selected = listbox.curselection()
    if not selected:
        messagebox.showinfo(
            "No song chosen",
            "Oops! You need to choose a song to play first.\n\nHint: Open a music "
            "file or load a playlist from the \"file\" menu to get started, "
            "then choose a song in the playlist before clicking play"
        )
        return

    index = selected[0]

    if playlist[index] == "Please load a file/playlist":
        messagebox.showinfo(
            "No song chosen",
            "Please load a music file or playlist before playing."
        )
        return

    if index < 0 or index >= len(playlist):
        messagebox.showerror(
            "Invalid selection",
            f"The selected index ({index}) does not match any song in the playlist (size: {len(playlist)})."
        )
        return

    current_song_index = index
    song_path = playlist[current_song_index]

    try:
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()

        # Duration and progress bar setup
        try:
            audio = File(song_path)
            duration = audio.info.length if audio and audio.info else 0
        except Exception:
            duration = 0

        if not duration:
            try:
                sound = pygame.mixer.Sound(song_path)
                duration = sound.get_length()
            except Exception:
                duration = 0

        progress_bar.config(to=duration)
        progress_var.set(0)
        time_label.config(text=f"0:00 / {format_time(duration)}")

        update_progress_bar()

        running_song['text'] = os.path.basename(song_path)

        update_now_playing_artwork_for_song(song_path)

        title, artist, album, year = get_song_metadata(song_path)
        metadata_title_label['text'] = f" {title or 'Unknown'}"
        metadata_artist_label['text'] = f" {artist or 'Unknown'}"
        metadata_album_label['text'] = f" {album or 'Unknown'} ({year})" if year else f"{album or 'Unknown'}"

        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
        root.after(1000, check_music_end)

    except Exception as e:
        messagebox.showerror("Playback Error", f"Failed to play the selected track:\n{str(e)}")

def update_progress_bar():
    if pygame.mixer.music.get_busy():
        pos = pygame.mixer.music.get_pos() / 1000  # milliseconds to seconds
        total = progress_bar.cget("to")
        if pos >= total:
            pos = total
        progress_var.set(pos)
        time_label.config(text=f"{format_time(pos)} / {format_time(total)}")
    root.after(1000, update_progress_bar)


# Function to handle the end of a song
def handle_song_end():
    next_music()



def shuffle():
    global playlist, current_song_index

    if not playlist:
        messagebox.showinfo("Shuffle", "Playlist is empty. Please load songs first.")
        return

    # Shuffle playlist list in-place
    random.shuffle(playlist)

    # Clear the listbox and repopulate with basenames
    listbox.delete(0, END)
    for song_path in playlist:
        listbox.insert(END, os.path.basename(song_path))

    # Set current song index to 0 (first in shuffled list)
    current_song_index = 0
    listbox.select_clear(0, END)             # Clear any previous selection
    listbox.select_set(current_song_index)  # Select first item
    listbox.activate(current_song_index)    # Focus on first item

    # Update label with currently playing song basename
    running_song['text'] = os.path.basename(playlist[current_song_index])

    # Play the first song in the shuffled playlist
    play_music()    

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
#    prev_song_index = current_song_index - 1  # Get the index of the previously playing song

#    pygame.mixer.music.stop()

    if pygame.mixer.music.get_busy():
        # current_song_index = prev_song_index
        pygame.mixer.music.stop()
    pygame.event.clear(pygame.USEREVENT + 1)    
    listbox.select_clear(0, END)

    # listbox.select_set(current_song_index)
    # listbox.activate(current_song_index)
    # running_song['text'] = listbox.get(current_song_index)
    running_song['text'] = "Playback stopped. Choose a song to play."
    metadata_title_label['text'] = ""
    metadata_artist_label['text'] = ""
    metadata_album_label['text'] = ""

def next_music():
    global current_song_index, loop_enabled

    current_song_index += 1
    if current_song_index >= len(playlist):
        if loop_enabled:
            current_song_index = 0
        else:
            stop_music()
            return

    playing = playlist[current_song_index]
    pygame.mixer.music.load(playing)
    pygame.mixer.music.play()

    listbox.select_clear(0, END)
    listbox.select_set(current_song_index)
    listbox.activate(current_song_index)
    running_song['text'] = os.path.basename(playing)

    # Update artwork and metadata
    update_now_playing_artwork_for_song(playing)
    title, artist, album, year = get_song_metadata(playing)
    metadata_title_label['text'] = f" {title or 'Unknown'}"
    metadata_artist_label['text'] = f" {artist or 'Unknown'}"
    metadata_album_label['text'] = f" {album or 'Unknown'} ({year})" if year else f"{album or 'Unknown'}"

    try:
        audio = File(playing)
        duration = audio.info.length if audio and audio.info else 0
    except Exception:
        duration = 0

    if not duration:
        try:
            sound = pygame.mixer.Sound(playing)
            duration = sound.get_length()
        except Exception:
            duration = 0

    progress_bar.config(to=duration)
    progress_var.set(0)
    time_label.config(text=f"0:00 / {format_time(duration)}")

    update_progress_bar()


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
    running_song['text'] = os.path.basename(playing)

    # Update artwork and metadata
    update_now_playing_artwork_for_song(playing)
    title, artist, album, year = get_song_metadata(playing)
    metadata_title_label['text'] = f" {title or 'Unknown'}"
    metadata_artist_label['text'] = f" {artist or 'Unknown'}"
    metadata_album_label['text'] = f" {album or 'Unknown'} ({year})" if year else f"{album or 'Unknown'}"


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
    
    if filepath and os.path.isfile(filepath) and filepath.lower().endswith(valid_extensions):
        # Remove placeholder if it exists
        if playlist and playlist[0] == "Please load a file/playlist":
            playlist.clear()
            listbox.delete(0, END)
        
        playlist.append(filepath)
        listbox.insert(END, os.path.basename(filepath))

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
            playlist.append(item)  # Keep full path for playback
            listbox.insert(END, os.path.basename(item))  # Insert only basename in listbox

        global current_song_index
        current_song_index = 0
        running_song['text'] = "Pick a tune from the Playlist"



def save_playlist():
    filetypes = [("Playlist files", "*.json")]
    directory = os.path.join(os.getcwd(), "playlists")
    if not os.path.exists(directory):
        os.makedirs(directory)

    root.withdraw()  # Temporarily hide the window
    filepath = filedialog.asksaveasfilename(
        initialdir=directory,
        title="Save Playlist",
        filetypes=filetypes,
        defaultextension=".json"
    )
    root.deiconify()  # Restore the window

    if filepath:
        playlist_data = {"playlist": playlist}

        try:
            with open(filepath, "w") as file:
                json.dump(playlist_data, file)

            messagebox.showinfo("Playlist saved", "Playlist was saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save playlist:\n{e}")


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
        "Developed by: Kaotick Jay\n"
        "Website: www.github.com/kaotickj"
    )


def show():
    listbox.delete(0, END)

    if not playlist:
        placeholder = "Please load a file/playlist"
        playlist.append(placeholder)
        listbox.insert(END, placeholder)
        global current_song_index
        current_song_index = -1
        return

    for song in playlist:
        if isinstance(song, str) and os.path.isfile(song):
            listbox.insert(END, os.path.basename(song))
        else:
            listbox.insert(END, str(song))

    current_song_index = 0 if len(playlist) > 0 else -1
    if current_song_index >= 0:
        listbox.select_set(current_song_index)
        listbox.activate(current_song_index)
def toggle_loop():
    global loop_enabled
    loop_enabled = loop_var.get()
    status = "enabled" if loop_enabled else "disabled"
    # Optionally update a status label or just print
    print(f"Loop mode {status}.")
    # messagebox.showinfo("Loop Mode", f"Loop mode {status}.")

def format_time(seconds):
    minutes = int(seconds) // 60
    sec = int(seconds) % 60
    return f"{minutes}:{sec:02d}"

# def loop():
#    pass


root = Tk()
root.title(" KaoS Tunes 🎸")
width = 700
height = 550
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
root.geometry(alignstr)
root.resizable(width=False, height=False)
root.configure(bg=black)
root.resizable(width=FALSE, height=FALSE)

# Set cross-platform compatible icon
icon_path_ico = resource_path("icon.ico")
icon_path_png = resource_path("icon.png")

# Set icon depending on OS
if sys.platform.startswith("win"):
    try:
        root.iconbitmap(icon_path_ico)
    except Exception as e:
        print(f"[!] Could not load .ico icon: {e}")
else:
    try:
        icon_image = Image.open(icon_path_png)
        icon_photo = ImageTk.PhotoImage(icon_image)
        root.iconphoto(True, icon_photo)
    except Exception as e:
        pass


container_width = 280
container_height = 280

image_width = 250
image_height = 250

x_pos = (container_width - image_width) // 2  # 15
y_pos = (container_height - image_height) // 2  # 15

playlist_frame = tk.Frame(root)
playlist_frame["bg"] = dkgray
playlist_frame.place(x=20, y=30, width=309, height=339)

artwork_frame = tk.Label(root)
artwork_frame["bg"] = black
artwork_frame.place(x=330, y=30, width=349, height=339)
# Container inside artwork_frame for album art and metadata
artwork_container = tk.Frame(artwork_frame, bg=black)
artwork_container.place(x=30, y=5, width=280, height=322)

controls_frame = tk.Frame(root)
controls_frame["bg"] = black
controls_frame.place(x=20, y=370, width=660, height=126)

# ***** SETUP IMAGES *****
# now playing
img_nowplaying = Image.open(resource_path('assets/logo.png'))
img_nowplaying = img_nowplaying.resize((250, 250), Image.LANCZOS)
img_nowplaying = ImageTk.PhotoImage(img_nowplaying)
np_image = tk.Label(artwork_container, bg=black)
np_image.place(x=x_pos, y=y_pos, width=image_width, height=image_height)
show_default_artwork()

metadata_title_label = tk.Label(artwork_frame, bg='black', fg=green, font=('Arial', 10, 'bold'), anchor='w')
metadata_title_label.place(x=35, y=271, width=275, height=18)

metadata_artist_label = tk.Label(artwork_frame, bg='black', fg=green, font=('Arial', 10), anchor='w')
metadata_artist_label.place(x=35, y=289, width=275, height=18)

metadata_album_label = tk.Label(artwork_frame, bg='black', fg=green, font=('Arial', 10), anchor='w')
metadata_album_label.place(x=35, y=307, width=275, height=18)

# remove from playlist
img_playlist_del = Image.open(resource_path('assets/del-from-list-wht.png'))
img_playlist_del = img_playlist_del.resize((20, 20))
img_playlist_del = ImageTk.PhotoImage(img_playlist_del)

# previous
img_back = Image.open(resource_path('assets/back.png'))
img_back = img_back.resize((40, 40))
img_back = ImageTk.PhotoImage(img_back)

# play
img_play = Image.open(resource_path('assets/play.png'))
img_play = img_play.resize((40, 40))
img_play = ImageTk.PhotoImage(img_play)

# pause
img_pause = Image.open(resource_path('assets/pause.png'))
img_pause = img_pause.resize((40, 40))
img_pause = ImageTk.PhotoImage(img_pause)

# resume
img_resume = Image.open(resource_path('assets/resume.png'))
img_resume = img_resume.resize((40, 40))
img_resume = ImageTk.PhotoImage(img_resume)

# stop
img_stop = Image.open(resource_path('assets/stop.png'))
img_stop = img_stop.resize((40, 40))
img_stop = ImageTk.PhotoImage(img_stop)

# next
img_forward = Image.open(resource_path('assets/skip.png'))
img_forward = img_forward.resize((40, 40))
img_forward = ImageTk.PhotoImage(img_forward)

'''
# The Llama's Head
img_llamas_head = Image.open('assets/koz-logo.png')
img_llamas_head = img_llamas_head.resize((90, 90))
img_llamas_head = ImageTk.PhotoImage(img_llamas_head)
'''

# The Llama's Ass
img_llamas_ass = Image.open(resource_path('assets/koz-logo.png'))
img_llamas_ass = img_llamas_ass.resize((90, 90))
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

# Progress bar and duration
progress_var = tk.DoubleVar()
progress_bar = tk.Scale(controls_frame, variable=progress_var, from_=0, to=100, orient=HORIZONTAL,
                        showvalue=False, length=400, sliderlength=10, troughcolor=dkgray,
                        fg=green, bg=black, highlightthickness=0)
progress_bar.place(x=130, y=35)

time_label = tk.Label(controls_frame, text="0:00 / 0:00", bg=black, fg=green, font=('Arial', 9))
time_label.place(x=540, y=35)


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
back_button.place(x=170, y=430, width=60, height=60)
back_button["command"] = previous_music

# play button
play_button = tk.Button(root)
play_button["bg"] = dkbtn
play_button["fg"] = black
play_button["justify"] = "center"
play_button["image"] = img_play
play_button.place(x=230, y=430, width=60, height=60)
play_button["command"] = play_music

# Pause button
pause_button = tk.Button(root)
pause_button["bg"] = dkbtn
pause_button["fg"] = black
pause_button["justify"] = "center"
pause_button["image"] = img_pause
pause_button.place(x=290, y=430, width=60, height=60)
pause_button["command"] = pause_music

# Resume button
resume_button = tk.Button(root)
resume_button["bg"] = dkbtn
resume_button["fg"] = black
resume_button["justify"] = "center"
resume_button["image"] = img_resume
resume_button.place(x=350, y=430, width=60, height=60)
resume_button["command"] = continue_music

# stop button
stop_button = tk.Button(root)
stop_button["bg"] = dkbtn
stop_button["fg"] = black
stop_button["justify"] = "center"
stop_button["image"] = img_stop
stop_button.place(x=410, y=430, width=60, height=60)
stop_button["command"] = stop_music

# skip/forward button
skip_button = tk.Button(root)
skip_button["bg"] = dkbtn
skip_button["fg"] = black
skip_button["justify"] = "center"
skip_button["image"] = img_forward
skip_button.place(x=470, y=430, width=60, height=60)
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

w = Scrollbar(playlist_frame, orient="vertical", command=listbox.yview)
w.grid(row=0, column=1, sticky=NSEW)

listbox.config(yscrollcommand=w.set)
w.pack(side="right", fill="y")

# create the llama's head
llamas_head = tk.Label(root)
llamas_head["bg"] = "#000000"
llamas_head["fg"] = dkgray
llamas_head["justify"] = "center"
llamas_head["image"] = img_llamas_ass
llamas_head.place(x=40, y=415)
create_tooltip(llamas_head,
               LOGO_TEXT)

# create the llama's ass
llamas_ass = tk.Label(root)
llamas_ass["bg"] = "#000000"
llamas_ass["fg"] = dkgray
llamas_ass["justify"] = "center"
llamas_ass["image"] = img_llamas_ass
llamas_ass.place(x=570, y=425, width=70, height=70)
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
'''
loop_var = tk.BooleanVar(value=False)

loop_checkbox = tk.Checkbutton(root, text="Loop", bg=black, fg=dkgreen,
                               font=('Arial', 10), relief=tk.RAISED, borderwidth=2, variable=loop_var,
                               command=toggle_loop)
loop_checkbox["bg"] = black #"#e9e9ed"
loop_checkbox["justify"] = "center"
loop_checkbox.place(x=580, y=371, width=70, height=30)
create_tooltip(loop_checkbox,
               "Loop the current playlist")

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
file_menu.add_command(label="Shuffle Playlist", command=shuffle)
file_menu.add_separator()
file_menu.add_command(label="Close", command=close_app)

# Create the help menu
help_menu = tk.Menu(menubar, tearoff=0, bg=black, fg=yellow)
menubar.add_cascade(label="Help", menu=help_menu)

# Add help menu options
help_menu.add_command(label="About Kaos Tunes", command=about_kaos)


music_state = StringVar()
music_state.set("Choose one!")

if __name__ == "__main__":
    show()
    root.mainloop()
