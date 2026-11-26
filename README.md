# wichteln

[![Open the web app](https://img.shields.io/badge/🎁_Open_the_web_app-jakmannob.github.io%2Fwichteln-b3261e?style=for-the-badge)](https://jakmannob.github.io/wichteln/)

A small tool to help with the generation of a secret santa (german "Wichteln") mapping

**Just want to draw names? Use the [web app](https://jakmannob.github.io/wichteln/), no installation needed, entirely local and private within your browser.**

## How it works

This tool will turn a list of $`n`$ names of participants into $`n`$ different files
that are named after a participant and contain the respective participants
secret santa target.
You can include comments in the input file with hashes (`#`).
You can select whether you want the output files to be `PDF` or simple text files.

To make sure that no one draws their own name, we use a cyclic permutation over
the input names by default. If you want to e.g. have 24 participants into 4
groups of 6 participants each, you can also specify the cycles of your desired
permutation.

## Web version

The [web app](https://jakmannob.github.io/wichteln/) (`docs/index.html`) is a static
page with the same functionality that runs fully in the browser and downloads all files as a ZIP. To host it, enable GitHub Pages in the
repository settings with source "Deploy from a branch", branch `main`, folder `/docs`.

## How to use it

See all available options:

```sh
$ python wichteln.py --help
```

Then run with your desired options.

## Custom permutations

You can give the program a list of tuples specifying the cycles of the permutation.
The first entry of the tuple is the size of the cycle and the second is the count
of how often such a cycle is in the permutation.
If one of these is $`-1`$, it will be assumed.
Examples:

- `(-1,1)`: The default will create one cycle with all participants in it
- `(-1,2)`: This will split all participants into two cycles as evenly as possible
    (e.g. 7 participants become one 4-cycle and one 3-cycle)
- `(3,1),(4,-1)`: One cycle of 3 participants, the rest will be 4-cycles. Will raise
    an exception if there exists no $`k`$, s.t. $`n = 3+4{\cdot}k`$
