from tkinter import *
from PIL import Image, ImageDraw
import preprocessing
import model
import torch

prediction = None
last_x = None
last_y = None
live_mode = False
prediction_job = None

def display() :
    
    # Create a window
    window = Tk()

    window.title("Number Recognition")
    window.geometry("1280x720")
    window.minsize(1280,720)
    window.config(bg = "#FFFFFF")

    # Frames 
    top_frame = Frame(window, bg = "#FFFFFF")
    drawing_frame = Frame(window, bg = "#FFFFFF")
    prediction_frame = Frame(window, bg = "#FFFFFF")

    # Subframes 
    drawing_square = Canvas(drawing_frame, height = 280, width = 280, highlightthickness = 2, bg = "#000000")
    prediction_buttons_frame = Frame(drawing_frame, bg = "#FFFFFF")

    pil_image = Image.new("L", (280, 280), 0)
    pil_draw = ImageDraw.Draw(pil_image)

    # Labels and inputs 
    instructions_label = Label(top_frame, text = "Draw a number !", font = ("Helvetica", 30), bg = "#FFFFFF", fg = "black") 
    prediction_label = Label(prediction_frame, text = f"You draw a : {prediction}", font = ("Helvetica", 30), bg = "#FFFFFF", fg = "black")

    def clear_canvas() : 
        global last_x, last_y
        drawing_square.delete("all")
        last_x, last_y = None, None
        pil_draw.rectangle((0, 0, 280, 280), fill=0)
        prediction_label.config(text="You draw a : ")

    def start_drawing(event) : 
        global last_x, last_y
        last_x = event.x
        last_y = event.y

    def drawing(event) : 
        global last_x, last_y
        if last_x is not None and last_y is not None :
            drawing_square.create_line(last_x, last_y, event.x, event.y, width = 15, smooth = True, capstyle = ROUND, joinstyle = ROUND, fill = "white")
            pil_draw.line((last_x, last_y, event.x, event.y), fill=255, width=15)
        last_x = event.x
        last_y = event.y
        if live_mode:
            live_prediction()

    def get_drawing():
        image = pil_image
        image.save("number.png")
        return image
        
    def predict_number():
        image = get_drawing()
        tensor = preprocessing.preprocess(image)

        if tensor is None:
            prediction_label.config(text="You draw a : Nothing")
        else:
            with torch.no_grad():
                outputs = model.model(tensor)
                prediction = torch.max(outputs, 1)[1].item()
            prediction_label.config(text=f"You draw a : {prediction}")
            if not live_mode:
                window.after(1500, clear_canvas) # Exécute clear_canvas après 1500 ms

    def switch_mode() :
        global live_mode
        live_mode = not live_mode
        if live_mode : 
            live_mode_button.config(text = "LIVE MODE : ON")
        else : 
            live_mode_button.config(text = "LIVE MODE : OFF")

    def live_prediction() : 
        global prediction_job

        if prediction_job is not None:
            window.after_cancel(prediction_job)

        prediction_job = window.after(20, predict_number)

    drawing_square.bind("<Button-1>", start_drawing)
    drawing_square.bind("<B1-Motion>", drawing)

    # Buttons
    prediction_button = Button(prediction_buttons_frame, text = "PREDICTION", font = ("Helvetica", 30), command = lambda : predict_number(), width = 12)
    clear_button = Button(prediction_buttons_frame, text = "CLEAR", font = ("Helvetica", 30), command = lambda : clear_canvas(), width = 12)
    live_mode_button = Button(prediction_buttons_frame, text = "LIVE MODE : OFF", font = ("Helvetica", 30), command = lambda : switch_mode(), width = 20)

    # Display labels
    instructions_label.grid(row = 0, column = 0, pady = (30,5))
    prediction_button.grid(row = 0, columnspan = 2, pady = (30,5))
    clear_button.grid(row = 1, column = 0, pady = (30,5))
    live_mode_button.grid(row = 2, column = 0, pady = (30,5))
    prediction_label.grid(row = 0, column = 0, pady = (30,5))

    # Display frames
    top_frame.pack()
    drawing_frame.pack()
    prediction_frame.pack()

    drawing_square.pack()
    prediction_buttons_frame.pack()

    # Display window
    window.mainloop()
