# Recommendation System API Documentation

This documentation provides an overview of the endpoints and functionality of the Recommendation System API.

## Introduction

The Recommendation System API is designed to provide recommendations based on user interactions and text analysis. It uses cosine similarity to recommend articles that are similar to those previously read by the user.

## Endpoints

### 1. Get All Articles

This endpoint allows you to retrieve articles by their titles.

- **URL:** `/articles`
- **Method:** GET
- **Response:**
  - JSON object containing all articles.
### 2. Get Articles by Title

This endpoint allows you to retrieve articles by their titles.

- **URL:** `/articles/<string:articleTitle>`
- **Method:** GET
- **Parameters:**
  - `articleTitle` (string): The title of the article to search for.
- **Response:**
  - JSON object containing article data matching the search title all title that contains the keyword.

### 3. Recommend MySQL Articles

This endpoint enables you to receive article recommendations based on user interactions.

- **URL:** `/articles`
- **Methods:** POST (to add user interactions) and GET (to retrieve a list of articles).
- **Parameters (POST method):**
  - `article_id` (int): The ID of the article the user interacted with.
  - `author_id` (int): The ID of the user.
- **Response (POST method):**
  - JSON object containing a message and article recommendations.
- **Response (GET method):**
  - JSON object containing a list of articles.


### 4. Recommend Articles Based on User History

This endpoint provides personalized recommendations based on a user's reading history.

- **URL:** `/articles/history/<int:author_id>`
- **Method:** GET
- **Parameters:**
  - `author_id` (int): The ID of the user for whom personalized recommendations are requested.
- **Response:**
  - JSON object containing personalized recommendations, user history, and user ID.

## Sample Usage

Here's an example of how to use the Recommendation System API:

1. To retrieve all articles:
   - Send a GET request to `/articles`.
   - ```
     https://web-production-9662.up.railway.app/articles ## GET
     ```
     ![image](https://github.com/KimberlyPangilinan/qoaj-recommendation-api/assets/92774426/b3649c03-0d61-4af5-9325-a9ee58cb603d)

1. To retrieve articles by title:
   - Send a GET request to `/articles/<articleTitle>`.
   - ```
     https://web-production-9662.up.railway.app/articles/gender ## GET
     ```
     ![image](https://github.com/KimberlyPangilinan/qoaj-recommendation-api/assets/92774426/53a29c4a-b022-41c1-8809-8a0e6b972bc0)

2. To recommend articles and save user interactions:
   - Send a POST request to `/articles` with the JSON payload containing `article_id` and `author_id`.
   - ```
     https://web-production-9662.up.railway.app/articles ## POST
     {
       "article_id": 20,
       "author_id":2
     }
     ```
  ![image](https://github.com/KimberlyPangilinan/qoaj-recommendation-api/assets/92774426/b71b0869-89d3-4f5f-a4d9-306758eea994)

3. To receive personalized recommendations based on user history:
   - Send a GET request to `/articles/history/<author_id>`.
   - ```
     https://web-production-9662.up.railway.app/articles/history/2  ## GET
     ```
  ![image](https://github.com/KimberlyPangilinan/qoaj-recommendation-api/assets/92774426/ca97533f-e493-4286-abe6-07e5921dc59e)

## Technologies Used

- Flask: The web framework for building the API.
- scikit-learn: Used for cosine similarity calculations.
- NLTK: Used for text preprocessing.
- MySQL: The database used for storing article and user dat
