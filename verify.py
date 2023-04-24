#
# Try out: python3 verify.py -t 0.3 100_101.png 100_03.jpg 101_03.jpg 102_03.jpg
#

import face_biometric_recognition as lib
import sys, getopt

REAL_DIR = "./morphs-noah/"
MORPH_DIR = "./morphs-noah/"

def compare(morph_img, real_imgs, tolerance = 0.5):
    morph = lib.load_image_file(MORPH_DIR + morph_img)
    morph_enc = lib.face_encodings(morph)[0]
    morph_landmarks = lib.face_landmarks(morph)

    reals = []

    for ri in real_imgs:
        ri_img = lib.load_image_file(REAL_DIR + ri)
        ri_enc = lib.face_encodings(ri_img)[0]

        reals.append(ri_enc)

    results = lib.compare_faces(reals, morph_enc, tolerance)

    # Prints [True, False] since 100 is recognized, 101 is not
    print("Results: ",)

    for i, ri in enumerate(real_imgs):
        print(" - ", ri, "\t", results[i])

def main():
    if len(sys.argv) < 3:
        print("Syntax: verify.py [-t] MORPH REAL...")

        return

    try:
        opts, args = getopt.getopt(sys.argv[1:], "t:", ["tolerance"])
    except getopt.GetoptError as err:
        print(err)
        
        return

    offset = (len(opts) * 2) + 1
    morph = sys.argv[offset]
    reals = sys.argv[(offset + 1):]
    
    output = None
    verbose = False
    tolerance = 0.6

    for o, a in opts:
        if o in ("-t", "--tolerance"):
            tolerance = float(a)
        else:
            assert False, "Unknown option: " + o

    print("Checking morphs:")
    print(" morph \t\t= ", morph)
    print(" real \t\t= ", ", ".join(reals))
    print(" tolerance \t= ", tolerance)

    compare(morph, reals, tolerance)

if __name__ == "__main__":
    main()