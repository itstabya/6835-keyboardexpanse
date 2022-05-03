<div align="center">
<img src="https://user-images.githubusercontent.com/10828202/166475106-f2d31006-6d54-4d60-a44b-0626de2778ca.png" width="40%"/>
</div>

<h1 align="center">
  <strong>Keyboard</strong> Expanse
</h1>

Switching back between the keyboard and mouse not only breaks you from the flow, but also wastes time. Keyboard shortcuts are great; but they’re also a pain to learn, require awkward control sequences.

<div align="center">
    
![Screenshot_from_2022-05-03_10-34-45-removebg-preview](https://user-images.githubusercontent.com/10828202/166475758-57fd0b3e-24cc-4731-ae91-3103a3af9555.png)
</div>

Keyboard Expanse is all about keeping your hands on your keyboard; but expanding the interactable surface from simple button presses.

1. **Grounded Location**: Minimises gestural fatigue
2. **Subtle Events**: No large, artificial movements required.
3. **No "wake"-command**: Allows keyboard-shortcut level speed.
4. **Concrete metaphors** related to real-world experiences: To go left you point left; to minimise you swipe the window away; to change desktop you move along the keyboard.
5. **Works alongside Keyboard Shortcuts**: Keyboard shortcuts still have a place in this system: Copy + Paste are both ubiquitous, well-known and have no quick facsimile in gestural space.

## :wrench: Technology

Python, MediaPipe, OpenCV, Plover, Pandas/Numpy, Autopy, (FFMPEG, Seaborn)

## :gear: Installation

### Physical
- Mirrored Setup
    - Bottom of the screen ("when flipped") should match up with the top row of keyboard commands.

## Software

- Requires Python3.8 (due to autopy dependency), use pyenv to install custom version if necessary

## :zap: Running

```
python3 -m keyboardexpanse
```

## Linux may require root

```
sudo -E env PATH=$PATH python3 -m keyboardexpanse
```

## :sunglasses: Acknowledgements & Prior Work

- The entire [oslayer](./keyboardexpanse/oslayer) is taken from [Plover](https://github.com/openstenoproject/plover) - the open source stenotype engine - (with some minor modifications).
- The MediaPipe Library does much of the heavy lifting for gesture detection by providing Realtime Landmarks.
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


### Tap+Touch
![Tap+Touch](https://user-images.githubusercontent.com/10828202/166473601-75f7ab45-509a-4f2d-b159-266e519bb5ea.gif)

### Swipe Commands
![Swipe](https://user-images.githubusercontent.com/10828202/166473663-ebf38960-2478-45e6-9267-bdcee09e65c8.gif)



### Future

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

- ``` => ``` + `a` => accented a
- ``` => ``` + `e` => accented e
- How about Dead Modifiers?
