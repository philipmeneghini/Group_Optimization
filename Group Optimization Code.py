#!/usr/bin/env python
# coding: utf-8

# In[31]:


import gurobipy as gp
from gurobipy import GRB
import numpy as np
import pandas as pd

##initialize all data
names = ["Alex M.","Alex R.","Arjun","Brendan","Elisabeth","Emma","Erica","Evan","Hanna","Kalju","Khai","Lorene","Matthew","Maura",
         "Maxwell","Nathan","Parker","Philip","Samuel","Sarah","Sejal","Yongzhi","Yongkai","Yuchen"]

numberofpeople = len(names)
skills_frame = pd.read_csv(r"C:\Users\philm\Documents\456\Group_Optimization\People's_Skills.csv")
preferences_frame = pd.read_csv(r"C:\Users\philm\Documents\456\Group_Optimization\People's_Project_Preferences.csv")
availability_frame = pd.read_csv(r"C:\Users\philm\Documents\456\Group_Optimization\People's_Availabilities.csv")
preferences_frame.drop(preferences_frame.columns[0], axis =1, inplace=True)


names_val= skills_frame["name"]
coding_val = skills_frame["Coding skills"]
writing_val = skills_frame["Writing skills"]
latex_val = skills_frame["Latex skills"]
present_val = skills_frame["Presentation skills"]
leader_val = skills_frame["Leadership skills"]
org_val = skills_frame["Organizational skills"]
time_val = skills_frame["Time management skills"]

#The dictionaries we want our data in
coding={}
writing ={}
latex ={}
presentation={}
leadership={}
organization={}
timemanagement ={}
preferences ={}
time={}

#Converting all our dictionary values to boolean values. If they rank themselves above a sux they are considered
#"proficient"
for i in range(0,24):
    if coding_val[i] >6:
        coding[names[i]]=1
    else:
        coding[names[i]]=0
    if writing_val[i] >6:
        writing[names[i]]=1
    else:
        writing[names[i]]=0
    if latex_val[i] >6:
        latex[names[i]]=1
    else:
        latex[names[i]]=0
    if present_val[i] >6:
        presentation[names[i]]=1
    else:
        presentation[names[i]]=0
    if leader_val[i] >6:
        leadership[names[i]]=1
    else:
        leadership[names[i]]=0
    if org_val[i] >6:
        organization[names[i]]=1
    else:
        organization[names[i]]=0
    if time_val[i] >6:
        timemanagement[names[i]]=1
    else:
        timemanagement[names[i]]=0
    preferences[names[i]]=list()
    temp = preferences_frame.iloc[i]
    temp=temp.transpose()
    for j in range(0,7):
        preferences[names[i]].append(temp.iloc[j])
    time[names[i]]= list()
    temp2 = availability_frame.iloc[i]
    temp2 =temp2.transpose()
    for j in range(0,len(availability_frame.columns)):
        time[names[i]].append(temp2.iloc[j])

##initialize all decision variables
m=gp.Model()
x = m.addVars(24,7,vtype=GRB.BINARY, name = "x")
y = m.addVars(7, vtype=GRB.BINARY, name = "y")
w= m.addVars(7, 168, vtype=GRB.BINARY, name = "w")
##Last variable represents how many restraints are broken
c = m.addVars(7, vtype = GRB.INTEGER, name ="c")
obj =0
for i in range(0,24):
    for j in range(0,7):
        obj=obj + int(preferences[names[i]][j])*x[i,j]
for k in range(0,7):
    ##Our objective function goes down as we break more of the constraints
    obj=obj-c[k]

m.setObjective(obj, GRB.MAXIMIZE)

##Initialize Constraints

##Each student is assigned to one project
for i in range(0,24):
    sum1=0
    for j in range(0,7):
        sum1 = sum1 + x[i,j]
    m.addConstr(sum1 ==1)


##Student cannpot be assigned to project if it is not happening
for j in range(0,7):
    sum2=0
    for i in range(0,24):
        sum2=sum2 + x[i,j]
    ##Add Constraints to keep three to four people to group
    m.addConstr(sum2-4*y[j]<=0)
    m.addConstr(sum2-3*y[j]>=0)

##Six or Seven Projects should happen
sum3=0
for j in range(0,7):
    sum3=sum3 +y[j]
m.addConstr(sum3>= 6)
m.addConstr(sum3<=7)

##Every project needs at least one coder, presenter, writer, organizer, Latex expert, leader, and a person who is good at time management
##The matrix variable c serves as a way to mark if one of these constraints are not met and it penalizes the objective function.
for j in range(0,7):
    sum4=0
    sum5=0
    sum6=0
    sum7=0
    sum8=0
    sum9=0
    sum10=0
    for i in range(0,24):
        sum4 = sum4 + coding[names[i]]*x[i,j]
        sum5=sum5+ presentation[names[i]]*x[i,j]
        sum6=sum6+ writing[names[i]]*x[i,j]
        sum7 = sum7 + latex[names[i]]*x[i,j]
        sum8=sum8+ leadership[names[i]]*x[i,j]
        sum9=sum9 + organization[names[i]]*x[i,j]
        sum10=sum10 + timemanagement[names[i]]*x[i,j]
    m.addConstr(sum4+ c[j]>=y[j])
    m.addConstr(sum5 + c[j]>=y[j])
    m.addConstr(sum6+ c[j]>=y[j])
    m.addConstr(sum7+c[j]>=y[j])
    m.addConstr(sum8+ c[j]>=y[j])
    m.addConstr(sum9+ c[j]>=y[j])
    m.addConstr(sum10+ c[j]>=y[j])
    m.addConstr(c[j]>=0)

##Time constraint is as follows
##We set w[j,h] to be binary so we want if group j can meet at hour h then we have a zero and a one otherwise
for j in range(0,7):
    for h in range(0,168):
        res1=0
        res2=0
        for i in range(0,24):
            res1+= x[i,j]
            res2+= time[names[i]][h]*x[i,j]
        m.addConstr(w[j,h]<= res1-res2)
        ##This makes sure if one or more group mates cannot meet that there is a one in that entry
        m.addConstr(w[j,h]>= (res1-res2)/4)

        
##Now making the actual time constraint that a group must have at least two hours where they can all meet
for j in range(0,7):
    res3=0
    for h in range(0,168):
        res3+= w[j,h]
    m.addConstr(res3<= 166*y[j])

##Now since we have all our constraints we can try to find the optimal groups
m.optimize()

##Now print out the groups
for j in range(0,7):
    print("\nGroup "+ str(j) +": ")
    for i in range(0,24):
        if x[i,j].X == 1.0:
            print(names[i]+", ")
    if y[j].X==0:
        print("project not happening")
    else:
        print("\nmeeting times: ")
        for k in range(0,168):
            if w[j,k].X== 0:
                day=""
                d= int(k/24)
                if d == 0:
                    day="sunday"
                if d == 1:
                    day="monday"
                if d == 2:
                    day="tuesday"
                if d == 3:
                    day="wednesday"
                if d == 4:
                    day="thursday"
                if d == 5:
                    day="friday"
                if d == 6:
                    day="saturday"
                hour = k%24
                print("day: "+ day + " hour: "+ str(hour) + " (military)")
    


# In[17]:





# In[79]:





# In[ ]:





# In[ ]:




