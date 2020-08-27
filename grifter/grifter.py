import argparse

import face_recognition
import numpy as np
from PIL import Image, ImageDraw

from .utils import gif


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infile", required=True)
    parser.add_argument("-o", "--outfile", required=True)
    parser.add_argument("-t", "--target", default=None)
    parser.add_argument("-s", "--scale", type=float, default=1)
    parser.add_argument("--frames", type=int, default=0)
    parser.add_argument("--upscale", type=int, default=0)
    parser.add_argument("--model", choices=["cnn", "hog"], default="hog")
    args = parser.parse_args()

    im = Image.open(args.infile)

    if args.target:
        target = Image.open(args.target)
    else:
        print("[*] INFO: no target specified, using debug rectangle")
        target = None

    outputs = []
    for i, frame in enumerate(gif.get_frames(im)):
        print(f"\r[*] processing frame {i}", end="", flush=True)

        array = np.array(frame.convert("RGB"))
        faces = face_recognition.face_locations(
            array, number_of_times_to_upsample=args.upscale, model=args.model
        )
        if len(faces) == 0:
            print(f"\r[*] WARNING: no faces found in frame {i}")
        elif len(faces) > 1:
            print(f"\r[*] WARNING: multiple faces found in frame {i}")

        output = process_frame(frame, faces, target, args.scale)
        outputs.append(output)

        if args.frames and len(outputs) >= args.frames:
            break

    print(f"\r[*] processed {len(outputs)} frames total")
    print("[*] done")

    outputs[0].save(args.outfile, save_all=True, append_images=outputs[1:], repeat=0)


def process_frame(frame, faces, target=None, scale=1):
    layer = Image.new("RGBA", frame.size)
    draw = ImageDraw.Draw(layer)
    for face in faces:
        top, left, bottom, right = face
        width = right - left
        height = bottom - top

        if target:
            if width > height:
                factor = target.width / width
            else:
                factor = target.height / height

            fx = int(target.width / factor * scale)
            fy = int(target.height / factor * scale)
            target = target.resize((fx, fy))

            ox = left - (target.width - width) // 2
            oy = top - (target.height - height) // 2
            layer.paste(target, (ox, oy), target)
        else:
            size = max(width, height) * scale
            
            ox = left - (size - width) // 2
            oy = top - (size - height) // 2
            draw.rectangle([(ox, oy), (ox + size, oy + size)], outline='red', width=2)

    return Image.alpha_composite(frame, layer)
