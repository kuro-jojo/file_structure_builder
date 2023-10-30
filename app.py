"""File structure generator ": a GUI to generate a file structure more easily"""

import tkinter as tk
from customtkinter import filedialog
import customtkinter as ctk
import pyautogui

WINDOW_WIDTH = pyautogui.size().width - 300

WINDOW_HEIGHT = pyautogui.size().height - 300

# Frame 1
#   - folder where to create the structure
#   - button to generate the structure


class DirectorySelectorFrame(ctk.CTkFrame):
    """A frame containing a button to select a directory and a text entry to display the path"""

    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

        self.path = ctk.CTkEntry(self, placeholder_text="C:/Users/Me/Desktop")
        self.path.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        select_strucutre_location_button = ctk.CTkButton(
            self, text="Select location", fg_color="grey", command=self.show_file_dialog
        )
        select_strucutre_location_button.grid(
            row=0, column=1, padx=10, pady=10, sticky="w"
        )

    def show_file_dialog(self):
        """Show the file dialog to select a directory and display the path in the entry"""

        filename = filedialog.askdirectory()
        if filename:
            # Read and print the content (in bytes) of the file.
            self.path.delete(0, "end")
            self.path.insert(0, filename)
            print(filename)
        else:
            print("No file selected.")


class GeneratorFrame(ctk.CTkFrame):
    """A frame containing a button to generate the structure and the path where to create it"""

    def __init__(self, master):
        super().__init__(master, fg_color="white", bg_color="white")
        self.grid_columnconfigure(0, weight=1)

        directory_selector_frame = DirectorySelectorFrame(self)
        directory_selector_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        generator_button = ctk.CTkButton(
            self, text="Generate", command=lambda: print("Hello World!")
        )
        generator_button.grid(row=0, column=1, padx=10, pady=10, sticky="w")


# Frame 2 : below frame 1
# - the canva where to draw  the structure
# - where to display the generated structure


class StructureDisplayFrame(ctk.CTkFrame):
    """A frame containing a canvas to display the structure"""

    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.structure_canvas = StructureCanvas(self)
        self.structure_canvas.configure(
            width=WINDOW_WIDTH // 2, height=WINDOW_HEIGHT * (3 / 4)
        )
        self.structure_canvas.grid(row=0, column=0, padx=10, pady=10, sticky="ewns")

        self.add_element_frame = AddElementFrame(self, self.structure_canvas)
        self.add_element_frame.grid(row=0, column=1, padx=10, pady=10, sticky="")


class StructureCanvas(ctk.CTkCanvas):
    """A canvas to draw the structure by placing folders and files"""

    def __init__(self, master):
        super().__init__(master)


# Frame 3 : aside frame 2
# 3 image butttons  to add a folder, a file, a link


