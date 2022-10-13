# ku-polls
![Unittest Workflow](https://github.com/Siripa-Maneein/ku-polls/actions/workflows/python-app.yml/badge.svg)
[![codecov](https://codecov.io/gh/Siripa-Maneein/ku-polls/branch/main/graph/badge.svg?token=WL8RY9E0ZA)](https://codecov.io/gh/Siripa-Maneein/ku-polls)

## What ku-polls does
An application for conducting online polls and surveys based
on the [Django Tutorial project][django-tutorial], with
additional features.

App created as part of the [Individual Software Process](
https://cpske.github.io/ISP) course at Kasetsart University.

## How to Install

1. Clone this repository
```
git clone https://github.com/Siripa-Maneein/ku-polls.git
```
2. Move to ku-polls directory
```
cd ku-polls
```
3. Create virtual environment
```
python -m venv env
```

4. Start virtual environment in bash or zsh
```
. env/bin/activate
```

5. Install dependencies
```
pip install -r requirements.txt
```

6. Run migrations
```
python manage.py migrate
```

7. Install data from data fixtures
```
python manage.py loaddata data/polls.json data/users.json
```

8. Create .env file following the instructions in sample.env


## How to run
1. Make sure to activate virtual environment 
```
. env/bin/activate
```

2. Run the below command in your cloned directory
```
python manage.py runserver
```

3. Visit the following url
```
http://localhost:8000/polls/
```

## Demo Users
| Username  | Password  |
|-----------|-----------|
|   harry   | hackme22 |
|   jerry   | tomnjerry22 |

## Project Documents

All project documents are in the [Project Wiki](../../wiki/Home)

- [Vision Statement](../../wiki/Vision%20Statement)
- [Requirements](../../wiki/Requirements)
- [Project Plan](../../wiki/Development%20Plan)
- [Iteration 1 Plan](../../wiki/Iteration%201%20Plan) and [Task Board](https://github.com/users/Siripa-Maneein/projects/7/views/1?layout=board) 
- [Iteration 2 Plan](../../wiki/Iteration%202%20Plan) and [Task Board](https://github.com/users/Siripa-Maneein/projects/7/views/5)
- [Iteration 3 Plan](../../wiki/Iteration%203%20Plan) and [Task Board](https://github.com/users/Siripa-Maneein/projects/7/views/7)
- [Iteration 4 Plan](../../wiki/Iteration%204%20Plan) and [Task Board](https://github.com/users/Siripa-Maneein/projects/7/views/8?layout=board)

[django-tutorial]: https://docs.djangoproject.com/en/4.1/intro/tutorial01/
