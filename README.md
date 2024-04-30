# Megano
It is a plug-in django application. 
It takes care of everything related to the selection of pages, and the data is accessed via the API.

## This website contains functions such as:
1) Registration and authorization of users
2) Create an order and a shopping cart, including an unregistered user's shopping cart
3) Website management via the admin dashboard
4) Product search and filtering
5) Viewing and editing a profile
6) The ability to leave comments
7) Payment
8) Uploading and downloading files on the website

## API Contract
The names of the routes and the expected response structure from the endpoints API can be found in diploma-frontend/swagger/swagger.yaml.

## Frontend
Vue3 was used as the frontend framework, which is connected in the basic template templates/frontend/base.html:
JS script static/frontend/assets/js/app.js contains the implementation of the Vue object, and all other JS scripts from the static/frontend/assets/js directory implement the impurity objects for the corresponding project page.

## Installation
1. Clone the repository from GitHub
2. In the main directory, run the command: docker compose build app
3. In the main directory, run the command: docker compose up app
4. Create superuser with command: python manage.py createsuperuser
5. Enter login und password for admin
6. If you start the development server: python manage.py runserver, then the start page of the online store should open at 127.0.0.1:8000
7. Enjoy)
