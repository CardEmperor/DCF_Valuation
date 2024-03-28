# DCF_Valuation
a.       This implements a growth-RoC DCF model with explicit fade period, workings for which the excel file can be found here - https://github.com/aditya-dhinavahi/Reverse_DCF_test. If you’re unfamiliar with the theoretical working of discounted cash flow (DCF) model, you may refer to any free resources online.

b.      User inputs are cost of capital, RoCE, growth during high growth period, high growth period (years), fade period (years) and terminal growth rate. Kindly restrict inputs to ranges as given in the reference web app.

c.       Tax rate is assumed constant at 25%.

d.      High growth period (years) and fade period (years) may vary as per user input.

        i.      Example in excel sheet uses fixed high growth period of 15 years and fade period of 15 years.

        ii.      During the fade period, the growth falls linearly to terminal growth rate.

e.      Lower of current PE and FY23PE is used to calculate degree of overvaluation.

        i.      e.g. if current PE < FY23PE, degree of overvaluation = (current PE/calculated intrinsic PE) – 1,

        ii.      else degree of overvaluation = (FY23 PE/calculated intrinsic PE) - 1
