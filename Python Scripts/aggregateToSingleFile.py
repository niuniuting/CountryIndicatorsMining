# -*- coding: utf-8 -*-
import time
import csv
import numpy as np
from sklearn.preprocessing import Imputer

def writeCSV(path,aList):
	with open(path,'wb') as w:
		a = csv.writer(w, delimiter = ',')
		a.writerows(aList)
	w.close()

# ----- Define Target Variables and Filenames 
targetList = ['2704: Corruption perceptions index - Transparency',
'2707: Failed States Index Total - Fund for Peace',
'2713: Legitimacy of the State - Fund for Peace',
'2716: Security Apparatus - Fund for Peace',
'2718: External Intervention - Fund for Peace',
'0808: GDP per capita  (current US$) - WDI',
'0811: GDP per capita growth  (annual %) - WDI',
'0835: GNI per capita; PPP  (current international $) - WDI'
]

targetColumnIndex = [1995, 1998, 2004, 2007, 2009, 808, 811, 835]

# filenameList = ['2004_2016-06-16-14-15-50.csv',
# '2005_2016-06-16-14-16-51.csv',
# '2006_2016-06-16-14-17-56.csv',
# '2007_2016-06-16-14-18-58.csv',
# '2008_2016-06-16-14-19-59.csv',
# '2009_2016-06-16-14-21-00.csv',
# '2010_2016-06-16-14-22-01.csv',
# '2011_2016-06-16-14-23-02.csv',
# '2012_2016-06-16-14-24-03.csv',
# '2013_2016-06-16-14-25-06.csv',
# '2014_2016-06-16-14-26-06.csv']

filenameList = ['2006_2016-07-26-21-13-34.csv',
'2007_2016-07-26-21-14-53.csv',
'2008_2016-07-26-21-16-12.csv',
'2009_2016-07-26-21-17-32.csv',
'2010_2016-07-26-21-18-54.csv',
'2011_2016-07-26-21-20-14.csv',
'2012_2016-07-26-21-21-33.csv',
'2013_2016-07-26-21-22-52.csv',
'2014_2016-07-26-21-24-10.csv',
'2015_2016-07-26-21-25-28.csv']

# ----- Get a header row
totalYear = len(filenameList)-1
firstRow = ['Year - Country']
with open('./Formatted Files/'+filenameList[0], 'rb') as f:
	reader = csv.reader(f)
	for row in reader:
		header = row
		break
	f.close()
	firstRow = firstRow[0:1]+[t[0:4]+'N'+t[4:] for t in targetList]+header[1:]
firstRow = [firstRow]

# 	# print [header.index(t) for t in targetList]	

# ----- Create a header column
countryList = []
with open('./Formatted Files/'+filenameList[0], 'rb') as f:
	reader = csv.reader(f)
	count = 0
	for row in reader:
		count += 1
		if count == 1:
			continue
		countryList.append(row[0])
countryList = [[str(year)+' - '+country] for year in range(2006,2015) for country in countryList ]
print len(countryList)

# ----- Create data file
allData = None
notImputed = None
validity = None
rows = [firstRow]
for idx in range(totalYear):
	nowYearFile = filenameList[idx]
	nextYearFile = filenameList[idx+1]

	# ----- Collect data from this year
	datasetThisYear = np.genfromtxt('./Formatted Files/'+nowYearFile, delimiter=",", skip_header=1, autostrip=True, missing_values=np.nan, usecols=tuple(range(1,len(header))))
	
	# ----- Calculate the density of each column and decide whether it is a valid column (density > 0.4) or not
	densityThisYear = np.sum(~np.isnan(datasetThisYear), axis = 0) * 1.0 / datasetThisYear.shape[0]
	validColumnThisYear = densityThisYear > 0.4
	
	# ----- For each invalid column, fill 0 for all rows
	row, column = datasetThisYear.shape
	for i in range(column):
		if not validColumnThisYear[i]:
			datasetThisYear[:,i] = np.zeros(row)
	notImputedThisYear = np.copy(datasetThisYear)

	# ----- Missing values imputation with median
	imp = Imputer(missing_values='NaN', strategy='median', axis=0)
	datasetThisYear = imp.fit_transform(datasetThisYear)
	# print datasetThisYear

	# ----- Collect target variables from the next year and combine with the dataset this year
	targetNextYear = np.genfromtxt('./Formatted Files/'+nextYearFile, delimiter=",", skip_header=1, autostrip=True, missing_values=np.nan, usecols=tuple(targetColumnIndex))
	combinedData = np.concatenate((targetNextYear,datasetThisYear),axis=1)
	notImputedCombinedData = np.concatenate((targetNextYear,notImputedThisYear),axis=1)

	# ----- Concatenate data with the previous years and calculate final validity of columns using logical_and
	if allData is None:
		allData = combinedData
		notImputed = notImputedCombinedData
		validity = validColumnThisYear		
	else:
		allData = np.concatenate((allData,combinedData),axis=0)
		notImputed = np.concatenate((notImputed,notImputedCombinedData),axis=0)
		validity = np.logical_and(validity,validColumnThisYear)		

print allData.shape
print np.sum(validity)
# ----- Add validity values for targets and header column
validity = np.concatenate((np.array((len(targetList)+1)*[True]),validity))

# ----- Combine data, headerRow, headerColumn
dataWithCountry = np.concatenate((np.array(countryList),allData),axis=1)
dataWithCountryAndHeader = np.concatenate((np.array(firstRow),dataWithCountry),axis = 0)

notImputedDataWithCountry = np.concatenate((np.array(countryList),notImputed),axis=1)
notImputedDataWithCountryAndHeader = np.concatenate((np.array(firstRow),notImputedDataWithCountry),axis = 0)
# print dataWithCountryAndHeader
# print dataWithCountryAndHeader.shape

# ----- Select only valid columns
selectedColumn = tuple([colIdx for colIdx in range(len(validity)) if validity[colIdx]])
filteredDataWithCountryAndHeader = dataWithCountryAndHeader[:,selectedColumn]
filteredNotImputedDataWithCountryAndHeader = notImputedDataWithCountryAndHeader[:,selectedColumn]

print ('dataWithCountryAndHeader shape = %d,%d'%(dataWithCountryAndHeader.shape[0],dataWithCountryAndHeader.shape[1]))
print ('filteredDataWithCountryAndHeader shape = %d,%d'%(filteredDataWithCountryAndHeader.shape[0],filteredDataWithCountryAndHeader.shape[1]))
print ('filteredNotImputedDataWithCountryAndHeader shape = %d,%d'%(filteredNotImputedDataWithCountryAndHeader.shape[0],filteredNotImputedDataWithCountryAndHeader.shape[1]))

writeCSV("New_2006-2014_AllCols.csv",dataWithCountryAndHeader.tolist())
writeCSV("New_2006-2014_FilteredCols.csv",filteredDataWithCountryAndHeader.tolist())
filteredNotImputedList = filteredNotImputedDataWithCountryAndHeader.tolist()
filteredNotImputedList = [['' if data == 'nan' else data for data in row] for row in filteredNotImputedList ]
writeCSV("New_2006-2014_FilteredColsNotImputed.csv",filteredNotImputedList)