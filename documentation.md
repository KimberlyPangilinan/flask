# Recommendation System API Documentation

This documentation provides an overview of the endpoints and functionality of the Recommendation System API.

## Introduction

The Recommendation System API is designed to provide recommendations based on user interactions and text analysis. It uses cosine similarity to recommend articles that are similar to those previously read by the user.

## Endpoints
1. Get Articles

    - Endpoint: `/articles`
    - Methods: `GET`
    - Description: Get a list of articles.

2. Search Articles

    - Endpoint: `/articles/search`
    - Methods: `GET`
    - Description: Search articles based on specified criteria.
    - Parameters:
        `dates` (list): `List of date ranges`.
        `journal` (string): `Journal name`.
        `input` (string): `Keywords for search`.


3. Insert to read logs and Get Recommendations Based on Selected Article

    - Endpoint: `/articles/logs/read`
    - Methods: `POST`
    - Description: Get article recommendations based on the current article.
    - Request Format: JSON

    ```json
    {
        "article_id": 1,
        "author_id": 123
    }
    ```
3. Insert to logs as downloads

    - Endpoint: `/articles/logs/download`
    - Methods: `POST`
    - Description: Insert to logs as article download
    - Request Format: JSON

    ```json
    {
        "article_id": 1,
        "author_id": 123
    }
    ```


4. Get Recommendations Based on Read Historyand get History

    - Endpoint: `/articles/recommendations/<int:author_id>`
    - Methods: `GET`
    - Description: Get personalized recommendations based on the user's read history.


5. Get Recommendations based on popularity of user interactions
    - Endpoint: `/articles/recommendations`
    - Methods: `GET`
    - Description: Get personalized recommendations based on the user's read history.
    - Request Format: JSON

    ```json
    {
        "period": "weekly" //weekly or monthly
    }
    ```


## Technologies Used

- Flask: The web framework for building the API.
- scikit-learn: Used for cosine similarity calculations.
- NLTK: Used for text preprocessing.
- MySQL: The database used for storing article and user dat
