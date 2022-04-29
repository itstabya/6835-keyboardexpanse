# Keyboard Expanse

## Setup

- Mirrored Setup
    - Bottom of the screen ("when flipped") should match up with the top row of keyboard commands.

## Installation

- Requires Python3.8, use pyenv to install custom version if necessary

## Linux may require root

```
sudo -E env PATH=$PATH python3 -m keyboardexpanse
```

## Concepts

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