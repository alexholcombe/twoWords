#Loads raw data
require(R.matlab)
rawDataPath<-"../dataRaw/"
directoryOfRawData<- rawDataPath
path <- file.path(directoryOfRawData)

filePaths<- list.files(path, pattern="*.txt")

i=1
rawFileToImport<- file.path(path, filePaths[i])

dataThisSubject<- read.table(rawFileToImport, header=TRUE)

df <- rbind(df,dataThisSubject) #Add subjects data to main dataFrame

df<-data.frame()
for (fileName in filePaths) #Loop through and read in each Cheryl-prepared data file
{
  rawFileToImport<- file.path(path, fileName)
  dataThisSubject<- read.table(rawFileToImport, header=TRUE)
  dataThisSubject$filename<- fileName
  df <- rbind(df,dataThisSubject) #Add subjects data to main dataFrame
}

library(ggplot2)


#sanity check
g=ggplot(df,   aes(x=responsePosRelativeright))  
g<-g+facet_grid(wordEcc~.)  +geom_histogram(bin_width=1)
g #looks good

library(dplyr)
#ggplot will accumulate data automatically to make a histogram, will it not accumulate to make a heatPlot?

dCount<- df %>% count(responsePosRelativeleft, responsePosRelativeright)

correl<- ggplot(dCount, aes(x = responsePosRelativeleft, y = responsePosRelativeright)) + geom_tile(aes(fill = n)) +  facet_grid(wordEcc~.)
show(correl)
#theme(axis.title.y = element_blank())


#melt data so that SPE


ggplot(mat.melted, aes(x = SPEleft, y = SPEright, fill = value)) + geom_tile()  


sanityCheck=FALSE
if (sanityCheck) {
 #sanity check
 g=ggplot(E1,   aes(x=responseLetter1))  
 g<-g+facet_grid(condition~.)  +geom_histogram()
 g
}


saveDataFramesPath<-"loadRawData/"
write.csv(E1,paste0(saveDataFramesPath, "CherylE1.csv"),row.names=FALSE)