class AddElementFrame(ctk.CTkFrame):
    """A frame containing 3 buttons to add a folder, a file, a link"""

    def __init__(self, master, canvas: StructureCanvas):
        super().__init__(master)
        self.canvas = canvas

        self.folder_image = tk.PhotoImage(file="assets/folder.png")
        # folders and links from that folder
        self.folders = {}

        self.file_image = tk.PhotoImage(file="assets/file.png")
        # file and links from that file
        self.files = {}

        self.selected_item = None

        # 3 buttons to add a folder, a file, a link
        self.add_folder_button = ctk.CTkButton(
            self, text="Add folder", width=80, height=100, command=self.add_folder
        )
        self.add_folder_button.grid(row=0, column=0, padx=10, pady=10, sticky="ewns")

        self.add_file_button = ctk.CTkButton(
            self, text="Add file", width=80, height=100, command=self.add_file
        )
        self.add_file_button.grid(row=1, column=0, padx=10, pady=10, sticky="ewns")

    def add_folder(self):
        """Add a folder to the canvas"""
        x, y = 100, 100  # Default initial position
        folder_tag = self.canvas.create_image(x, y, image=self.folder_image)
        self.folders[folder_tag] = {}
        self.config_binging(folder_tag)
        self.canvas.tag_bind(folder_tag, "<B1-Motion>", self.move_item)

    def add_file(self):
        """Add a file to the canvas"""
        x, y = 100, 100  # Default initial position
        file_tag = self.canvas.create_image(x, y, image=self.file_image)
        self.files[file_tag] = {}
        self.config_binging(file_tag)
        self.canvas.tag_bind(file_tag, "<B1-Motion>", self.move_item)

    def config_binging(self, tag):
        # add create link between selected item and the previous one
        self.start_x = None
        self.start_y = None
        self.line = None

        # releash the arrow
        # when in a certain scope of another item (folder, file, link)
        # create a link between the two items

        self.canvas.tag_bind(
            tag,
            "<ButtonPress-1>",
            lambda event, tag=tag: self.select_item(event, tag),
        )
        self.canvas.tag_bind(tag, "<Button-3>", self.start_drawing_arrow)
        self.canvas.tag_bind(tag, "<B3-Motion>", self.draw_arrow)
        self.canvas.tag_bind(tag, "<ButtonRelease-3>", self.end_drawing_arrow)

    def select_item(self, event, tag: int):
        print("seleting item", self.selected_item)
        if not self.selected_item:
            self.selected_item = tag
            self.selected_item_bp = tag
            self.selected_item_outline = self.canvas.create_rectangle(
                self.canvas.bbox(self.selected_item),
                outline="red",
                width=3,
                tags="border_image",
            )

        else:
            # desect the item
            self.canvas.delete(self.selected_item_outline)
            self.selected_item = None

    def start_drawing_arrow(self, event):
        # TODO: arrow origin is the center of the image  
        if self.selected_item:
            self.start_x = event.x
            self.start_y = event.y
            self.line = self.canvas.create_line(
                self.start_x,
                self.start_y,
                self.start_x,
                self.start_y,
                fill="black",
                arrow="last",
                width=5,
            )
        # attach the created arrow to the selected item

    def draw_arrow(self, event, tag=None):
        new_x, new_y = self.set_arrow_boundaries(event)
        if tag:
            if self.selected_item in self.folders:
                print(self.folders[self.selected_item])
                if len(self.folders[self.selected_item][tag]) == 2:
                    origin_x = self.folders[self.selected_item][tag][0]
                    origin_y = self.folders[self.selected_item][tag][1]
            elif self.selected_item in self.files:
                if len(self.files[self.selected_item][tag]) == 2:
                    origin_x = self.files[self.selected_item][tag][0]
                    origin_y = self.files[self.selected_item][tag][1]
            self.canvas.coords(self.line, origin_x, origin_y, new_x, new_y)

        elif self.start_x and self.start_y and self.line:
            self.canvas.coords(self.line, self.start_x, self.start_y, new_x, new_y)

    def end_drawing_arrow(self, event, tag=None):
        if self.selected_item and self.line:
            self.attach_arrow_to_item(self.line, self.start_x, self.start_y)

            # drag the arrow after it was created
            self.canvas.tag_bind(
                self.line,
                "<B1-Motion>",
                lambda event, tag=self.line: self.draw_arrow(event, tag),
            )
            self.canvas.tag_bind(
                self.line,
                "<ButtonRelease-1>",
                lambda event, tag=self.line: self.end_drawing_arrow(event, tag),
            )
        print(self.folders)

    def move_item(self, event):
        self.canvas.delete(self.selected_item_outline)
        if self.selected_item:
            image = self.get_selected_image()
            if image:
                new_x, new_y = self.set_images_boundaries(event, image)
                self.canvas.coords(self.selected_item, new_x, new_y)
                self.selected_item_outline = self.canvas.create_rectangle(
                    self.canvas.bbox(self.selected_item),
                    outline="red",
                    width=3,
                    tags="border_image",
                )
                new_x, new_y = self.set_arrow_boundaries(event)
                if self.selected_item in self.folders:
                    arrows = self.folders[self.selected_item]
                    for arrow in arrows:
                        self.canvas.coords(
                            arrow,
                            new_x,
                            new_y,
                            arrows[arrow][0],
                            arrows[arrow][1],
                        )
                elif self.selected_item in self.files:
                    arrows = self.files[self.selected_item]
                    for arrow in arrows:
                        self.canvas.coords(
                            arrow,
                            new_x,
                            new_y,
                            arrows[arrow][0],
                            arrows[arrow][1],
                        )

    def get_selected_image(self):
        if self.selected_item in self.folders:
            return self.folder_image
        elif self.selected_item in self.files:
            return self.file_image
        return None

    def attach_arrow_to_item(self, arrow, origin_x, origin_y):
        if self.selected_item in self.folders:
            self.folders[self.selected_item][arrow] = [origin_x, origin_y]
        elif self.selected_item in self.files:
            self.files[self.selected_item][arrow] = [origin_x, origin_y]

    def set_arrow_boundaries(self, event):
        new_x = event.x
        new_y = event.y

        if new_x >= self.canvas.winfo_width():
            new_x = self.canvas.winfo_width()
        elif new_x <= 0:
            new_x = 0
        if new_y >= self.canvas.winfo_height():
            new_y = self.canvas.winfo_height()
        elif new_y <= 0:
            new_y = 0

        return new_x, new_y

    def set_images_boundaries(self, event, image):
        new_x = event.x
        new_y = event.y

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_width = image.width()
        image_height = image.height()

        if new_x < image_width / 2:
            new_x = image_width / 2
        elif new_x > canvas_width - image_width / 2:
            new_x = canvas_width - image_width / 2

        if new_y < image_height / 2:
            new_y = image_height / 2
        elif new_y > canvas_height - image_height / 2:
            new_y = canvas_height - image_height / 2

        return new_x, new_y


class App(ctk.CTk):
    """The main app"""

    def __init__(self):
        super().__init__()

        self.title("Build your file structure")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 9 / 10)
        # self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)

        self.generator_frame = GeneratorFrame(self)
        self.generator_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.structure_display_frame = StructureDisplayFrame(self)
        self.structure_display_frame.grid(
            row=1, column=0, padx=10, pady=10, sticky="ew"
        )


if __name__ == "__main__":
    app = App()

    app.mainloop()
