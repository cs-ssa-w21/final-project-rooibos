# final-project-rooibos
This is the final project of team rooibos. We tried to see how the occurrence of gender-specific crimes in China relates to socioeconomic factors. We scraped gender-specific crime data from a 'bot' webpage documenting such incidents and matched most of them to their happening cities. In the meantime, we gather socioeconomic data on these cities, and eventually conduct quantative analyses to arrive at conclusions.

## Web-scraping
The libraries/packages used in this part include:
- requests version: 2.25.1
- bs4 (BeautifulSoup) version: 4.9.3
- pandas version: 1.2.0
- csv version: 1.0
- cpca version: 0.5.5 (can be found at https://github.com/DQinYuan/chinese_province_city_area_mapper or https://pypi.org/project/cpca/)
- jieba version: 0.39 (can be found at https://github.com/fxsjy/jieba)
- china_cities version: 0.0.3 (can be found at https://pypi.org/project/china-cities/)
- pinyin version: 0.4.0 (can be found at https://pypi.org/project/pinyin/)

This part of code was entirely written on Jupyter Notebook; to run this part, open the "neat version" file and run each chunk. Thanks =)

## Social data collection and match
After getting crime data by web-scraping, we collect social-economic data. The data resource is the EPS (Easy Professional Superior) data platform, which is a systematic information service platform and where there is access to many databases. 

Web: https://www.epsnet.com.cn/index.html#/Home

The original data are about 21 variables, from two databases in the EPS platform. The last three come from Chinses Regional Economic Database, the others come from Chinese City Database. For each variable, we collect panel data from 2014-2018, the number of observations (cities) vary from different variables.
The final version of socio-economic data is that, for each city, the value of a variable is the mean of the values of the variable from 2014-2018.
Finally, we match the socio-economic data with crime data, that is only remaining observations which we both have their crime data and socio-economic data.

The libraries/packages used in this part include:
- pandas version: 1.2.0
- numpy
- os
- matplotlib.pyplot
- seaborn version: 0.11.1

Files:
- socioeco_variables_pre.csv:
- total_data_impute.csv: The data after imputation
- data_reg.csv: The data picked after checking correlation(multicolinearity among predictors)


## Visualization
Besides packages covered above, additional packages & data sets in this part include:
- geopandas version: 0.9.0
- bokeh version: 2.3.0
- wordcloud version: 1.8.1
- folium version: 0.12.0
- seaborn version: 0.11.1
- scikit-learn version: 0.24.1
- [map of China (city-level) shapefile](https://www.jianguoyun.com/p/DU61EH8QgsnRBxj4x7QD)
- [longitutes & latitutes of Chinese cities](https://simplemaps.com/data/cn-cities)

Two interactive maps ([NumberOnMap](NumberOnMap.html) & [WordCloudOnMap](WordCloudOnMap.html)) are included in the repository. Learn more about our results by browsing the maps!

![image](rainbow%20pup%20saying%20thank%20you.png)
