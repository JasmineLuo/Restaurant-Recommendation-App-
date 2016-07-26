# D5 Web App

This repository contains the web interface and the database operation
of our recommender application.

## Dependency

- Python 2.7
- Flask (bundled with Python)
- Jinja2 (bundled with Flask)
- MySQL Python Driver??
- TODO

## Front End Design Schema

Core principles:
- mobile first, responsive page layout
- No create, update, delete via HTTP GET

App sitemap
- route("/")
  - welcome page (picture)
  - sign up button
  - log in button
- route("/dashboard")
  - my info (with button to update)
  - fire new proposal
  - view matched proposal
  - view friends circle

**TODO**

## Back End Design Schema

**TODO**

