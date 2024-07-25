# RPA Challenge 3.0 - News Data Extraction Bot

## Description

This project is a solution for the RPA Challenge 3.0, which involves automating the process of extracting data from a news website. The solution was developed for the AP News site and uses the Robocorp library to automate navigation and information collection.

## Features

  - News Search: Automates the search for a specific term in news categories.
  - Data Extraction: Collects title, date, description, link, image URL, and counts the number of occurrences of a search phrase in the title and description.
  - Image Download: Downloads images associated with the news and saves them locally.
  - Storage: Stores the extracted data in an Excel file, including the image file path.

## Requirements

  - Python 3.8 or higher
  - Main Libraries: robocorp, beautifulsoup4, requests, pandas, uuid
  - Robocorp Cloud and Robocorp App Integration for execution and automation

## How to Use

Configure Robocorp to use the bot. Create a task in Robocloud and set the following parameters:

  - search_phrase: Search term for news.
  - news_category/section/topic: News category or section (optional).
  - number_of_months: Number of months to search for news (0 or 1 for the current month, 2 for the current and previous month, etc.).
  - Run the task in Robocloud.

After execution, you will find the Excel file RPAChallengeRobocorp.xlsx in the output folder, containing the extracted data. The downloaded images will also be available in the same folder.

## Contribution

Contributions are welcome! If you encounter any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.