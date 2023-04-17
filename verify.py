import face_biometric_recognition as lib

morph = lib.load_image_file("./morphs-noah/100_101.png")
morph_landmarks = lib.face_landmarks(morph)

real1 = lib.load_image_file("./morphs-noah/100_03.jpg")
real2 = lib.load_image_file("./morphs-noah/101_03.jpg")

morph_encodings = lib.face_encodings(morph)[0]
real1_encodings = lib.face_encodings(real1)[0]
real2_encodings = lib.face_encodings(real2)[0]

results = lib.compare_faces([real1_encodings, real2_encodings], morph_encodings)

# Prints [True, False] since 100 is recognized, 101 is not
print(results)