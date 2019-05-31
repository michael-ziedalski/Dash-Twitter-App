# Dash-Twitter-App

## Overview

This is a Twitter app built in Python using the Dash framework, https://plot.ly/products/dash, it is meant to simply visualize users' tweets and display the distributions of all their sentiment scores. It is mostly an exercise in clean data visualization and building an app.

## Installation

To run it oneself, install all of the required libraries within `requirements.txt`, and just run `python main_code.py` from this project's folder.

## Usage

The controls are intuitive: enter the twitter usernames separated by commas, and wait for the table and graph to populate. Changing the tweet sources or any of the other settings first requires that the stream be paused. 

If nothing happens, check the console for any errors, such as having inputted a non-existent twitter handle.

## Current limitations

The free Twitter API in use has common-sense network restrictions, so if too many requests are made in too short a time, Twitter may start sending 404's in retaliation for the bombardment. In addition, too many twitter handles or tweets cannot be requested all at once.

Hope you enjoy!
