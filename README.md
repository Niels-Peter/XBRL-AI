# XBRL-AI

The purpuse off this project is to apply XBRL in AI and Machine learning, by usage of Python.

The project will be divided into 3 parts:
1. Generic XBRL to AI.
  * xbrl_ai.py
2. XBRL in Danish GAAP og Danish IFRS (with extension) to AI
  * xbrl_ai_dk.py
3. Sample of Machine Learning implementation based on this project
  * test_xbrl_ai_dk.py

## Why this project?

Working with machine learning basicly comes down to one thing: y = f(X), y is what we want to predict, X is the input and f is the machine learning model. Unfortunately X hardly ever fits into to f. If we want to fit e.g. an XBRL-instance into to f, we need to prepare the data. XBRL needs a good representation to fit into AI and Machine learning.

Creating a good and standardized representation of XBRL into AI and Machine learning are the main purpose of this project.

## Getting started

To see an example of how one could use xbrl-ai start by creating a conda environment from the cloned yaml file:
```
>> conda env create -f environment.yml
```
now activate the environment by using
```
>> activate xbrl_ai
```
for windows, or
```
>> source activate xbrl_ai
```
for linux.

You can now run the test_xbrl_ai_dk.py.
