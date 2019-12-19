# MarketGenie
This is part of an course in id1214 in KTH. 

Milestone 1 - Explicit what kind of data will be used and how will it be structured in training/test data. 
   - How do define labels?
      If tomorrow closening price is higher than today, buy. Prelimary just buy (no weak or strong).
      If tomorrow closening price is lower than today, sell. 
   - How many days in period? 
      We will try 30 in the beginning. (maybe later 15 or 60 days)
   - for each day, what data will be used?
      ???? High, Low, Volume, open , close , volume ?????
Milestone 2 - The three functions/black boxes
  
  1) ----------------The data provider ------------------
        input: The two stocknames we want to crossexamine! give me a start date and end date! Give me the length of a period, like 30
          days!  
        output: [[day1,day2,day3...,today],[day1,day2,day3...,today],[day1,day2,day3...,today],[day1,day2,day3...,today]...] 
        output2: [period1,period2,period3...] 
      
  2) ----------------Our labelmaking classifier----------
        input: [[day1,day2,day3...,today],[day1,day2,day3...,today],[day1,day2,day3...,today],[day1,day2,day3...,today]...]
        output: [label1,label2,label3 ....]
        
  3) ---------------- Machinelearning function-----------
        input: data from program 1 and the labels from program 2, test data!
        output: Predicted label on the test data.




REAL EXAMPLE: 
given TESLA and APPLE, with a 4-day period. If we look at this example -> 

TESLA:
                  High         Low        Open       Close    Volume   Adj Close
Date
2017-01-03  220.330002  210.960007  214.860001  216.990005   5923300  216.990005
2017-01-04  228.000000  214.309998  214.750000  226.990005  11213500  226.990005
2017-01-05  227.479996  221.949997  226.419998  226.750000   5911700  226.750000
2017-01-06  230.309998  225.449997  226.929993  229.009995   5527900  229.009995
2017-01-09  231.919998  228.000000  228.970001  231.279999   3979500  231.279999

APPLE:
                  High         Low        Open       Close      Volume   Adj Close
Date
2017-01-03  116.330002  114.760002  115.800003  116.150002  28781900.0  110.953873
2017-01-04  116.510002  115.750000  115.849998  116.019997  21118100.0  110.829704
2017-01-05  116.860001  115.809998  115.919998  116.610001  22193600.0  111.393303
2017-01-06  118.160004  116.470001  116.779999  117.910004  31751900.0  112.635139
2017-01-09  119.430000  117.940002  117.949997  118.989998  33561900.0  113.666824

We can make one training data entry that looks like this -> 
[220.330002, 210.960007, 214.860001, 216.990005, 5923300, 216.990005, 228.000000, 214.309998, 214.750000, 226.990005, 11213500, 226.990005, 227.479996, 221.949997, 226.419998, 226.750000, 5911700, 226.750000, 230.309998, 225.449997, 226.929993, 229.009995, 5527900, 229.009995, 116.330002, 114.760002, 115.800003, 116.150002, 28781900.0, 110.953873, 116.510002, 115.750000, 115.849998, 116.019997, 21118100.0, 110.829704, 116.860001, 115.809998, 115.919998, 116.610001, 22193600.0, 111.393303, 118.160004, 116.470001, 116.779999, 117.910004, 31751900.0, 112.635139]
The label for this example is "BuyBuy" because both the stocks increase in day 2017.01.09 (the future), if we use a simple classifier.
