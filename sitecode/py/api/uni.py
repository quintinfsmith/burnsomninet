from sitecode.py.gitmanip import Project
from sitecode.py.cachemanager import get_cached, check_cache, update_cache
from sitecode.py import api
from burnsomninet.views import STATIC_PATH
import json
from datetime import datetime, timedelta
import time, os
from PIL import Image

def process_request(**kwargs):
    disciplines = kwargs.get("d", "").split(",")
    for i, entry in enumerate(disciplines):
        disciplines[i] = entry.strip()

    inputs = {
        "mountain": {
            "src": "/univids/muni",
            "alias": "Mountain",
        },
        "street": {
            "src": "/univids/street",
            "alias": "Street"
        }
    }

    output = []
    for discipline, input in inputs.items():
        if disciplines and discipline not in disciplines:
            continue

        new_dict = {
            "name": input["alias"],
            "subsections": []
        }

        root_dir = f"{STATIC_PATH}{input["src"]}"
        for subsection in os.listdir(root_dir):
            if not os.path.isdir(f"{root_dir}/{subsection}"):
                continue

            subsection_dict = {
                "name": subsection.title(),
                "video_urls": []
            }

            for (main, dirs, files) in os.walk(f"{root_dir}/{subsection}"):
                for f in files:
                    if not f.lower().endswith(".webm"):
                        continue

                    vidpath = f"{main}/{f}".replace("//", "/")
                    if not os.path.isfile(f"{vidpath}.png"):
                        os.system(f"ffmpeg -i \"{vidpath}\" -ss 00:00:00 -vframes 1 \"{vidpath}.png\"")
                        image = Image.open(f"{vidpath}.png")
                        if (image.size[0] / image.size[1]) < (16 / 9):
                            nh = image.size[1]
                            nw = int(nh * (16 / 9))
                            new_image = Image.new("RGBA", (nw, nh), (0,0,0,0))
                            x_offset = (nw - image.size[0]) // 2
                            for y in range(image.size[1]):
                                for x in range(image.size[0]):
                                    new_image.putpixel((x_offset + x, y), image.getpixel((x, y)))
                            new_image.save(f"{vidpath}.png")
                        elif image.size[0] / image.size[1] > (16 / 9):
                            nw = image.size[0]
                            nh = int(nw / (16 / 9))
                            new_image = Image.new("RGBA", (nw, nh), (0,0,0,0))
                            y_offset = (nh - image.size[1]) // 2
                            for y in range(image.size[1]):
                                for x in range(image.size[0]):
                                    new_image.putpixel((x, y_offset + y), image.getpixel((x, y)))
                        else:
                            new_image = image

                        nw = 500
                        nh = int(nw * (9 / 16))
                        new_image = new_image.resize((nw, nh))
                        new_image.save(f"{vidpath}.png")


                    rel_path = "/content/" + vidpath[len(STATIC_PATH) + 1:]

                    subsection_dict["video_urls"].append(rel_path)
            new_dict["subsections"].append(subsection_dict)
        output.append(new_dict)

    if len(disciplines) == 1:
        output = output[0]
    
    return output
