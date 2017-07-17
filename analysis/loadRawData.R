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
#Error #library(devtools); install_github("ggplot2", "hadley", "develop") #to get latest version of ggplot2 that has viridis color palette

#ggplot will accumulate data automatically to make a histogram, will it not accumulate to make a heatPlot?

dCount<- df %>% count(wordEcc,responsePosRelativeleft, responsePosRelativeright)

correl<- ggplot(dCount, aes(x = responsePosRelativeleft, y = responsePosRelativeright)) + geom_tile(aes(fill = n)) +  facet_grid(wordEcc~.)
correl<- correl+theme_bw()
correl + scale_colour_brewer
correl + scale_colour_grey
correl<-correl + scale_fill_gradient(low="black", high="white") 
#correl + scale_color_viridis() 
show(correl)

#Zero in on center because most large SPEs are guesses
minSPE<--3
maxSPE<- 3
correl +  xlim(minSPE,maxSPE) + ylim(minSPE,maxSPE)

#scales free
correl + facet_grid(wordEcc~., scales="free")  +  xlim(minSPE,maxSPE) + ylim(minSPE,maxSPE)

#Calculate correlation
cor.test(df$responsePosRelativeleft, df$responsePosRelativeright,
         alternative = c("two.sided"),
         method = c("pearson"),
         exact = NULL, conf.level = 0.95, continuity = FALSE)

smallSPEs <- df %>% filter(abs(responsePosRelativeleft) <= 3 ) %>% filter( abs(responsePosRelativeright) <= 3 )

#ddply(smallSPEs, .(wordEcc), 
near<- smallSPEs %>% filter( wordEcc==1 )
far <- smallSPEs %>% filter( wordEcc > 1 )

cor.test(smallSPEs$responsePosRelativeleft, smallSPEs$responsePosRelativeright,
         alternative = c("two.sided"),
         method = c("pearson"),
         exact = NULL, conf.level = 0.95, continuity = FALSE)

nearCorr<- cor.test(near$responsePosRelativeleft, near$responsePosRelativeright,
         alternative = c("two.sided"),
         method = c("pearson"),
         exact = NULL, conf.level = 0.95, continuity = FALSE)

farCorr<- cor.test(far$responsePosRelativeleft, far$responsePosRelativeright,
                   alternative = c("two.sided"),
                   method = c("pearson"),
                   exact = NULL, conf.level = 0.95, continuity = FALSE)

#To-do
#Eliminate the five bad Ss
#Address the argument that it wasn't correlated in the far just because of more guessing
#Calculate for each subject and then do a t-test for near and far

