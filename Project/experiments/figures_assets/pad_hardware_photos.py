import sys
from PIL import Image
S, dst = sys.argv[1], sys.argv[2]
items = {"macbook_pro_m4.png": f"{S}/cut/MacBook_Pro_16_inch_M4_Pro_Silver_jpg.png",
         "mac_mini_m4.png": f"{S}/cut/Mac_mini_2024_M4_jpg.png",
         "mac_studio.png": f"{S}/cut/Mac_Studio_1_jpg.png",
         "dgx_spark.png": f"{S}/cut/Nvidia_DGX_Spark_oblique_view_dllu_jpg.png",
         "rtx_5090.png": f"{S}/hw2/Palit_GeForce_RTX_5090_Gamerock_20250530_HOF4166_RAW-Export.png"}
W, H, M = 1200, 900, 40
for out, path in items.items():
    im = Image.open(path).convert("RGBA")
    bbox = im.split()[-1].getbbox(); im = im.crop(bbox)
    sc = min((W - 2 * M) / im.width, (H - 2 * M) / im.height); im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    canvas = Image.new("RGBA", (W, H), (255, 255, 255, 0)); canvas.paste(im, ((W - im.width) // 2, (H - im.height) // 2), im)
    canvas.save(f"{dst}/{out}", optimize=True); print(out)
