# -*- coding: utf-8 -*-

"""Build script.
"""

# Environment info
config.project        = 'django-flash'
config.virtualenv_dir = '~/.virtualenvs'

# Information needed to build the documentation
config.sphinx_output = 'build/sphinx'
config.sphinx_latex  = '%s/latex' % config.sphinx_output
config.sphinx_html   = '%s/html' % config.sphinx_output
config.doc_output    = 'djangoflash'

# Host where the documentation website lives
config.fab_hosts  = ['destaquenet.com']
config.doc_folder = '/home/destaquenet/public_html'

# TODO Add version 2.4 to the list below!
# TODO To make it work, I should install pysqlite2

# Supported Python versions
config.versions = ('-py2.5', '')


def setup(command, version=''):
     """Executes a setup command with a virtual Python installation.
     """
     local('%s/%s%s/bin/python setup.py %s' % (config.virtualenv_dir, config.project, version, command))

def test():
    """Runs all tests in different Python versions.
    """
    for version in config.versions:
        python('test', version)

def clear_sphinx():
    """Removes the Sphinx build directory.
    """
    local('rm -R ' + config.sphinx_output)

@depends(clear_sphinx)
def build_docs():
    """Builds the documentation, both in PDF and HTML.
    """
    setup('build_sphinx')
    setup('build_sphinx -b latex')
    local('make -C ' + config.sphinx_latex)

@depends(build_docs)
def zip_docs():
    """Creates a zip file with the whole documentation.
    """
    # Compile the Latex-based documentation to a PDF file
    local('cp %s/%s.pdf %s' % (config.sphinx_latex, config.project, config.sphinx_html))

    # Create a zip file with the complete documentation
    local('cd %s; mv html %s; zip -r9 %s.zip %s' % ((config.sphinx_output,) + (config.doc_output,)*3))

def register_pypi():
    """Register the current version on PyPI.
    """
    setup('register')

def deploy_src():
    """Deploy the source code to PyPI.
    """
    setup('sdist upload')

def deploy_eggs():
    """Upload Python Eggs to PyPI.
    """
    for version in config.versions:
        setup('bdist_egg upload', version)

@depends(register_pypi, deploy_src, deploy_eggs)
def deploy_pypi():
    """Deploy Django-flash to PyPI.
    """
    pass

@depends(zip_docs)
def deploy_website():
    """Deploy Django-flash website.
    """
    put('%s/%s.zip' % (config.sphinx_output, config.doc_output), config.doc_folder)
    run('cd %s; rm -R %s; unzip %s.zip; rm %s.zip' % ((config.doc_folder,) + (config.doc_output,)*3))

@depends(deploy_pypi, deploy_website)
def deploy():
    """Perform the complete Django-flash deploy.
    """
    pass
