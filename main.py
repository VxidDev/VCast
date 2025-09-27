import customtkinter as ctk
import functions

window = ctk.CTk()
window.title("Veather")
window.geometry("350x500")
window.resizable(width=False , height=False)
window.configure(fg_color=("white" , "black"))

search_frame = ctk.CTkFrame(window , width=350 , height=500 , fg_color=("white" , "black"))
search_frame.place(relx=0 , rely=0 , relwidth=1 , relheight=1)

results_frame = ctk.CTkFrame(window , width=350 , height=500 , fg_color=("white" , "black"))
results_frame.place(relx=0 , rely=0 , relwidth=1 , relheight=1)

for frame in (search_frame , results_frame):
    frame.place(relx=0 , rely=0 , relwidth=1 , relheight=1)

functions.show_frame(search_frame)

try:
    if functions.config["theme"] == "Light":
        ctk.set_appearance_mode("Light")
        theme_icon = "☾"
    else:
        ctk.set_appearance_mode("Dark")
        theme_icon = "☀︎"
except KeyError:
    functions.gen_config()

# SEARCH FRAME
city = ctk.StringVar()

logo = ctk.CTkLabel(search_frame , text="Veather - Search" , font=("arial" , 40 , "bold"))
logo.place(x=20 , y=60)

theme_button = ctk.CTkButton(search_frame , fg_color=("#ffffff" , "#000000") , text_color=("#000000" , "#ffffff"), hover_color=("#ffffff" , "#000000") , text=theme_icon , width=65 , height=65 , font=("arial" , 30 , "bold") , command=lambda: functions.change_theme(ctk.get_appearance_mode() , theme_button))
theme_button.place(x=285 , y=0)

search_button = ctk.CTkButton(search_frame , text="🔍" , width=65 , height=65 , font=("arial" , 30 , "bold") , command=lambda: functions.fetch_data(window , results_frame , search_frame , city.get()))
search_button.place(x=240 , y=130)

city_entry = ctk.CTkEntry(search_frame  , width=195 , height=65 , font=("Arial" , 30 , 'bold') , textvariable=city)
city_entry.place(x=45 , y=130)

window.bind("<Return>" , lambda e: functions.fetch_data(window , results_frame , search_frame , city.get() , e))
window.bind("<Control-t>" , lambda e: functions.change_theme(ctk.get_appearance_mode() , theme_button , e))

window.mainloop()
