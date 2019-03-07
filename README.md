# depend-test-framework

[![Build Status](https://travis-ci.org/LuyaoHuang/depend-test-framework.svg?branch=master)](https://travis-ci.org/LuyaoHuang/depend-test-framework)

A case generator tool to help generate cases base on logic unit. This tools help users to generate test cases as more as possible and sort generated cases via Deep Learning.

Features
--

1. Support generate test cases base on template and test units
2. Use Deep Learning (LSTM) to sort generated cases to make the generator more suit for different use case
3. Have a light test framework to run generate cases
4. Support generate manual test cases and map to auto cases

Installing
--

You need install pip first and then run:

    git clone https://github.com/LuyaoHuang/depend-test-framework
    cd depend-test-framework/
    pip install -r requirements.txt
    python setup.py install

Unit test & Syntax check
--

To run unit test, use:

    python setup.py test

And syntax check, use:

    python setup.py syntax_check
