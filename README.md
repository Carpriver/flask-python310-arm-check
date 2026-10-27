# Flask Python 3.10 on Windows ARM64

## Verified result

The first complete manual run passed on 2026-10-27: [Windows ARM verification #1](https://github.com/Carpriver/flask-python310-arm-check/actions/runs/40480968516), tested commit `651c9188b517361fb53409127611f95525f08dd3`.
The host was Windows 11 Enterprise on Cobalt 100 ARM64, not a Snapdragon laptop. Python 3.10.20/Flask 2.3.2 setup, checks, generated VS Code defaults, terminal activation, real loopback HTTP, and preservation of the original x64 Python 3.14/base package records all passed.
The later diagnostic-only enhancement prints whether the detected Miniconda executable is x64, ARM64, or x86. This enhancement was additionally tested on the teacher's x64 PC; it was not part of run #1. Device policy and graphical VS Code selection remain outside the automated test.

Public, minimal verification sources for adding a separate Python 3.10 classroom environment while retaining Python 3.14.
No textbook content, student data, local teacher diagnostics, or credentials are included.

## Manual verification

Open **Actions → Windows ARM - Flask Python 3.10 → Run workflow**.

The workflow uses the standard `windows-11-arm` runner, has a 30-minute timeout, runs only when manually requested, and does not upload artifacts or use Actions caches.

It installs a pinned official Windows x64 Miniconda installer after checking SHA256 and its Windows signature.
The ARM64 host executes x64 Python via Windows emulation. It then runs the distributed preflight, setup, dependency-check, and VS Code configuration batches.

Target environment: `C:\conda-envs\flask_python310` (Python 3.10.20, Flask 2.3.2 and fixed dependencies).
Project folder: `C:\work_flask`.

Checks include fixed package versions, Flask HTTP responses, in-memory SQLite/ORM, form validation, generated terminal activation, and preservation of the original Python 3.14/base package records.

This does not test school Device Guard rules, school device write permissions, or graphical VS Code interpreter selection. The scripts do not issue a channel-terms acceptance command. In run #1, Conda itself detected the CI context and logged acceptance of three channel terms. Student PCs must follow the school's process for reviewing applicable Anaconda terms.

The `CLASS_CI=1` environment variable suppresses only interactive `pause` commands in the batches. The same setup/check/configuration operations are used locally.

Passing this workflow is evidence for this Windows ARM runner image, not a guarantee for every Snapdragon device or every chapter of a textbook.
