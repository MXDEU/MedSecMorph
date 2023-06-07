#
# Try out: python3 verify.py -t 0.3 100_101.png 100_03.jpg 101_03.jpg 102_03.jpg
#
# Automatic testing: (standard tolerance is 0.6)
#  python3 verify.py -a
#  python3 verify.py -a -t 0.4
#

import face_biometric_recognition as lib
import sys, getopt
import re

from os import listdir
from os.path import isfile, join
from random import randrange
import random

DRYRUN = False
TYPE_MORPH = "morph"
TYPE_ORIG = "orig"

IMAGES = "images"
# DIR_FMT = re.compile("morphs-emil") # 
DIR_FMT = re.compile("morphs-[a-z]+") # Run a single dir: morphs-name
IMG_FMT = re.compile(IMAGES + "/0*(\d+)_03.jpg")
FOLDER_NAME_FMT = re.compile("morphs-(.*)/.*")
MORPH_FMT = re.compile("([a-z]+)-(\d+)_(\d+)\.[a-z]{3}")

class Sample:
    def __init__(self, img, imgs, matches, tolerance):
        self.type = "unset"
        self.program = "unset"
        self.img = img
        self.imgs = imgs
        self.matches = matches
        self.tolerance = tolerance

        imgId = IMG_FMT.search(img)
        imgFolder = FOLDER_NAME_FMT.search(img)

        if imgId is not None:
            self.imgId = imgId.group(1)
        else:
            self.imgId = -1

        if imgFolder is not None:
            self.imgFolder = imgFolder.group(1)
        else:
            self.imgFolder = '<none>'

    def __str__(self):
        if self.type == TYPE_MORPH:
            return f"[{self.type}, {self.program}, {self.imgFolder}, {self.img}, {self.imgs}, {self.matches}, {self.tolerance}]"
        elif self.type == TYPE_ORIG:
            return f"[{self.type}, {self.img}, {self.imgId}, {self.imgs}, {self.matches}, {self.tolerance}]"

        return f"[{self.type}]"

    def __repr__(self):
        return str(self)

images = []

# Eval

# Returns an array of all failed result tupels.
# A tupel is failed if any of the matches returned true.
def findErrors(results):
    return

# Returns FMR
def findFMR(results):
    fm = 0 # false matches
    matches = 0

    for s in results:
        matches = matches + len(s.matches)

        for i, m in enumerate(s.matches):
            falseMatch = (m == True and not s.imgId == s.imgs[i]) or (m == False and s.imgId == s.imgs[i])

            if falseMatch:
                fm = fm + 1

    if matches == 0:
        return [0, 0]
    
    return [fm, round(fm / matches, 3)]

# Execute

def compare(morph_img, real_imgs, tolerance = 0.5):
    if DRYRUN:
        return [random.choice([True, False]) for ri in real_imgs]

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

def genSample(imgFile, imgs, tolerance = 0.6):
    files = list(map(lambda i: IMAGES + "/" + i + "_03.jpg", imgs))
    comp = compare(imgFile, files, tolerance)
    sample = Sample(imgFile, imgs, comp, tolerance)

    return sample

# Filename format: {program}-{left}_{right}.jpg
def genMorphSample(morphDir, morphFilename, tolerance):
    match = MORPH_FMT.search(morphFilename)

    if match != None:
        morphFile = morphDir + "/" + morphFilename
        program = match.group(1)
        left = match.group(2)
        right = match.group(3)

        images.append(left)
        images.append(right)

        sample = genSample(morphFile, [left, right], tolerance)
        sample.type = TYPE_MORPH
        sample.program = program

        return sample

    return None

def getImageTupel(morphDir, morphFilename):
    match = MORPH_FMT.search(morphFilename)

    if match != None:
        program = match.group(1)
        left = match.group(2)
        right = match.group(3)

        # TODO: randomize
        tolerance = 0.6

        morphFile = morphDir + "/" + morphFilename
        leftFile = IMAGES + "/" + left + "_03.jpg"
        rightFile = IMAGES + "/" + right + "_03.jpg"

        comp = compare(morphFile, [leftFile, rightFile], tolerance)
        images.append(left)
        images.append(right)

        # program, original left, original right, tolerance used, match (left, right)
        return [program, left, right, tolerance, comp]
    
    return []

def readImages():
    onlyfiles = [f for f in listdir(IMAGES) if isfile(join(IMAGES, f))]
    return onlyfiles

def doMorphDir(dir, tolerance):
    files = [f for f in listdir(dir) if isfile(join(dir, f))]
    samples = []

    for f in files:
        samples.append(genMorphSample(dir, f, tolerance))

    return samples

def doMorphDirs(tolerance):
    onlydirs = [f for f in listdir("./") if not isfile(join("./", f))]
    onlydirs = list(filter(lambda d: DIR_FMT.search(d) != None, onlydirs))

    print("")
    print("Processing morph images:")

    samples = []

    for d in onlydirs:
        samples.extend(doMorphDir(d, tolerance))

    return samples

def doOriginalImages(tolerance):
    if len(images) % 2 != 0:
        return

    print("")
    print("Processing original images:")
    
    pairs = []
    samples = []

    for i in range(len(images) - 1):
        pairs.append([images[i], images[i + 1]])

    pairs.append([images[len(images) - 1], images[0]])

    for p in pairs:
        sample = genSample(IMAGES + "/" + p[0] + "_03.jpg", [p[1]], tolerance)
        sample.type = TYPE_ORIG

        samples.append(sample)

    return samples

def groupSamples(samples, attribute):
    grouped = {}

    for s in samples:
        if getattr(s, attribute) not in grouped:
            grouped[getattr(s, attribute)] = []

        grouped[getattr(s, attribute)].append(s)

    return grouped

def autoTesting(tolerance):
    morphSamples = doMorphDirs(tolerance)
    origSamples = doOriginalImages(tolerance)

    # grouped by program
    groupedMorphs = {}

    for s in morphSamples:
        if s.program not in groupedMorphs:
            groupedMorphs[s.program] = []

        groupedMorphs[s.program].append(s)

    # error rates
    morphFMR = findFMR(morphSamples)
    origFMR = findFMR(origSamples)

    print("")
    print("Samples collected:")
    print(" morph --", len(morphSamples), " FMR:", morphFMR[1], " False matches:", morphFMR[0], "of", len(morphSamples) * 2, "comparisons")
    print(" origs --", len(origSamples), " FMR:", origFMR[1], " False matches:", origFMR[0])

    print("")
    print("Morphs:")

    for gm in groupedMorphs.keys():
        fmr = findFMR(groupedMorphs[gm])

        print(" ==", gm, "@ Samples:", len(groupedMorphs[gm]), " FMR:", fmr[1], " False matches:", fmr[0])
        print(groupedMorphs[gm])

    print("")
    print("FMR by creator:")

    groupedMorphs = groupSamples(morphSamples, 'imgFolder')

    for gm in groupedMorphs.keys():
        fmr = findFMR(groupedMorphs[gm])

        print(" *", gm, "\t@ Samples:", len(groupedMorphs[gm]), " FMR:", fmr[1], " False matches:", fmr[0], "of", len(groupedMorphs[gm]) * 2, "comparisons")

    print("")
    print("Originals:")
    print(origSamples)

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

        autoTesting(tolerance)
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