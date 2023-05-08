#
# Try out: python3 verify.py -t 0.3 100_101.png 100_03.jpg 101_03.jpg 102_03.jpg
#

import face_biometric_recognition as lib
import sys, getopt
import re

from os import listdir
from os.path import isfile, join

IMAGES = "./images"
DIR_FMT = re.compile("morphs-[a-z]+")
MORPH_FMT = re.compile("([a-z]+)-(\d+)_(\d+)\.[a-z]{3}")

REAL_DIR = "./morphs-noah/"
MORPH_DIR = "./morphs-noah/"

def compare(morph_img, real_imgs, tolerance = 0.5):
    morph = lib.load_image_file(morph_img)
    morph_enc = lib.face_encodings(morph)[0]
    morph_landmarks = lib.face_landmarks(morph)

    reals = []

    for ri in real_imgs:
        ri_img = lib.load_image_file(ri)
        ri_enc = lib.face_encodings(ri_img)[0]

        reals.append(ri_enc)

    results = lib.compare_faces(reals, morph_enc, tolerance)

    # Prints [True, False] since 100 is recognized, 101 is not
    print("Results: ", morph_img, "\tTolerance:", tolerance)

    for i, ri in enumerate(real_imgs):
        print(" - ", ri, "\t", results[i])

    return results

# Filename format: {program}-{left}_{right}.jpg
def getImageTupel(morphDir, morphFilename):
    match = MORPH_FMT.search(morphFilename)

    if match != None:
        program = match.group(1)
        left = match.group(2)
        right = match.group(3)

        # TODO: randomize
        tolerance = 0.6

        leftFile = IMAGES + "/" + left + "_03.jpg"
        rightFile = IMAGES + "/" + right + "_03.jpg"
        comp = compare(morphDir + "/" + morphFilename, [leftFile, rightFile], tolerance)

        # program, original left, original right, tolerance used, match (left, right)
        return [program, left, right, tolerance, comp]
    
    return []

def readImages():
    onlyfiles = [f for f in listdir(IMAGES) if isfile(join(IMAGES, f))]
    return onlyfiles

def doMorphDir(dir):
    files = [f for f in listdir(dir) if isfile(join(dir, f))]
    tupels = []

    for f in files:
        tupels.append(getImageTupel(dir, f))

    return tupels

def doMorphDirs():
    onlydirs = [f for f in listdir("./") if not isfile(join("./", f))]
    onlydirs = list(filter(lambda d: DIR_FMT.search(d) != None, onlydirs))

    tupels = []

    for d in onlydirs:
        tupels.extend(doMorphDir(d))

    print(tupels)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "t:a", ["tolerance", "auto"])
    except getopt.GetoptError as err:
        print(err)
        
        return
    
    output = None
    verbose = False
    tolerance = 0.6
    auto = False

    for o, a in opts:
        if o in ("-t", "--tolerance"):
            tolerance = float(a)
        elif o in ("-a", "--auto"):
            auto = True
        else:
            assert False, "Unknown option: " + o

    if auto != True and len(sys.argv) < 3:
        print("Syntax: verify.py [-ta] MORPH REAL...")

        return

    if auto:
        print("Automatic testing enabled...")

        doMorphDirs()
    else:
        offset = (len(opts) * 2) + 1
        morph = sys.argv[offset]
        reals = sys.argv[(offset + 1):]

        print("Checking morphs:")
        print(" morph \t\t= ", morph)
        print(" real \t\t= ", ", ".join(reals))
        print(" tolerance \t= ", tolerance)

        compare(morph, reals, tolerance)

if __name__ == "__main__":
    main()