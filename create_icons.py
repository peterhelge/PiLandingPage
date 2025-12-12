import os
from PIL import Image, ImageDraw

# Create assets directory
if not os.path.exists("assets"):
    os.makedirs("assets")

def draw_sun(filename, bg_color="#121212"):
    img = Image.new("RGBA", (100, 100), bg_color)
    draw = ImageDraw.Draw(img)
    draw.ellipse((25, 25, 75, 75), fill="#FFD700")
    img.save(filename)

def draw_cloud(filename, bg_color="#121212", color="#B0BEC5"):
    img = Image.new("RGBA", (100, 100), bg_color)
    draw = ImageDraw.Draw(img)
    draw.ellipse((20, 40, 60, 80), fill=color)
    draw.ellipse((40, 30, 80, 70), fill=color)
    draw.ellipse((10, 50, 50, 80), fill=color)
    img.save(filename)

def draw_rain(filename, bg_color="#121212"):
    draw_cloud(filename, bg_color, "#90A4AE")
    img = Image.open(filename)
    draw = ImageDraw.Draw(img)
    draw.line((35, 80, 25, 95), fill="#4FC3F7", width=3)
    draw.line((50, 80, 40, 95), fill="#4FC3F7", width=3)
    draw.line((65, 80, 55, 95), fill="#4FC3F7", width=3)
    img.save(filename)

def draw_snow(filename, bg_color="#121212"):
    draw_cloud(filename, bg_color, "#CFD8DC")
    img = Image.open(filename)
    draw = ImageDraw.Draw(img)
    draw.ellipse((30, 85, 36, 91), fill="white")
    draw.ellipse((50, 82, 56, 88), fill="white")
    draw.ellipse((70, 85, 76, 91), fill="white")
    img.save(filename)

def draw_thunder(filename, bg_color="#121212"):
    draw_cloud(filename, bg_color, "#546E7A")
    img = Image.open(filename)
    draw = ImageDraw.Draw(img)
    points = [(50, 60), (40, 80), (55, 80), (45, 100)]
    draw.line(points, fill="#FFEA00", width=4, joint="curve")
    img.save(filename)

def draw_lightbulb(filename, bg_color="#121212", bulb_color="#555555"):
    img = Image.new("RGBA", (100, 100), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Bulb glass (Circle)
    draw.ellipse((30, 20, 70, 60), fill=bulb_color)
    
    # Bulb base (Rectangle-ish)
    draw.rectangle((40, 55, 60, 75), fill=bulb_color)
    
    # Screw thread (Lines)
    draw.line((40, 60, 60, 60), fill="#222", width=2)
    draw.line((40, 65, 60, 65), fill="#222", width=2)
    draw.line((40, 70, 60, 70), fill="#222", width=2)
    
    # Bottom tip
    draw.pieslice((40, 70, 60, 85), 0, 180, fill="#333")
    
    img.save(filename)

def draw_power(filename, bg_color="#121212", fg_color="#D32F2F"):
    img = Image.new("RGBA", (100, 100), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Circle arc (almost full circle)
    draw.arc((20, 20, 80, 80), start=300, end=240, fill=fg_color, width=8)
    
    # Vertical line at top
    draw.line((50, 20, 50, 50), fill=fg_color, width=8)
    
    img.save(filename)

def generate_icons():
    print("Generating icons...")
    draw_sun("assets/clear.png")
    draw_cloud("assets/clouds.png")
    draw_rain("assets/rain.png")
    draw_snow("assets/snow.png")
    draw_thunder("assets/thunderstorm.png")
    draw_cloud("assets/mist.png", color="#78909C")
    
    # Home Assistant Icons
    draw_lightbulb("assets/bulb_on.png", bulb_color="#FFD700") # Gold/Yellow
    draw_lightbulb("assets/bulb_off.png", bulb_color="#444444") # Dark Gray
    
    # System Icons
    draw_power("assets/power.png", fg_color="#E53935") # Red (Shutdown)
    draw_reboot("assets/reboot.png", fg_color="#FDD835") # Yellow/Orange
    draw_exit("assets/exit.png", fg_color="#90A4AE") # Blue/Gray
    
    # Volume Icons
    draw_vol_down("assets/vol_down.png")
    draw_vol_up("assets/vol_up.png")
    
    print("Done. Icons saved to ./assets/")

def draw_reboot(filename, bg_color="#121212", fg_color="#FDD835"):
    img = Image.new("RGBA", (100, 100), bg_color)
    draw = ImageDraw.Draw(img)
    # Arrow Circle
    draw.arc((20, 20, 80, 80), start=30, end=330, fill=fg_color, width=8)
    # Arrow Head
    draw.polygon([(70, 20), (90, 30), (70, 40)], fill=fg_color)
    img.save(filename)

def draw_exit(filename, bg_color="#121212", fg_color="#90A4AE"):
    img = Image.new("RGBA", (100, 100), bg_color)
    draw = ImageDraw.Draw(img)
    # Door Frame
    draw.rectangle((30, 20, 70, 80), outline=fg_color, width=5)
    # Door Arrow
    draw.line((40, 50, 85, 50), fill=fg_color, width=5)
    draw.polygon([(80, 40), (95, 50), (80, 60)], fill=fg_color)
    img.save(filename)

def draw_vol_down(filename, bg_color=(0, 0, 0, 0), fg_color="white"):
    img = Image.new("RGBA", (100, 100), bg_color)
    draw = ImageDraw.Draw(img)
    # Speaker body
    draw.polygon([(20, 35), (20, 65), (40, 65), (55, 80), (55, 20), (40, 35)], fill=fg_color)
    # Low volume wave (small)
    draw.arc((40, 40, 70, 60), 300, 60, fill=fg_color, width=4)
    img.save(filename)

def draw_vol_up(filename, bg_color=(0, 0, 0, 0), fg_color="white"):
    img = Image.new("RGBA", (100, 100), bg_color)
    draw = ImageDraw.Draw(img)
    # Speaker body
    draw.polygon([(20, 35), (20, 65), (40, 65), (55, 80), (55, 20), (40, 35)], fill=fg_color)
    # High volume waves
    draw.arc((40, 40, 70, 60), 300, 60, fill=fg_color, width=4)
    draw.arc((30, 30, 80, 70), 300, 60, fill=fg_color, width=4)
    draw.arc((20, 20, 90, 80), 300, 60, fill=fg_color, width=4)
    img.save(filename)

if __name__ == "__main__":
    generate_icons()