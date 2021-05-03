# Random Dose of Knowledge

# [Visit the App!](http://rdok.net/)

## Read the [detailed blog](https://medium.com/p/1b504a1a2be4) post!

![GitHub Logo](/app/static/images/sample-app.png)

## Frameworks/Software/Technologies/Platforms used:
![GitHub Logo](/app/static/images/banner.png)

## You want to run the app locally by yourself

1. Clone the repository
```
git clone https://github.com/Deffro/random-dose-of-knowledge.git
```
2. Create a virtual environmental. For example with anaconda/miniconda
```
conda create -n rdok python=3.8
conda activate rdok
```
3. Install packages
```
pip install -r requirements.txt
```
4. Navigate to app/utils/reddit_api.py and change SECRET_KEY, CLIENT_ID, REDDIT_USERNAME, and REDDIT_PASSWORD to your own (line 63).
For the password, you have to create a pswd.txt inside the utils folder.

Done! Go to *localhost:8000* to see the app

## You also want to dockerize it

1. [Install](https://www.docker.com/get-started) docker.
2. Go to the directory where Dockerfile is
3. `docker build -t rdok:1.2 .` (don't forget the dot)
4. docker run --name rdok -d -p 80:8000 rdok:1.2

Done! Go to *localhost:80* or just *localhost* to see the app

## You also want to deploy it on AWS
I have written the process in full details [here](https://medium.com/p/1b504a1a2be4/).
