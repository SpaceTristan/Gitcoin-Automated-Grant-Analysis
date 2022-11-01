# Gitcoin-Automated-Grant-Analysis

## Description

This app performs analysis on the gitcoin grant data and application json files. The analysis includes reviews of mostly offchain data as well as a wallet validation to identify issues in submission validity. A score is assigned based on checks made using the address and the description. A higher number means higher need of scrutiny. Lower number means less red flags

## Application Analysis

The application analysis script analyzes the grant applications and is intended to provide an automated mechanism to identify applications with potential data issues. 

## Grant Analysis

The grant analysis script does analysis on the existing grants to identify existing issues with the data by reviewing the twitter, website and github repos for each project
