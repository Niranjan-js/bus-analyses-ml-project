import imageio
from pathlib import Path

SCREENSHOTS_DIR = Path(r"c:\Users\niran\Downloads\mini project collage\learning\AI_College_Transport_Analyzer\screenshots")
webm_file = SCREENSHOTS_DIR / "working_demo.webm"
mp4_file = SCREENSHOTS_DIR / "working_demo.mp4"
gif_file = SCREENSHOTS_DIR / "working_demo.gif"

print(f"Reading {webm_file}...")
reader = imageio.get_reader(str(webm_file))
fps = reader.get_meta_data().get('fps', 10)
print(f"FPS: {fps}")

# 1. Save to MP4
writer_mp4 = imageio.get_writer(str(mp4_file), fps=fps)
# 2. Save to GIF (subsampled every 3rd frame for lightweight size)
writer_gif = imageio.get_writer(str(gif_file), fps=fps/2)

count = 0
for frame in reader:
    writer_mp4.append_data(frame)
    if count % 2 == 0:
        writer_gif.append_data(frame)
    count += 1

writer_mp4.close()
writer_gif.close()
reader.close()

print(f"✅ Converted {count} frames to {mp4_file} and {gif_file} successfully!")
