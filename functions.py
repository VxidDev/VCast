import customtkinter as ctk
import pathlib , json , requests , datetime , os , zoneinfo
from tkinter import messagebox
from PIL import Image

base_config = {
    "theme": "light"
}

path = pathlib.Path(__file__).resolve().parent

def gen_config():
    global config
    with open(f"{path}/config.json" , "w") as file:
        json.dump(base_config , file)

def get_config_data():
    try:
        with open(f"{path}/config.json" , "r") as file:
            config = json.load(file)

        return config
    except (FileNotFoundError , json.JSONDecodeError):
        gen_config()

def update_config(config):
    try:
        with open(f"{path}/config.json" , "w") as file:
            json.dump(config , file)
    except FileNotFoundError:
        gen_config()

config = get_config_data()

def read_cache(path , city , id=None):
    os.makedirs(path , exist_ok=True)
    if id is not None:
        path = f"{path}{city.lower().replace(" ", "_").replace("'", "").replace("-", "_")}-{id}.json"
    else:
        path = f"{path}{city.lower().replace(" ", "_").replace("'", "").replace("-", "_")}.json"
    try:
        with open(path , "r") as file:
            output = json.load(file)
        if output.get("date" , datetime.datetime.today().strftime("%D")) != datetime.datetime.today().strftime("%D"):
            return None
        return output
    except (FileNotFoundError , json.JSONDecodeError):
        return None

def write_cache(path , city , data , id=None):
    os.makedirs(path , exist_ok=True)
    if id is not None:
        path = f"{path}{city.lower().replace(" ", "_").replace("'", "").replace("-", "_")}-{id}.json"
    else:
        path = f"{path}{city.lower().replace(" ", "_").replace("'", "").replace("-", "_")}.json"
    with open(path , "w") as file:
        json.dump(data , file)

def show_frame(frame):
    frame.lift()

def show_results(frame , geocode_data , city):
    show_frame(frame)
    
    if not hasattr(frame , "scrollable"):
        scrollable = ctk.CTkScrollableFrame(frame , fg_color=("white" , "black"))
        frame.scrollable = scrollable
        scrollable.pack(fill="both" , expand="true")
        scrollable.bind("<Button-4>" , lambda event , f=scrollable: scrollable._parent_canvas.yview("scroll" , -3 , "units"))
        scrollable.bind("<Button-5>" , lambda event , f=scrollable: scrollable._parent_canvas.yview("scroll" , 3 , "units"))
    else:
        for button in frame.scrollable.winfo_children():
            button.destroy()

    frames = {}
    buttons = []
    
    buttons.append(ctk.CTkButton(frame.scrollable , text="⬅️" , font=("arial" , 30 , "bold") , width=50 , height=50 , command=lambda f=frame: f.lower()))

    for i in range(len(geocode_data["results"])):
        geo_name = geocode_data["results"][i]["name"]

        frames[f"{geo_name}-{i}"] = ctk.CTkFrame(frame , width=350 , height=700 , fg_color=("white" , "black"))
        
        button_name = f"{geocode_data['results'][i]['name']} , {geocode_data['results'][i].get('admin1' , "Unknown")} , {geocode_data['results'][i].get("country" , "unknown")}"

        if len(button_name) > 43:
            button_name = button_name[:40] + "..."
        buttons.append(ctk.CTkButton(frame.scrollable , text=button_name , width=150 , height=75 , font=("arial" , 15 , "bold") , command=lambda frame=frames[f"{geo_name}-{i}"] , id=i: get_city_weather(geocode_data , id , frame , city)))

    for frame in frames.values():
        frame.place(relx=0 , rely=0 , relheight=1 , relwidth=1)
        
        for i in range(0 , len(buttons)):
            buttons[i].grid(column=0 , row=i , pady=15 , sticky="w")
        
        frame.lower()

