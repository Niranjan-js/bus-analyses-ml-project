import imageio
from pathlib import Path

SCREENSHOTS_DIR = Path(r"c:\Users\niran\Downloads\mini project collage\learning\AI_College_Transport_Analyzer\screenshots")
mp4_file = SCREENSHOTS_DIR / "working_demo.mp4"
gif_file = SCREENSHOTS_DIR / "working_demo.gif"

print("Converting MP4 to GIF...")
reader = imageio.get_reader(str(mp4_file))
writer = imageio.get_writer(str(gif_file), fps=10)

count = 0
for frame in reader:
    if count % 3 == 0:
        writer.append_data(frame)
    count += 1

writer.close()
reader.close()
print(f"DONE! Saved GIF with {count} frames.")
