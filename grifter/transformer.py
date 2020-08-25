import argparse

import face_recognition
import numpy as np
from PIL import Image

from .utils import gif

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", "--infile", required=True)
    parser.add_argument("-out", "--outfile", required=True)
    parser.add_argument("-src", "--source", required=True)
    parser.add_argument("-sc", "--scale", type=float, default=1)
    parser.add_argument("-f", "--frames", type=int, default=None)
    parser.add_argument("-up", "--upscale", type=int, default=0)
    args = parser.parse_args()

    if args.frames is not None and args.frames <= 0:
        print("[*] no frames to process, exiting")
        return

    im = Image.open(args.infile)
    source = Image.open(args.source)

    outputs = []
    for i, frame in enumerate(gif.get_frames(im)):
        print(f"\r[*] processing frame {i}", end="", flush=True)

        array = np.array(frame.convert('RGB'))
        faces = face_recognition.face_locations(array, number_of_times_to_upsample=args.upscale, model='cnn')
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
                factor = source.width / width
            else:
                factor = source.height / height
            ssource = source.resize((int(source.width / factor * args.scale), int(source.height / factor * args.scale)))

            output.paste(ssource, (
                left - (ssource.width - width) // 2,
                top - (ssource.height - height) // 2,
            ), ssource)

        output = Image.alpha_composite(frame, output)

        outputs.append(output)
        if args.frames is not None and len(outputs) >= args.frames:
            break

    print(f"\r[*] processed {len(outputs)} frames total")
    print("[*] done")

    outputs[0].save(args.outfile, save_all=True, append_images=outputs[1:], repeat=0)
