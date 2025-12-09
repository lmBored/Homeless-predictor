# Homeless prediction - Vestide

This extension analyzes your current vestide applications.

<img width="740" height="595" alt="image" src="https://github.com/user-attachments/assets/d9ef7e3f-fb85-40d6-b508-3d20f7d15373" />

+ Percentile ranking = (position/total * 100)
+ IQR outlier detection: Tukey's method (Q1 - 1.5\*IQR, Q3 + 1.5\*IQR) [1]
+ Z-score outlier detection: Values with |Z| > 2 are potential outliers [2]
+ Pick top N things based on average percentile performance

+ For pending application, use median number of total applications from processed list, and convert z-score into percentage probability where the true rank percentile is.
+ Example:
+ If pos is 5 out of 20 (top 25%), p_current = 0.25, n = 20
+ Target threshold then is 20/200 = 10%
+ Calculate how many std the current 25% is away from the target 10%
+ In this case it's low

## Version
### Initial Release (v1.0)
+ Popup dashboard to analyze housing application lists.
+ Automatically separates 'Pending' and 'Processed' applications.
+ Uses Z-score probability to predict the chance of finishing in the top 20 based on current position and historical applicant counts.
+ Color-coded status (Green/Orange/Red) indicating the likelihood of success.

## Guide
+ Visit https://rooms.vestide.nl/en/my-vestide/my-applications/ and click the extension

Or:
+ To use, visit room.vestide.nl
+ Click "My vestide"
+ Click "My applications" on the left side bar
+ Click the extension

## Test with python
+ There's a python file to test separately. Go to applied houses site, copy everything and paste to `asdf.txt`. Then run `main.py`
+ 
## Reference
[1] Tukey, J.W. (1977). Exploratory Data Analysis. Addison-Wesley

[2] Shiffler, R.E. (1988). Maximum Z scores and outliers; The American Statistician, 42(1), 79-80
