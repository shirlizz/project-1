#Web Programming course
#Author : Elias Guaman / mail : cruz.guaman@yachaytech.edu.ec
#Tutor : Rigoberto Fonseca
#Date: Nov/2019

import os
import csv
import psycopg2
conn = psycopg2.connect("postgres://hlcellsnmwzcnm:de87153f5c3f0358ec5f0e8ae8b21468e0ecaa2e8b40f906e8a5bae3e1ca3b54@ec2-174-129-253-146.compute-1.amazonaws.com:5432/d6nem5fv43fj8u")
cur = conn.cursor()
i=0

with open("books.csv", 'r') as f:
  reader = csv.reader(f)
  next(reader)
  for row in reader:
    cur.execute("INSERT INTO books (isbn, title, author, year) VALUES (%s, %s, %s, %s)",(row[0],row[1],row[2], int(row[3])))
    i=i+1
    print(i)
  conn.commit()
