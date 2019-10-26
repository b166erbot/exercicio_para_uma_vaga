coverage erase
isort -sp src -y
echo
coverage run --source=src -m unittest discover -s tests
echo
coverage html
coverage report
echo
radon cc -as src
echo
pep257 --match='.*(?<!__init__).py' src
echo
pycodestyle src tests

echo
echo para uma melhor visualização da cobertura, abra o arquivo htmlcov/index.html
