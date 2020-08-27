import argparse

import face_recognition
import numpy as np
from PIL import Image

from .utils import gif

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infile", required=True)
    parser.add_argument("-o", "--outfile", required=True)
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("-s", "--scale", type=float, default=1)
    parser.add_argument("--frames", type=int, default=None)
    parser.add_argument("--upscale", type=int, default=0)
    parser.add_argument("--model", choices=["cnn", "hog"], default="hog")
    args = parser.parse_args()

    if args.frames is not None and args.frames <= 0:
        print("[*] no frames to process, exiting")
        return

    im = Image.open(args.infile)
    target = Image.open(args.target)

    outputs = []
    for i, frame in enumerate(gif.get_frames(im)):
        print(f"\r[*] processing frame {i}", end="", flush=True)

        array = np.array(frame.convert('RGB'))
        faces = face_recognition.face_locations(array, number_of_times_to_upsample=args.upscale, model=args.model)
        # faces = face_recognition.face_locations(array, number_of_times_to_upsample=args.upscale)

        if len(faces) == 0:
            print(f"\r[*] WARNING: no faces found in frame {i}")
        elif len(faces) > 1:
            print(f"\r[*] WARNING: multiple faces found in frame {i}")

        output = Image.new('RGBA', im.size)
        for face in faces:
            top, left, bottom, right = face
            width = right - left
            height = bottom - top
            if width > height:
                factor = target.width / width
            else:
                factor = target.height / height
            rtarget = target.resize((int(target.width / factor * args.scale), int(target.height / factor * args.scale)))

            output.paste(rtarget, (
                left - (rtarget.width - width) // 2,
                top - (rtarget.height - height) // 2,
            ), rtarget)

        output = Image.alpha_composite(frame, output)

        outputs.append(output)
        if args.frames is not None and len(outputs) >= args.frames:
            break

    print(f"\r[*] processed {len(outputs)} frames total")
    print("[*] done")

    outputs[0].save(args.outfile, save_all=True, append_images=outputs[1:], repeat=0)
