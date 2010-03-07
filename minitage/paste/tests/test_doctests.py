#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
"""
Launching all doctests in a specific directory with globals and setup enhancement


Lot of files generated by the collective.generic packages  will try to load user defined objects in user specific files.
The final goal is to regenerate easyly the test infrastructure on templates updates without impacting
user-specific test boilerplate.
We do not use paster local commands (insert/update) as it cannot determine witch is specific or not and we prefer to totally
separe generated stuff and what is user specific



If you need to edit something in this file, you must have better to do it in:


    - user_testcase.py
    - user_utils.py
    - user_globals.py


Objects that you can edit and get things overidden are:


    - minitage.paste.tests.user_testcase:

        * method: setUp

            Default tearDown function

        * method: tearDown
            Default setUp function

        * class:  DocTestCase

            Default Zope2 testCase class

    - minitage.paste.tests.user_utils:

        utilities functions to register as a global in tests

    - minitage.paste.tests.user_globals:

        Any variable added in there will be available in relative tests as a global
        Example:
        # Add in user_globals.py
        from for import bar
        and in your doctests, you can do without importing bar:
        >>> bar.something


"""
################################################################################


import re
import unittest
import doctest
import os.path

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# UTILITIES AND GLOBBALS SUPPORT / EDIT .user_utils.py or .user.globals.py to overidde
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# if you have plone.reload out there add an helper to use in doctests while programming
# just use preload(module) in pdb :)
# it would be neccessary for you to precise each module to reload, this method is also not recursive.
# eg: (pdb) from foo import bar;preload(bar)
# see utils.py for details

from minitage.paste.tests.globals import *
try:from minitage.paste.tests.user_globals import *
except:pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# setUp/tearDown in a non-Zope2 environement / EDIT .user_testcase.{setUp, tearDown} to overidde
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def setUp(test):pass
def tearDown(test):pass
try:from minitage.paste.tests.user_testcase import setUp
except:pass
try:from minitage.paste.tests.user_testcase import tearDown
except:pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ZOPE2 SPEFICIC / EDIT .user_testcase.DocTestCase to overidde
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
HAS_ZOPE2 = False
DocTestCase = None
try:
    from Testing import ZopeTestCase as ztc
    HAS_ZOPE2 = True
    # try to import a default testcase which looks like
    try:
        from minitage.paste.tests.user_testcase import DocTestCase
    except:pass
    #       from Testing import ZopeTestCase as ztc
    #       class DocTestCase(ztc.DocTestCase):
    #           """Base functional doctestcase
    #           Think that you have a reference to the tested file in self.testref
    #           This class is only useful in a Zope2 environment as the
    #           test_class comes from the ZopeTestCase product.
    #           In other cases, please use the setUp and tearDown functions.
    #           """
    #           def setUp(self):
    #               """."""
    #               TestCase.setUp(self)
    #           def tearDown(self):
    #               """."""
except ImportError:
    pass

doctest_flags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

reflags = re.M|re.U|re.S
def testfilter(patterns,
               filename):
    for pattern in patterns:
        if re.search(pattern, filename, reflags):
            return True
    return False



def test_doctests_suite(directory=__file__,
                        files = None,
                        patterns = None,
                        globs=None,
                        suite=None,
                        testklass=None,
                        doctest_options = doctest_flags,
                        lsetUp=None, ltearDown=None
                       ):
    """A doctest suite launcher.
    You can even launch doctests from others packages with the
    paste setup with embedding this test suite
    You can even add others globals in those tests.
    No need to copy and duplicate this file, it is useless.

      #Example : This snippet will launch all txt doctests in the other package directory
      >>> from minitage.paste.tests.test_setup import test_doctests_suite as ts
      >>> def test_suite():
      ...     globs = globals()
      ...     return ts(__file__, globs)

    directory: where to find files to test
    globs: A dictionnary to setup test globals from.
    directory: directory or filename where to run the tests
    files: files to include
    pattern: pattern for tests inclusion in the suite
    suite: a TestSuite object
    testklass: only useful if you are inside a Zope2 environment, because ztc comes from there.
               Note that in this case, setUp and tearDown are useless.
    Indeed modern application relys more on the setUp and tearDown functions.
    tearDown: tearDown code to run
    setUp: setUp code to run
    """
    _f = None
    if not patterns:
        patterns = ['.txt$']
    if not directory or os.path.isfile(directory):
        directory, _f = os.path.split(os.path.abspath(directory))
    elif os.path.isfile(directory):
        directory = os.path.dirname(directory)
    if not globs: globs={}
    g = globals()
    for key in g: globs.setdefault(key, g[key])
    if not files:
        files = [os.path.join(directory, f)
                 for f in os.listdir(directory)
                 if testfilter(patterns, f)]
    else:
        for i, f in enumerate(files[:]):
            if not os.path.sep in f:
                files[i] = os.path.abspath(os.path.join(directory, f))
            else:
                files[i] = os.path.abspath(f)

    if not suite: suite = unittest.TestSuite()
    if files:
        for test in files:
            ft = None
            if HAS_ZOPE2:
                if not testklass: testklass=DocTestCase
                ft = ztc.FunctionalDocFileSuite(
                    test,
                    test_class=testklass,
                    optionflags=doctest_options,
                    globs=globs,
                    module_relative = False,
                )
            else:
                from minitage.paste.tests.test_doctests import setUp, tearDown
                if lsetUp:
                    setUp=lsetUp
                if ltearDown:
                    tearDown=ltearDown
                ft = doctest.DocFileSuite(
                    test,
                    optionflags=doctest_options,
                    globs=globs,
                    setUp=setUp,
                    tearDown=tearDown,
                    module_relative = False,
                )
            if ft: suite.addTest(ft)
    return suite

def test_suite():
    """."""
    suite = unittest.TestSuite()
    return test_doctests_suite(suite=suite)

# vim:set ft=python:
