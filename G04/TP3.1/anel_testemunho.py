# /// script
# dependencies = ["marimo", "z3-solver"]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo


if __name__ == "__main__":
    app.run()
