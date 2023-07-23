# Evaluation Platform for MTIL(Machine Translation for Indian Languages)

A Evaluation Platform for the [MTIL](https://mtilfire.github.io/mtil/2023/index.html) track under [FIRE](http://fire.irsi.res.in/fire/2023/home) (Forum for Information Retrieval Evaluation)

## Installation

Follow the steps to install the project on your local machine

Step 1: Create a virtual environment and activate it

```bash
python -m venv your-env-name
```

Step 2: Install Required Dependencies

```bash
pip install -r requirement.txt
```

Step 3: Create a new file named `.env` and copy the content from `.env_sample`

Step 4: Create a mysql database and update the `.env` accordingly

Step 5: Find the database dump in the repo and query to create the DB schema

Step 6: Run the following command to start the server

```bash
uvicorn main:app --reload
```

## Endpoints

* All the Endpoints links can be found at [swagger docs](http://localhost:8000/docs)
* [postman](https://api.postman.com/collections/15333643-c85f704f-0d15-4d46-b725-d38b495aeb7c?access_key=PMAT-01H602RYKW8NNDMYK2XH46S5P5) Collection


## TODO

* [ ] Auth

  * [X] signup
  * [X] signin
  * [ ] signout
* [X] profile

  * [X] view profile
  * [X] update profile
* [X] Create Team

  * [ ] send Invitation Mail
* [ ] Evaluation

  * [ ] Upload Submission file
  * [ ] Calculate BLUE, CHRF++, CHRF, TER Score
* [ ] Leaderboard

  * [ ] Public Leaderboard
  * [ ] Different leaderboard for different language pair
  * [ ] One can submit maximum of 3 submissions
  * [ ] Private leaderboard in the user's dashboard
