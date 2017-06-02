library(formattable)

setwd("~/Documents/twoWords/STIMULUS/CURRENT")
group=2
if (group==1 | group==2 | group==3){
  fileName1 <- "W1.txt"
  fileName2 <- "W2.txt"
  targetFile1 <- "TargetList1.txt"
  fileName3 <- "W3.txt"
  fileName4 <- "W4.txt"
  targetFile2 <- "TargetList3.txt"
  fileName5 <- "W5.txt"
  fileName6 <- "W6.txt"
  targetFile3 <- "TargetList5.txt"
}
if (group==4 | group==5 | group==6){
  fileName1 <- "W3.txt"
  fileName2 <- "W4.txt"
  targetFile1 <- "TargetList3.txt" 
  fileName3 <- "W5.txt"
  fileName4 <- "W6.txt"
  targetFile2 <- "TargetList5.txt"
  fileName5 <- "W1.txt"
  fileName6 <- "W2.txt"
  targetFile3 <- "TargetList1.txt"
}
if (group==7 | group==8 | group==9){
  fileName1 <- "W5.txt"
  fileName2 <- "W6.txt"
  targetFile <- "TargetList5.txt"
  fileName3 <- "W1.txt"
  fileName4 <- "W2.txt"
  targetFile2 <- "TargetList1.txt"
  fileName5 <- "W3.txt"
  fileName6 <- "W4.txt"
  targetFile3 <- "TargetList3.txt"
}
if (group==10 | group==11 | group==12){
  fileName1 <- "W2.txt"
  fileName2 <- "W1.txt"
  targetFile1 <- "TargetList2.txt"
  fileName3 <- "W4.txt"
  fileName4 <- "W3.txt"
  targetFile2 <- "TargetList4.txt"
  fileName5 <- "W6.txt"
  fileName6 <- "W5.txt"
  targetFile3 <- "TargetList6.txt"
}
if (group==13 | group==14 | group==15){
  fileName1 <- "W4.txt"
  fileName2 <- "W3.txt"
  targetFile1 <- "TargetList4.txt"  
  fileName3 <- "W6.txt"
  fileName4 <- "W5.txt"
  targetFile2 <- "TargetList6.txt"
  fileName5 <- "W2.txt"
  fileName6 <- "W1.txt"
  targetFile3 <- "TargetList2.txt"
}
if (group==16 | group==17 | group==18){
  fileName1 <- "W6.txt"
  fileName2 <- "W5.txt"
  targetFile1 <- "TargetList6.txt"
  fileName3 <- "W4.txt"
  fileName4 <- "W3.txt"
  targetFile2 <- "TargetList4.txt"
  fileName5 <- "W2.txt"
  fileName6 <- "W1.txt"
  targetFile3 <- "TargetList2.txt"
}




tableName <- "shuffledWords"
wordList1 <- read.table(fileName1, header=FALSE, sep=",",stringsAsFactors = FALSE, fill = TRUE, colClasses="character")
wordList2 <- read.table(fileName2, header=FALSE,  sep=",",stringsAsFactors = FALSE, fill = TRUE, colClasses="character")
targets1 <- read.table(targetFile1, header=FALSE,  sep=",",stringsAsFactors = FALSE, fill = TRUE)

wordList3 <- read.table(fileName3, header=FALSE,  sep=",",stringsAsFactors = FALSE, fill = TRUE, colClasses="character")
wordList4 <- read.table(fileName4, header=FALSE,  sep=",",stringsAsFactors = FALSE, fill = TRUE, colClasses="character")
targets2 <- read.table(targetFile2, header=FALSE,  sep=",",stringsAsFactors = FALSE, fill = TRUE)

wordList5 <- read.table(fileName5, header=FALSE,  sep=",",stringsAsFactors = FALSE, fill = TRUE, colClasses="character")
wordList6 <- read.table(fileName6, header=FALSE,  sep=",",stringsAsFactors = FALSE, fill = TRUE, colClasses="character")
targets3 <- read.table(targetFile3, header=FALSE,  sep=",",stringsAsFactors = FALSE, fill = TRUE)

table1 <- cbind(wordList1,wordList2,targets1)
names(table1) <- cbind("wordlist1","wordlist2","targets")
shuffledTable1 <- rbind(table1[1:10,],table1[sample(11:nrow(table1)),])
#df1[sample(nrow(df1)),]

wordList1a <- shuffledTable1[,1]
wordList1b <- shuffledTable1[,2]
targetFile1a <- shuffledTable1[,3]

table2 <- cbind(wordList3,wordList4,targets2)
names(table2) <- cbind("wordlist1b","wordlist2b","targetsb")
shuffledTable2 <- rbind(table2[1:10,],table2[sample(11:nrow(table2)),])
wordList2a <- shuffledTable2[,1]
wordList2b <- shuffledTable2[,2]
targetFile2a <- shuffledTable2[,3]

table3 <- cbind(wordList5,wordList6,targets3)
names(table3) <- cbind("wordlist1s","wordlist2s","targetss")
shuffledTable3 <- rbind(table3[1:10,],table3[sample(11:nrow(table3)),])
wordList3a <- shuffledTable3[,1]
wordList3b <- shuffledTable3[,2]
targetFile3a <- shuffledTable3[,3]

FullTable <- cbind(shuffledTable1,shuffledTable2,shuffledTable3, deparse.level=0)
FullTable1 <- as.data.frame(FullTable)

formattable(FullTable1, list(
  wordlist1s = formatter("span", style = ~ ifelse(targetss == "L", 
                                               style(color = "black", font.weight = "bold"), NA)),

  wordlist2s = formatter("span", style = ~ ifelse(targetss == "R", 
                                                  style(color = "black", font.weight = "bold"), NA)), 
  
  wordlist1 = formatter("span", style = ~ ifelse(targets == "L", 
                                                  style(color = "black", font.weight = "bold"), NA)),
  
  wordlist2 = formatter("span", style = ~ ifelse(targets == "R", 
                                                  style(color = "black", font.weight = "bold"), NA)), 
  wordlist1b = formatter("span", style = ~ ifelse(targetsb == "L", 
                                                  style(color = "black", font.weight = "bold"), NA)),
  
  wordlist2b = formatter("span", style = ~ ifelse(targetsb == "R", 
                                                  style(color = "black", font.weight = "bold"), NA))
  ))

setwd("~/Documents/twoWords/STIMULUS/PSYCHOPY")

write(wordList1a, file = fileName1, append=FALSE, sep="\t")
write(wordList1b, file = fileName2, append=FALSE, sep="\t")
write(targetFile1a, file = targetFile1, append=FALSE, sep="\t")
write(wordList2a, file = fileName3, append=FALSE, sep="\t")
write(wordList2b, file = fileName4, append=FALSE, sep="\t")
write(targetFile2a, file = targetFile2, append=FALSE, sep="\t")
write(wordList3a, file = fileName5, append=FALSE, sep="\t")
write(wordList3b, file = fileName6, append=FALSE, sep="\t")
write(targetFile3a, file = targetFile3, append=FALSE, sep="\t")
write.table(FullTable1, file = tableName, append=FALSE, sep="\t" )


