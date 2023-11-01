data <- read.csv("data/AEMO1213.csv", header=TRUE, stringsAsFactors=FALSE)



source("R/sVAR-opt.R")


# only use 10 sites to save some time...
data <- data[,c(22,1,20,15,2,11,17,18,3,14)]


head(data, 5)

# Number of distinct time series / spatial dimension
K <- ncol(data)

# Choose training data
# First 45 days
train <- 1:(12*24*45)


#train = data
head(train, 5)

# Choose test data
# Proceeding year
#test <- 1:(12*24*365) + tail(train,1) 


# fit sVAR model
fit <- sVARfit(data[train,],dirtemp="./tempfiles")

#fit <- sVARfit(train,dirtemp="./tempfiles")


saveRDS(fit, file="fit.RData")