def organize_data(frame , weather_data , geocode_data , id):
    show_frame(frame)
    
    city = geocode_data["results"][id]["name"]
    if len(city) >= 22:
        city = city[:19] + "..."

    if not hasattr(frame , "exit_button"):
        frame.exit_button = ctk.CTkButton(frame , text="⬅️" , font=("arial" , 30 , "bold"),width=50 , height=50, command=lambda: frame.lower())
        frame.exit_button.place(x=5 , y=5)
    else:
        frame.exit_button.lift()

    if not hasattr(frame , "city_name"):
        frame.city_name = ctk.CTkLabel(frame , text=city , font=("arial" , 30 , "bold"))
        frame.city_name.place(x=5 , y=55)
    else:
        frame.city_name.configure(text=city)
        frame.city_name.lift()
    
    timezone = zoneinfo.ZoneInfo(geocode_data["results"][id].get("timezone" , "UTC"))
    time = datetime.datetime.now(timezone)
    rain_amount = weather_data["hourly"]["rain"][int(time.strftime("%H"))] + weather_data["hourly"]["showers"][int(time.strftime("%H"))]
    temperature = weather_data["hourly"]["temperature_2m"][int(time.strftime("%H"))]
    wind_speed = weather_data["hourly"]["wind_speed_10m"][int(time.strftime("%H"))]
    humidity = weather_data["hourly"]["relative_humidity_2m"][int(time.strftime("%H"))]
    cloud_coverage = weather_data["hourly"]["cloud_cover"][int(time.strftime("%H"))]
    
    if rain_amount <= 0:
        if cloud_coverage <= 0:
            weather_icon = "clear"
            weather_label = "Clear"
        else:
            if 0 < cloud_coverage <= 25:
                weather_icon = "cloudy-1"
                weather_label = "Mostly clear"
                label_pos = (75 , 305)
            elif 25 < cloud_coverage <= 75:
                weather_icon = "cloudy-2"
                weather_label = "Cloudy"
                label_pos = (115 , 305)
            else:
                weather_icon = "cloudy-3"
                weather_label = "Overcast"
                label_pos = (85 , 305)

    elif 0 < rain_amount <= 2.5:
        weather_icon = "rainy-1"
        weather_label = "Light rain"
        label_pos = (90 , 305)
    elif 2.5 < rain_amount <= 15:
        weather_icon = "rainy-2"
        weather_label = "Moderate rain"
        label_pos = (45 , 305)
    else:
        weather_icon = "rainy-3"
        weather_label = "Heavy rain"
        label_pos = (75 , 305)
    
    if 6 < int(time.strftime("%H")) < 18:
        time_of_day = "day"
    else:
        time_of_day = "night"

    if weather_icon.split("-")[0] in ["rainy" , "cloudy"]:
        if time_of_day == "night":
            icon_pos=(75 , 95)
        else:
            icon_pos = (85 , 95)
        if weather_icon.split("-")[0] == "cloudy":
            size = (220 , 200)
        else:
            size = (200 , 180)
    else:
        if time_of_day == "night":
            icon_pos = (-35 , 120)
        else:
            icon_pos = (95 , 100)
        label_pos = (125 , 305)
        size = (280 , 240)

    if temperature <= 10:
        temp_color = "#8ee0f9"
    elif 10 < temperature <= 25:
        temp_color = "#61f48b"
    elif 25 < temperature <= 30:
        temp_color = "#fcd76a"
    else:
        temp_color = "#fc6955"

    weather_icon = Image.open(f"icons/{weather_icon}-{time_of_day}.png")

    weather_icon = ctk.CTkImage(weather_icon , size=(size[0] , size[1]))

    if not hasattr(frame , "weather_icon"):
        frame.weather_icon = ctk.CTkLabel(frame , text="" , image=weather_icon)
        frame.weather_icon.image = weather_icon
        frame.weather_icon.place(x=icon_pos[0] , y=icon_pos[1])
    else:
        frame.weather_icon.lift()

    if not hasattr(frame , "weather_label"):
        frame.weather_label = ctk.CTkLabel(frame , text=weather_label , font=("arial" , 40 , "bold"))
        frame.weather_label.place(x=label_pos[0] , y=label_pos[1])
    else:
        frame.weather_label.configure(text=weather_label)
        frame.weather_label.lift()

    if not hasattr(frame , "temperature_label"):
        frame.temperature_label = ctk.CTkLabel(frame , text=f"{temperature} °C" , text_color=temp_color , font=("arial" , 40 , "bold"))
        frame.temperature_label.place(x=115 , y=260)
    else:
        frame.temperature_label.configure(text=f"{temperature} °C")
        frame.temperature_label.lift()

    if not hasattr(frame , "windspeed_label"):
        frame.windspeed_label = ctk.CTkLabel(frame , text=f"Wind\n{wind_speed} m/s" , font=("arial" , 30 , "bold"))
        frame.windspeed_label.place(x=0 , y=435)
    else:
        frame.windspeed_label.configure(text=f"Wind\n{wind_speed} m/s")
        frame.windspeed_label.lift()

    if not hasattr(frame , "humidity_label"):
        frame.humidity_label = ctk.CTkLabel(frame , text=f"Humidity\n{humidity}%" , font=("arial" , 30 , "bold"))
        frame.humidity_label.place(x=220 , y=435)
    else:
        frame.humidity_label.configure(text=f"Humidity\n{humidity}%")
        frame.humidity_label.lift()

def get_city_weather(geocode_data, id , frame , city):
    weather_data = read_cache("cache/weather/" , city , id)
    if weather_data is None:
        try:
            request = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={geocode_data["results"][id]["latitude"]}&longitude={geocode_data["results"][id]["longitude"]}&hourly=temperature_2m,rain,showers,snowfall,snow_depth,surface_pressure,wind_speed_10m,relative_humidity_2m,cloud_cover&forecast_days=1")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("No connection." , "Cant fetch data without internet.")
            return
        if request.status_code == 200:
            weather_data = request.json()
            if weather_data.get("error"):
                messagebox.showerror("Fetching Error" , "Weather unavailable for this city.")
                return
            weather_data["date"] = datetime.datetime.today().strftime("%D")
            write_cache("cache/weather/" , city , weather_data , id)
        else:
            messagebox.showerror("Fetching Error" , f"Error: {request.status_code}")
    organize_data(frame , weather_data , geocode_data , id)

def get_city_geocode(window , city , fallback_frame , frame):
    geocode_data = read_cache("cache/geo-coding/" , city)
    if geocode_data is None:
        try:
            request = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=10&language=en&format=json")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("No Connection." , "Cant fetch data without internet.")
            return
        if request.status_code == 200:
            geocode_data = request.json()
            if geocode_data.get("results"):
                write_cache("cache/geo-coding/" , city , geocode_data)
            else:
                messagebox.showerror("Unknown City." , "perhaps you misspeled the city's name?")
                show_frame(fallback_frame)
                return
        else:
            messagebox.showerror("Fetching Error." , f"Error: {request.status_code}")
            show_frame(fallback_frame)
            return
    show_results(frame , geocode_data , city)

def fetch_data(window , frame , fallback_frame , city , event=None):
    if city == "":
        return
    get_city_geocode(window , city , fallback_frame , frame)

def change_theme(prev_theme , theme_button , event=None):
    config_data = config
    if prev_theme == "Light":
        text = "☀︎"
        ctk.set_appearance_mode("Dark")
        config_data["theme"] = "Dark"
    else:
        text = "☾"
        ctk.set_appearance_mode("Light")
        config_data["theme"] = "Light"
      
    theme_button.configure(text=text)
    update_config(config)
