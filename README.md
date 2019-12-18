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
