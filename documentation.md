# Recommendation System API Documentation

This documentation provides an overview of the endpoints and functionality of the Recommendation System API.

## Introduction

The Recommendation System API is designed to provide recommendations based on user interactions and text analysis. It uses cosine similarity to recommend articles that are similar to those previously read by the user.

## Endpoints
1. Get Articles

    - Endpoint: `/articles`
    - Methods: `GET`
    - Description: Get a list of articles.
    - Response Format: JSON
    Example Response:

    ```json


    [
      {
          "abstract": "his paper assessed the effects of social iso...",
          "article_id": 4,
          "author": "Renielle S. Rogel",
          "author_id": 1,
          "content": "-",
          "date": "March 2023",
          "date_added": "0000-00-00 00:00:00",
          "journal_id": 1,
          "keyword": "social isolation, work satisfaction, stress, work productivity",
          "publication_date": "Sat, 04 Nov 2023 19:55:53 GMT",
          "references": "",
          "status": "1",
          "step": 0,
          "title": "The Effects of Social Isolation, Remote Work Satisfaction, and ..",
          "volume": "Volume 1"
      },
      
    ]
    ```

2. Search Articles

    - Endpoint: `/articles/search`
    - Methods: `GET`
    - Description: Search articles based on specified criteria.
    - Parameters:
        `dates` (list): `List of date ranges`.
        `journal` (string): `Journal name`.
        `input` (string): `Keywords for search`.
    - Response Format: JSON
    Example Response:

    ```json

   {
    "results": [
        {
            "article_contains": [
                "education",
                "online learning"
            ],
            "article_id": 13,
            "author": "Romar B. Reyes",
            "date": "March 2023",
            "keyword": "challenges, online learning, Covid-19 pandemic, laboratory teachers, implementation",
            "title": "Physical Plant and Instructional Support Facilities of Diocese of Imus Catholic Educational System (DICES), Inc. Schools"
        },
        {
            "article_contains": [
                "online learning"
            ],
            "article_id": 10,
            "author": "Donalyn Dizon, Rafael Tabunda, Josephine Uy",
            "date": "March 2023",
            "keyword": "speaking, video recording, oral communication, integration, online learning",
            "title": "A Classroom-based Action Research on Selected First Year Infor- mati...-2022"
        },
    ```

3. Get Recommendations Based on Current Article

    - Endpoint: `/articles/recommendations`
    - Methods: `POST`
    - Description: Get article recommendations based on the current article.
    - Request Format: JSON

    ```json
    {
        "article_id": 1,
        "author_id": 123
    }
    ```

Response Format: JSON
Example Response:

```json

{
    "message": "Successfully saved to read history.",
    "related_articles": [
        {
            "article_id": 20,
            "score": 0.2797474614474822,
            "title": "The Perspectives and Preferences of BSIT Students at Quezon City University in Online Learning"
        },
        {
            "article_id": 27,
            "score": 0.2603498525730653,
            "title": "A Discourse Analysis of Ableist Construction of Students with Disabilities in Mainstream Secondary Education"
        }
    ],
    "selected_article": [
        {
            "article_id": 16,
            "score": 0.9999999999999998,
            "title": "Course Preferences among Education Students"
        }
    ]
}
```

4. Get Recommendations Based on Read History

    - Endpoint: `/articles/recommendations/<int:author_id>`
    - Methods: `GET`
    - Description: Get personalized recommendations based on the user's read history.
   
    - Response Format: JSON
    Example Response:

    ```json

    {
        "history": [
            {
                "article_id": 16,
                "title": "Course Preferences among Education Students"
            }
        ],
        "personalized_recommendations": [
            {
                "article_id": 174,
                "score": 0.35056245106637396,
                "title": "Impact of Part-time Job on Academic Performance of 3rd Year College Student in Quezon City University"
            },
            {
                "article_id": 50,
                "score": 0.345049622029431,
                "title": "Gender Perspectives of Selected First year Students: An Exploratory Study"
            }
        ],
        "user_id": 1
    }
    ```


## Technologies Used

- Flask: The web framework for building the API.
- scikit-learn: Used for cosine similarity calculations.
- NLTK: Used for text preprocessing.
- MySQL: The database used for storing article and user dat
