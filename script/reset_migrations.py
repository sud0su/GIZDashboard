from subprocess import call

call('find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf', shell=True)
call('find . -path "*/migrations/*.py" -not -name "__init__.py" -delete', shell=True)
call('find . -path "*.sqlite3" -delete', shell=True)