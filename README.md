# Menu Maker

![Coverage Badge](/assets/img/coverage.svg "Coverage Badge")

<strong><h3>Note: This project is currently usable as a proof-of-concept for an API that allows for the reliable creation of restaurants, menus, menu items, etc. It can be used to make a working menu with a minimalist design that includes pretty pictures.</h3></strong>

<strong>Current Status:</strong> Backend Web/API CRUD systems both working and tested.


### About

Menu Maker is a project that showcases my understanding of best practices using Python, Django and Git. In short, it is a simple CRUD app that highlights Django's utility as a web-first framework, onto which other functionality can be added as needed.


### Who is this for?

It is intended to serve as a reference guide for best practices when making a basic CRUD app using Django. Only the code needed to perform the desired task is used. There is no useless boilerplate or filler. All code in this repo has been created for this project and nothing has been copy-pasted.

The primary goal of this app is to serve as a personal reference for how best to perform common tasks using Django. (At least, from my always-learning perspective. Opinions and pull requests are welcome :)

If you are a restaurant owner who needs to make a menu, this service probably isn't the best tool available (There are probably a lot of options out there with more polish). If, however, this app does what you need, you are free to take the software and do whatever you want with it. All I ask is that you credit me, and let me know if this software helps you out at all. This software is CC licensed (see link at the bottom of this README).


### What does Menu Maker do?

This project allows restaurant owners to register their restaurant and create a customized menu. Then, customers can easily view the restaurant's offerings from a desktop or mobile device.


### What software is used in this project?

This app is made using Python 3.8.6 and Django 3.1.2, and 

This app makes use of the following Python practices and modules:
- Follows the Python PEP8 style guide (linted using flake8)
- Uses Coverage module to ensure all sections of the code has been tested

Menu Maker makes use of many of Django's features:

- Django's built-in ORM:
    - This project uses SQLite for maximum portability and ease of setup
- Whenever possible, Class-Based Views (CBVs) are used, in order to take advantage of the features that are built into Django's CBVs (e.g. easy paging).
- Django's built-in test runner:
    - To the best of my knowledge, all statements in the code have been properly tested (Coverage is currently at 99%).
    - Due to how Python's Coverage module detects code coverage, the number is a bit short of 100%. My goal is not to ensure that the badge says 100%, but to ensure that the codebase is fully tested (to a reasonable degree).
    - All efforts have been made to ensure that the tests cover all expected circumstances.

This project also represents an effort to implement proper Git best practices, including:

- Small, incremental ("atomic") commits
- Concise, useful descriptions of each commit

<br>
<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="margin-left: auto; margin-right: auto; border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a>

This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
