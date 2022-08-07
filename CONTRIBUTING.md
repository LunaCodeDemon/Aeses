# Contribution Guidelines

These are certain guidelines that are used to keep the repository 
structured in a uniform and ordered manner.
Every sentence matters in has the goal to improve the experience gained by contributing.
These aren't rules, so use your best judgement to send some nice pull requests.

## Unit testing
Feel free to add unit tests for your code or those of others. 
I am always happy to see some tests complete successfully.
Tests make me feel safe, but i also know that not everything in here can be tested with unit tests.

## Explain your progress
Of course it's not necessary to describe every line, but it is nice to know what you did.

You can just make a small list mentioning what features are new and what files are used for it.

## Coding conventions
Since I do not use any formatting tools I should explain how my code is written.

- I use 4 space indents.
- **Always** put spaces after a comma (`[1, 5, 4]`)
- I use type hinting to make clear what a function takes and returns.
- Normal strings are with double quotes and keys are with single quotes. (`arr['hello'] = "world"`) 

*Tip: use pylint to check, on your pull request pylint will run over all the code.*