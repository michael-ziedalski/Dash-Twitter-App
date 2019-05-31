# Dash-Twitter-App

## Overview

This is a Twitter app built in Python using the Dash framework, https://plot.ly/products/dash, it is meant to simply visualize users' tweets and display the distributions of their sentiment scores. Whenever any user's tweets are requested, a streaming API is utilized to also open a stream and listen for any new tweets, which will be displayed as they come in.

The Dash-Twitter-App is mostly a humble exercise in clean data visualization.

## Installation

To run it, install all of the required libraries within `requirements.txt`, and just run `python main_code.py` from the project's folder.

## Usage

The controls are intuitive: enter the twitter usernames separated by commas, and wait for the table and graph to populate. Changing the tweet sources, or any of the other settings, first requires that the stream be paused. 

If nothing happens, check the console for any errors, such as having inputted a non-existent twitter handle.

## Current limitations

The free Twitter API in use has generally common-sense network restrictions, so if too many requests are made in too short a time, Twitter may start sending 404's in retaliation for the unsolicited bombardment. In addition, too many twitter handles or tweets cannot be requested all at once.

Hope you enjoy!
