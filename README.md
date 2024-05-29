### Instructions

#### Set up

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export GITHUB_TOKEN="..."
export FRESHDESK_TOKEN="..."
```

#### Run the program

```
python main.py <github_username> <freshdesk_subdomain>
```

#### Run the tests

```
python -m unittest
```
