# Stockalyzer
## General purpose stock analysis toolbox

Stockalyzer is meant as a general tool for analyzing stocks. Underlying implementation is built on yfinance library that works as a wrapper to access financial data from the Yahoo Finance website. By basic analysis we can make usable and easily digestible conclusions on the health of the company. 

Fundamentally, the software is built on Pandas, Numpy and Matplotlib. It (should eventually) provide both a web based UI using the Django framework and a command line interface for easy debugging. Additionally, some heavy duty computations like numerical option pricing utilize my mathlib library written in C++.

Note! This is just a hobby project. All rights are reserved and the results of the computations are NOT financial advice.
