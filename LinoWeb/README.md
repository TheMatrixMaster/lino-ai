# linoMTL webapp

<p align="center" href="">
  Lino website for webscraping and classification of kijiji real estate offers.
</p>

This repo has been designed to be a friendly starter tutorial to using our real estate categoriation tool.

## Requirements

* Python 3.4+


## Installation
First, make sure you have the necessary dependencies.

```python
pip install -r requirements.txt
```

### Getting Started

First you need to set the environment variables for FLASK_APP and FLASK_ENV 

On windows:
```
set FLASK_APP=src
set FLASK_ENV=development
```
On linux/ubuntu
```
export FLASK_APP=src
export FLASK_ENV=development
```

To run server on localhost:5000/
```
flask run
```
or 
```
python -m flask run
```

Please make sure all modules are installed and add any missing modules by doing:
```
pip install <module name>
```
