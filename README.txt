This integer program was created in order to make optimal groups for a class of 24 students. Each of the groups will have a specific 
project they need to do. Each of the students put down preferences for what project they want to do (ranked the project from 1-10).
This is in the People's_Project_Preferences.csv document. The students then ranked from 1 -10 how good they were at a series of skills. 
This is in the People's_Skills.csv document and we use this in the integer program in order to make sure each group has one expert in 
each of these skills. We then need each group to have at least two hours a week to work together on it. This is found in the 
People's_Availabilities.csv. This has a binary entry for whether a particular student is available at a certain hour. The code is in the
Group Optimization Code py file and then a detailed description of the integer program as well as the results are in the pdf 
Group_Optimization_Integer_Program_Explanation.