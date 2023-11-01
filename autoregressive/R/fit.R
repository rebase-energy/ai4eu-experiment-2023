data <- read.csv("data/AEMO1213.csv", header=TRUE, stringsAsFactors=FALSE)



source("R/sVAR-opt.R")



fit <- list(1, 2, 3)


saveRDS(fit, file="fname.RData")