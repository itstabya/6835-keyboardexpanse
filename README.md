<div align="center">
<img src="https://user-images.githubusercontent.com/10828202/166475106-f2d31006-6d54-4d60-a44b-0626de2778ca.png" width="40%"/>
</div>

<h1 align="center">
  <strong>Keyboard</strong> Expanse
</h1>

Switching back between the keyboard and mouse not only breaks you from the flow but also wastes time. Keyboard shortcuts are great, but they are also a pain to learn and require awkward control sequences.

<div align="center">

![Screenshot_from_2022-05-03_10-34-45-removebg-preview](https://user-images.githubusercontent.com/10828202/166475758-57fd0b3e-24cc-4731-ae91-3103a3af9555.png)

</div>

Keyboard Expanse is all about keeping your hands on your keyboard; but expanding the interactable surface from simple button presses.

1. **Grounded Location**: Minimises gestural fatigue
2. **Subtle Events**: No large, artificial movements are required.
3. **No "wake"-command**: Allows keyboard-shortcut level speed.
4. **Concrete metaphors** related to real-world experiences: To go left - you point left; to minimise - you swipe the window away; to change desktop - you move along the keyboard.
5. **Works alongside Keyboard Shortcuts**: Keyboard shortcuts still have a place in this system: Copy + Paste are both ubiquitous, well-known and have no quick facsimile in gestural space.

## :wrench: Technology

Python, MediaPipe, OpenCV, Plover, Pandas/Numpy, Autopy, (FFMPEG, Seaborn)

## :gear: Installation

### Physical

The physical setup is generally easy, you can either used a raised web-camera facing downwards or attach a mirror to the existing web-camera.

1. **Mirrored Setup**
   - To minimise costs, we used a $5 'Telescoping Inspection Mirror' which had a useful ball-joint to allow rotation of the mirror in-place and some tape. A 3D-printed solution would likely be better.
   - `IS_MIRRORED_DOWN` should be `True` within [main.py](./keyboardexpanse/scripts/main.py)
2. **Webcamera setup**
   - Webcamera should be placed above the keyboard screen and pointed down.
   - `WEBCAM_NUMBER` will likely have to be set to `1` within [main.py](./keyboardexpanse/scripts/main.py)
   - `IS_MIRRORED_DOWN` should be `False` within [main.py](./keyboardexpanse/scripts/main.py)

> _Tips for best results_:
>
> 1. The 'bottom' of the screen should match up with the top row of keyboard.
> 2. You should be able to see your wrists when you are typing on the bottom row of the screen.

### Software

- Requires Python3.8 (due to autopy dependency), use pyenv to install custom version if necessary

```
# Install pyenv
curl https://pyenv.run | bash
pyenv install 3.8.10

# Setup Virtual Environment
python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip setuptools -q

# Install Requirements
pip install -r requirements.txt
```

## :zap: Running

```
python3 -m keyboardexpanse

# Linux may require root
sudo -E env PATH=$PATH python3 -m keyboardexpanse
```

## :+1: Default Gestures

In priority order, visible in [config](./keyboardexpanse/config.yaml).

1. `Index Finger Touch` (Touch two index fingers together): Find and Replace Shortcut
2. `Point` (Clenched fist with index finger extended, on either hand): Move cursor with finger tip position
3. `Peace` (Peace sign on either hand): Click when index and middle finger are together.
4. `Flat Rock Star` (Middle and ring finger are clenched): Change Window (Alt+Esc) when thumb is clenched and released.
5. `Left Thumb Out` (clenched right + left hand with left thumb extended): Tap right arrow key.
6. `Right Thumb Out` (clenched right + left hand with right thumb extended): Tap left arrow key.
7. `Lefthanded L` (clenched right + left hand with left index resting on keyboard and thumb extended): Continuously select characters to the right.
8. `Righthanded L` (clenched right + left hand with right index resting on keyboard and thumb extended): Continuously select characters to the left.
9. `Double L` (two L positions, see above): Select all
10. `Three Up` (left hand points three fingers): Jump to navigation bar in Chrome
11. `New+Index` (left hand has the thumb hidden with all the fingers resting, right hand has the thumb hidden, raise the index finger and return to rest): Create new window
12. `New+Middle` (left hand has the thumb hidden with all the fingers resting, right hand has the thumb hidden, raise the middle finger and return to rest): Close Window

Feel free to experiment and add your own gestures.

## 🏗 Project structure

| File or folder | Description                                                                                                    |
| -------------- | -------------------------------------------------------------------------------------------------------------- |
| `config.yaml`  | Configuration for recognised gestures and the action to perform at that point |
| `hands/detector.py`  | Applies the mediapipe landmark generation, and the classification to each finger (raised, clenched, resting) |
| `hands/gesture.py`  | Handles customised gesture recognition and action triggering. `KNOWN_ACTIONS` are also located at the top of this file.|
| `keyboard/hotkeys.py`  | Cross platform hotkeys for certain tasks. |
| `keyboard/interceptor.py`  | Supresses native keyboard presses and optionally relays them. Also applies the swipe detection using a Rolling Window|
| `keyboard/surfaces.py`  | Detects any keyboard surfaces in the screen using a variety of image processing techniques, provides cam space <-> keyboard space transforms. |
| `keyboard/window.py`  | Simple rolling window implementation using time_ns |
| `scripts/`  | The core entrypoints to keyboard expanse, some are used for testing. |
| `oslayer/`  | Cross-platform interface for Keyboard Control, Logging, and Windows Control from [plover](https://github.com/openstenoproject/plover) |


## :sunglasses: Acknowledgments & Prior Work

- The entire [oslayer](./keyboardexpanse/oslayer) is from [Plover](https://github.com/openstenoproject/plover) - the open source stenotype engine - (with some minor modifications & patches visible via diff).
- The MediaPipe Library does much of the heavy lifting for gesture detection by providing Real-time Hand Landmarks.
- [Typealike](https://dl.acm.org/doi/10.1145/3486952), although we started this project without discovering Typealike (a very similar project in many ways!), the insights from the paper were invaluable - in particular use of a mirror to create the downward view was inspired.
- [DownChord and UpChord](https://dl.acm.org/doi/10.1145/2948708.2948715)
- [Métamorphe](https://hal.inria.fr/hal-01821240/file/bailly13a.pdf)
- [HotStrokes](https://dl.acm.org/doi/10.1145/3290605.3300395)
- [Keyboard surface interaction](https://arxiv.org/pdf/1601.04029.pdf) Ramos et al.
- [GestKeyboard](https://dl.acm.org/doi/10.1145/2556288.2557362)
- [FingerArc and FingerChord](https://dl.acm.org/doi/10.1145/3242587.3242589)
- [Finger-Aware Shortcuts](https://dl.acm.org/doi/10.1145/2858036.2858355) Zheng et al

## :art: Concepts

### Gesture Taxonomy

Every gesture can be encoded in a string:
- "U" - Finger is raised
- "R" - Finger is resting
- "C" _ Finger is clenched
- "X" - Don't Care, can be in any position

Thumbs are unique in that they cannot be "resting", they are always either extended "U" or clenched "C".

### Tap+Touch

![Tap+Touch](https://user-images.githubusercontent.com/10828202/166473601-75f7ab45-509a-4f2d-b159-266e519bb5ea.gif)

### Swipe Commands

![Swipe](https://user-images.githubusercontent.com/10828202/166473663-ebf38960-2478-45e6-9267-bdcee09e65c8.gif)

### Future Plans

- Chord = simultaneously pressed commands
- Consume keystrokes until out of sequence
- Directional commands
  - Benefit from scaling: Rotation/Scaling/Flipping/Aligning/Colour Picker/Slider
  - Roll wrist / Rotate Arm

### Layers

Each layer <=> a modifier application

- Keyboard map includes transparent keycodes (arrow down)
- Right toggle_T:
  - Right shift when held
  - T when tapped

### Dead Keys

- `=>` + `a` => accented a
- `=>` + `e` => accented e
- How about Dead Modifiers?
