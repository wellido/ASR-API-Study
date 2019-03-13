import numpy as np
from keras.datasets import cifar10
from PIL import Image

# Custom Networks
from IR.networks.resnet import ResNet

# Helper functions
import IR.my_differential_evolution as my_differential_evolution
import IR.differential_evolution as differential_evolution
import IR.helper as helper
from IR.ir_api import ir_api

np.random.seed = 100

from cv2 import xfeatures2d as xf
from random import random


(x_train, y_train), (x_test, y_test) = cifar10.load_data()
class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


def perturb_image(xs, img):
    # If this function is passed just one perturbation vector,
    # pack it in a list to keep the computation the same
    if xs.ndim < 2:
        xs = np.array([xs])

    # Copy the image n == len(xs) times so that we can
    # create n new perturbed images
    tile = [len(xs)] + [1] * (xs.ndim + 1)
    imgs = np.tile(img, tile)

    # Make sure to floor the members of xs as int types
    xs = xs.astype(int)

    for x, img in zip(xs, imgs):
        # Split x into an array of 5-tuples (perturbation pixels)
        # i.e., [[x,y,r,g,b], ...]
        pixels = np.split(x, len(x) // 5)
        for pixel in pixels:
            # At each pixel's x,y position, assign its rgb value
            x_pos, y_pos, *rgb = pixel
            img[x_pos, y_pos] = rgb
    return imgs


def predict_classes(xs, img, target_class, model, minimize=True):
    # Perturb the image with the given pixel(s) x and get the prediction of the model
    imgs_perturbed = perturb_image(xs, img)
    print(imgs_perturbed.shape)
    predictions = model.predict(imgs_perturbed)[:,target_class]
    # This function should always be minimized, so return its complement if needed
    return predictions if minimize else 1 - predictions


def attack_success(x, img, target_class, model, targeted_attack=False, verbose=False):
    # Perturb the image with the given pixel(s) and get the prediction of the model
    attack_image = perturb_image(x, x_test[img])[0]

    confidence = model.predict_one(attack_image)
    predicted_class = np.argmax(confidence)

    # If the prediction is what we want (misclassification or
    # targeted classification), return True
    if(verbose):
        print('Confidence:', confidence[target_class])
    if ((targeted_attack and predicted_class == target_class) or
            (not targeted_attack and predicted_class != target_class)):
        return True

def predict_classes2(xs, img, target_class, minimize=True):
    # Perturb the image with the given pixel(s) x and get the prediction of the model
    imgs_perturbed = perturb_image(xs, img)[0]
    print(imgs_perturbed.shape)
    save_img = Image.fromarray(imgs_perturbed.astype('uint8')[0:224, 0:224, 0:2])
    save_img.save("use_img.png")
    image = get_file_content('use_img.png')
    obj_type, predictions = ir_api(image)
    if obj_type == target_class:
    # This function should always be minimized, so return its complement if needed
        return [predictions] if minimize else 1 - [predictions]
    else:
        return [0.1]


def attack_success2(target_class, targeted_attack=False, verbose=False):
    # Perturb the image with the given pixel(s) and get the prediction of the model
    # attack_image = perturb_image(x, img)[0]

    attack_image = get_file_content('use_img.png')
    obj_type, predictions = ir_api(attack_image)
    confidence = predictions
    predicted_class = obj_type
    # If the prediction is what we want (misclassification or
    # targeted classification), return True
    if(verbose):
        print('Confidence:', confidence)
    if ((targeted_attack and predicted_class == target_class) or
            (not targeted_attack and predicted_class != target_class)):
        return True


sift = xf.SIFT_create()


def getFeatureOperation(image, size):
    keypoints, descriptors = sift.detectAndCompute(image, None)
    featurePoints = [k.pt for k in keypoints]
    operation = []
    for f in featurePoints:
        for i in range(size):
            op = [(f[0] + (random() - 0.5)) / 32, (f[1] + (random() - 0.5)) / 32]
            for i in range(3):
                colorChange = random()
                op.append(colorChange)
            operation.append(op)

    if not len(operation):
        for i in range(400):
            op = []
            for i in range(5):
                x = random()
                op.append(x)
            operation.append(op)

    operation = np.array(operation)

    return operation

def getFeatureOperation2(image, size):
    keypoints, descriptors = sift.detectAndCompute(image, None)
    featurePoints = [k.pt for k in keypoints]
    operation = []
    for f in featurePoints:
        for i in range(size):
            op = [(f[0] + (random() - 0.5)) / 224, (f[1] + (random() - 0.5)) / 224]
            for i in range(3):
                colorChange = random()
                op.append(colorChange)
            operation.append(op)

    if not len(operation):
        for i in range(400):
            op = []
            for i in range(5):
                x = random()
                op.append(x)
            operation.append(op)

    operation = np.array(operation)

    return operation


def MyAttack(img, model, target=None, pixel_count=1,
             maxiter=75, popsize=400, verbose=False):
    # Change the target class based on whether this is a targeted attack or not
    targeted_attack = target is not None
    target_class = target if targeted_attack else y_test[img, 0]
    print(y_test[img, 0])

    # Define bounds for a flat vector of x,y,r,g,b values
    # For more pixels, repeat this layout
    bounds = [(0, 32), (0, 32), (0, 256), (0, 256), (0, 256)] * pixel_count

    # Population multiplier, in terms of the size of the perturbation vector x
    popmul = max(1, popsize // len(bounds))
    print("Population", popmul)


    # Format the predict/callback functions for the differential evolution algorithm
    predict_fn = lambda xs: predict_classes(
        xs, x_test[img], target_class, model, target is None)
    callback_fn = lambda x, convergence: attack_success(
        x, img, target_class, model, targeted_attack, verbose)

    feature_operation = getFeatureOperation(x_test[img], size=10)

    # Call Scipy's Implementation of Differential Evolution
    attack_result = my_differential_evolution.my_differential_evolution(
        predict_fn, bounds, feature_operation, maxiter=maxiter, popsize=popmul,
        recombination=1, atol=-1, callback=callback_fn, polish=False, init='random')

    # Calculate some useful statistics to return from this function
    attack_image = perturb_image(attack_result.x, x_test[img])[0]
    prior_probs = model.predict_one(x_test[img])
    predicted_probs = model.predict_one(attack_image)
    predicted_class = np.argmax(predicted_probs)
    actual_class = y_test[img, 0]
    success = predicted_class != actual_class
    cdiff = prior_probs[actual_class] - predicted_probs[actual_class]

    # Show the best attempt at a solution (successful or not)
    helper.plot_image(attack_image, actual_class, class_names, predicted_class)

    return [model.name, pixel_count, img, actual_class, predicted_class, success, cdiff, prior_probs, predicted_probs,
            attack_result.x]


def MyAttack2(img, target=None, pixel_count=1,
             maxiter=75, popsize=400, verbose=False):
    # Change the target class based on whether this is a targeted attack or not
    targeted_attack = target is not None
    target_class = target if targeted_attack else "动物-鱼类"

    # Define bounds for a flat vector of x,y,r,g,b values
    # For more pixels, repeat this layout
    bounds = [(0, 224), (0, 224), (0, 256), (0, 256), (0, 256)] * pixel_count

    # Population multiplier, in terms of the size of the perturbation vector x
    popmul = max(1, popsize // len(bounds))
    print("Population", popmul)


    # Format the predict/callback functions for the differential evolution algorithm
    predict_fn = lambda xs: predict_classes2(
        xs, img, target_class, target is None)
    callback_fn = lambda x, convergence: attack_success2(
        target_class, targeted_attack, verbose)

    feature_operation = getFeatureOperation2(img, size=10)

    # Call Scipy's Implementation of Differential Evolution
    attack_result = differential_evolution.differential_evolution(
        predict_fn, bounds, feature_operation, maxiter=maxiter, popsize=popmul,
        recombination=1, atol=-1, callback=callback_fn, polish=False, init='random')

    # Calculate some useful statistics to return from this function
    attack_image = get_file_content("use_img.png")
    obj_type, predictions = ir_api(attack_image)
    prior_probs = 0.706726
    predicted_probs = predictions
    predicted_class = obj_type
    actual_class = "动物-鱼类"
    success = predicted_class != actual_class

    # Show the best attempt at a solution (successful or not)
    helper.plot_image(attack_image, actual_class, class_names, predicted_class)

    return [model.name, pixel_count, img, actual_class, predicted_class, success, prior_probs, predicted_probs,
            attack_result.x]


image = 102
pixels = 1
# Number of pixels to attack
resnet = ResNet()
model = resnet
image_test = Image.open("../data/img/20180423_004214_sea_lion.png")
image_test = np.asarray(image_test, dtype="uint8")
image_test = image_test.reshape(224, 224, 3)
print(image_test.shape)
_ = MyAttack(image, model, pixel_count=pixels, verbose=True)
# _ = MyAttack2(image_test, pixel_count=pixels, verbose=True)