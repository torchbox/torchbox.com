## Motif heading

- The motif heading is used in conjunction with a drop cap title class that animates the first letter of the heading.
- The current heading classes are `motif-heading--one`, `motif-heading--one-b` and `motif-heading--two`.
- It can optinally accept a heading level value but this does not automatically change the heading class - classes need to be added manually.
- There is no animation on the heading if the user has opted for reduced motion.
- To achieve the animation the fist letter is wrapped in a span.
- To avoid issues when announcing the heading to screen readers the heading has an aria-label that is the same as the text content of the heading.
