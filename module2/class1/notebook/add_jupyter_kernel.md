### Create the virtual environment
```
uv sync
```
### Register the kernel
```
uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=m2-c1-notebook --display-name "M2 C1 Notebook"
```
