# Islamic Star Pattern Generator

## Repository

https://github.com/maryam7513/islamic-star-pattern-generator

## Description

A program that will generate star patterns similar to what is
common in the Islamic world.

## Features
- Pattern generation
    - This will mostly be with something like Kaplan's
      algorithm.
- Image output
	- Using `pillow` to output the pattern to an image,
      which could be used as a texture.
- (Possible, no gurantee) GUI
	- GUI allowing live-preview, perhaps using something
      like pygame.

## Challenges
- Performance, especially with larger patterns
- Generating tilings completely from scratch

## Outcomes
Ideally, we'd have a GUI that allows adjusting various
parameters, with a live view of the final pattern.

Minimal Viable Outcome:
The bare essential in my opinion would be a command-line
tool that is easy to use.

## Milestones

- Week 1
  1. Proof of concept for star generation.
  2. One tiling set of regular polygons,
     maybe two or three.

- Week 2
  1. Add more tilings for star pattern
     generation.
  2. Maybe a basic proof of concept for
     a live preview.

- Week 3 (Final)
  1. Add even more tilings.
  2. If possible, a fully functional GUI,
     but this will depend on how far we
     get in week 2.
