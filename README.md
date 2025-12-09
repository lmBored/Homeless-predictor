# Homeless prediction

This analyzes your current vestide applications. Go to applied houses site, copy everything and paste to `asdf.txt`. Then run.

- Percentile ranking = (position/total * 100)
- IQR outlier detection: Tukey's method (Q1 - 1.5\*IQR, Q3 + 1.5\*IQR) [1]
- Z-score outlier detection: Values with |Z| > 2 are potential outliers [2]
- Pick top N things based on average percentile performance

## Next step

+ [ ] FF extension

<!--# Disclaimer-->

## Reference
[1] Tukey, J.W. (1977). Exploratory Data Analysis. Addison-Wesley

[2] Shiffler, R.E. (1988). Maximum Z scores and outliers; The American Statistician, 42(1), 79-80
