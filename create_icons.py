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

def generate_icons():
    print("Generating icons...")
    draw_sun("assets/clear.png")
    draw_cloud("assets/clouds.png")
    draw_rain("assets/rain.png")
    draw_snow("assets/snow.png")
    draw_thunder("assets/thunderstorm.png")
    draw_cloud("assets/mist.png", color="#78909C")
    print("Done. Icons saved to ./assets/")

if __name__ == "__main__":
    generate_icons()