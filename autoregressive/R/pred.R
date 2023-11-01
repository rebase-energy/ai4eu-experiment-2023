data <- read.csv("data/AEMO1213.csv", header=TRUE, stringsAsFactors=FALSE)


fit = readRDS('R/fit.RData')

print(typeof(data))


#data = as.matrix(data)

# only use 10 sites to save some time...
data <- data[,c(22,1,20,15,2,11,17,18,3,14)]

data <- as.matrix(sapply(data, as.numeric))

print(typeof(data))

head(data, 10)


#print(data[4])

data <- tail(data, -2)


# Number of distinct time series / spatial dimension
K <- ncol(data)

# Choose training data
# First 45 days
train <- 1:(12*24*45)
# Choose test data
# Proceeding year
test <- 1:(12*24*365) + tail(train,1) 


# Form single coefficient matrix
B=fit$coef[[1]]
for(i in 2:fit$Order[1]){
	B <- cbind(B,fit$coef[[i]])
}


######## Residuals ########
lags <- fit$Order[[1]]

head(lags)

resid <- matrix(nrow=length(train)-lags,ncol=K)
for(i in (lags+1):length(train)){	
	resid[i-lags,] <- data[i,] - B %*% t(data[(i-1):(i-lags),])[1:(K*lags)]
}

####### 1 step ahead predictions on test data ######
pred <- matrix(nrow=length(test),ncol=K)
for(i in test){  
  pred[i-tail(train,1),] <- data[i,] - B %*% t(data[(i-1):(i-lags),])[1:(K*lags)]
}

head(pred, 10)