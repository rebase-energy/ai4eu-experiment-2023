# rm(list=ls())
# # setwd("./R Files")


# #### Load sVAR function ###

# # With stopping creterion
# source("sVAR-opt_v1_1.R")


# ###########################


# ### load some data ###
# load("AEMO_test_data.Rda")


data <- read.csv("data/AEMO1213.csv", header=TRUE, stringsAsFactors=FALSE)



source("R/sVAR-opt.R")


# only use 10 sites to save some time...
data <- data[,c(22,1,20,15,2,11,17,18,3,14)]


# Number of distinct time series / spatial dimension
K <- ncol(data)

# Choose training data
# First 45 days
train <- 1:(12*24*45)
# Choose test data
# Proceeding year
test <- 1:(12*24*365) + tail(train,1) 


# fit sVAR model
fit <- sVARfit(data[train,],dirtemp="./tempfiles")



# Plot BIC from stages 1 and 2 to check behaviour of stopping criterion
# par(mfrow=c(1,2))
# plot(fit$Ms,fit$BIC1,type="l",xlab="M",ylab="BIC",main="Stage 1")
# lines(c(fit$Order[2],fit$Order[2]),c(0,max(fit$BIC1)),lty=2,col=2)
# legend(fit$Ms[2],max(fit$BIC1),legend=as.character(fit$ps),lty=1,col=1:length(fit$ps),title="p")
# plot(fit$ms,fit$BIC2,type="b",xlab="m",ylab="BIC",main="Stage 2")
# lines(c(fit$Order[3],fit$Order[3]),c(0,max(fit$BIC2)),lty=2,col=2)


# Form single coefficient matrix
B=fit$coef[[1]]
for(i in 2:fit$Order[1]){
	B <- cbind(B,fit$coef[[i]])
}

######## Residuals ########
lags <- fit$Order[[1]]
resid <- matrix(nrow=length(train)-lags,ncol=K)
for(i in (lags+1):length(train)){	
	resid[i-lags,] <- data[i,] - B %*% t(data[(i-1):(i-lags),])[1:(K*lags)]
}

####### 1 step ahead predictions on test data ######
pred <- matrix(nrow=length(test),ncol=K)
for(i in test){  
  pred[i-tail(train,1),] <- data[i,] - B %*% t(data[(i-1):(i-lags),])[1:(K*lags)]
}

RMSE <- sqrt(colMeans((data[test,] - pred)^2))
