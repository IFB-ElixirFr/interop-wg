---
title: Self-assessment interface using FAIRMetrics
layout: template
filename: fm_demo
--- 

# Monitoring progress in FAIRification through self-assessment of resources maturity indicators

## Context and related works

The FAIR Evaluator framework [Wilkinson, Dumontier et al., Scientific Data 6:174] is composed of Maturity Indicators (MI), compliance tests and the evaluator application itself. The authors expect growing contributions in MI specifications and compliance tests to improve relevance and coverage of FAIR evaluation. They also propose that these tests should be carried out by third party organisations. 
In spite of many research contributions highlighting the potential benefits of FAIR principles for the research community and their potential impacts, few efforts have been done so far to take advantage from their concrete implementation, in the process of improving FAIRness of users/community resources. Early prototypes focus on publishing FAIRness metrics computed offline for predefined sets of public web accessible resources. However this does not provide concrete help to developers for better sharing their published works. 
In this work we propose a web demonstrator, leveraging existing web APIs, aimed at i) evaluating FAIR maturity indicators and ii) providing hints to progress in the FAIRification process. 

### FAIRMetrics

### Fair Maturity Indicators WG (RDA)

## Approach 

For now, we are willing to use the FAIRMetrics smartapi to create a simple interface and provide the user with an easy way to verify how FAIR is his resource.
We want to provide the user with clear informations on how to validate each aspect of the FAIR principles and help him to improve the FAIRness of his resource.

## Demonstration

The aim of this demonstration is to provide a typical usecase for this project idea.

### Step 1 - Resource generation

A researcher created a fresh new dataset and host it on the web, associated to a URL or DOI.

### Step 2 - How FAIR is the resource

The researcher want to have an idea of how FAIR is his resource, to maybe improve it further.

### Step 3 - Submit the resource to an easy to use web application

The researcher submit his resource throught a URL or DOI with minimal informations required (no personnal informations).

### Step 4 - Testing the resource against the Maturity Indicators

Provide the researcher with a one page result, with negative or positive score for each Maturity Indicator.

### Step 5 - Self-assesment of the FAIRness

When the result is negative, explain where it failed, and provide suggestions of how to validate this Maturity Indicator.
This will provide a usefull help to the researcher, and then allow him to improve the FAIRness of his ressource.

![fb_result_screen](/images/screen_fm_app.png)

### Step 6 - Improve and repeat

The reasercher will try to improve the FAIRness of his ressource, and test it again, and again, trying to validate the MI(s) he is interested in.


