
# 
# License: BSD_3_clause 
# 
# 
# Copyright (c) 2015, Jethro Dowell, Pierre Pinson, Guillaume Le Ray
#   
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#   
# Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in
# the documentation and/or other materials provided with the
# distribution.
# 
# Neither the name of the University of Strathclyde and the Danish 
# Technical University nor the names of its contributors may be used 
# to endorse or promote products derived from this software without specific
# prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


#### libraries required####
# Uncomment if not installed
#install.packages("ff","MASS")
library(ff)
library(MASS)

sVARfit <- function(data, p=3, Ms=NULL,ms=NULL,ms_start=NULL,converge=0.0001,fconverge=0.0001,dirtemp=paste0(getwd(),"/temp")){

      ### sVAR_BIC compute the BIC calculation at the different stage of the method
      sVAR_BIC <- function(pFunction,RFunction,A,BIC_weight,conv=converge,...){
        # Initialise variables
        gamma <- matrix(data=0, nrow=BIC_weight, ncol=1)
        oldgamma <- matrix(data=0, nrow=BIC_weight, ncol=1)
        alpha <- RFunction %*% gamma
        dim(R)
        # Count no. of itterations
        count=0
        repeat{
          count <- count +1
          Yhat <- matrix(data=0, nrow=N0,ncol=ncol(data))

          # Estimate noise COV matrix, Sigma
          Yhat <- do.call(rbind,lapply(1:(N0-pFunction),function(i,...){
            rowSums(do.call(cbind,lapply(1:pFunction,function(j,...)A[[j]] %*% data[i+pFunction-j,])))
          }))
          Yhat <-rbind(matrix(0,nrow=pFunction,ncol=ncol(data)),Yhat)

          Sigma <-Reduce("+",lapply((pFunction+1):N0,function(i,...){
            (Yhat[i,]-data[i,]) %*% t(Yhat[i,]-data[i,])
          }))
          Sigma <- Sigma/(N0-pFunction)

          # Estimate VAR coefs
          L <- do.call(cbind,lapply(1:(N0-pFunction),function(i,...){
            do.call(c,lapply(1:pFunction,function(j,...){
              data[i+pFunction-j,]
            }))
          }))

          y <- do.call(c,lapply(1:(N0-pFunction),function(i,...){data[i+pFunction,]}))

          invSigma <- solve(Sigma)

          # Split equation (A.4. Davis et al.) into managable matrices
          mat1 <- t(RFunction) %*% kronecker((L %*% t(L)),invSigma) %*% RFunction
          mat1 <- ginv(mat1) %*% t(RFunction)

          mat2 <- as.vector(apply(L,1,function(l,...){
            apply(invSigma,1,function(iS,...){
              kronecker(t(l),t(iS)) %*% y
            })
          }))

          gamma <-  mat1 %*% mat2
          alpha <- RFunction %*% gamma

          # Get As from alpha
          A <- lapply(1:pFunction,function(i,...)matrix(alpha[((i-1)*numberTimeSeries^2+1):(i*(numberTimeSeries^2))], nrow=numberTimeSeries, ncol=numberTimeSeries))

          # Check convergence...  # Convergence check
          if (max(oldgamma - gamma)<conv|count>100){
            if(count>100) warning(paste("Check VAR Coefficient Convergence: p=",pFunction,", M=",M,"; Converge=",max(oldgamma - gamma),".", sep =""))
            break
          }else oldgamma <- gamma
        }

        # Calculate residuals and Log Likelihood
        err <- t(Yhat[(pFunction+1):N0,] - data[(pFunction+1):N0,])

        eInvse <- sum(apply(err,2,function(i)t(i)%*%invSigma%*%i))
        logL <- -(numberTimeSeries*(N0-pFunction)*log(2*pi))/2 - ((N0-pFunction)/2)*log(det(Sigma)) - 0.5*eInvse

        # BIC...
        BIC <- -2*logL + log((N0-p))*BIC_weight

        return(list("BIC"=BIC,"Sigma"=Sigma,"R"=RFunction,"A"=A, "alpha"=alpha, "y"=y,"invSigma"=invSigma))

      }
      #### Missing data check ####
      ##### calculcate fxx from mvspec optimised ####

    # Multivariate spectral density matrix estimate
    print('Multivariate spectral density matrix estimate')
    #paramaters mvspec
      spans = 3*ncol(data)
      fast = TRUE
      na.action = na.fail

      data <- na.action(as.ts(data))
      data <- as.matrix(data)
      dataMvspec <- sweep(data, 2, colMeans(data))
      dataMvspec <- spec.taper(dataMvspec, 0)

      datafreq <- frequency(dataMvspec)

      N0 <- nrow(data)
      numberTimeSeries <- ncol(data)

      kernel <-  kernel("modified.daniell", spans%/%2)

      NewN <-nextn(N0)
      dataMvspec <- rbind(dataMvspec, matrix(0, nrow = (NewN - N0), ncol = ncol(dataMvspec)))
      N <- nrow(dataMvspec)
      Nspec <- floor(N/2)

      xfft <- mvfft(dataMvspec)

      dir.create(dirtemp, showWarnings = FALSE)

    ### JD: v2 mod
    #  options(fftempdir = paste0(getwd(),sub(".","",dirtemp)))
    options(fftempdir = dirtemp)

      lapply( 1:numberTimeSeries,function(i,...){
        lapply( 1:numberTimeSeries,function(j,..){
          res<- xfft[, i] * Conj(xfft[, j])/(N0 *  datafreq)
          res[1]<- 0.5 * (res[2] + res[N])
          res<- kernapply(res, kernel, circular = TRUE)
          res <- res[2:(Nspec + 1)]
          #wrap the results in an ff object
          res <- ff(rbind(Re(res),Im(res)),dim=c(2,length(2:(Nspec + 1))),vmode="double")
          tores <- filename(res)
          # save the ff file on the harddisk
          ffsave(res,file=paste0(getOption("fftempdir"),"/pgram",i,"-",j))
          close(res)
          file.remove(tores)
        })
      })




      ffload(paste0(getOption("fftempdir"),"/pgram",1,"-",1),overwrite =TRUE)
      complex(real=res[1,],imaginary=res[2,])

      #create the blocks to avoid to saturate the memory
      block1 <- seq(from=1,to=length(2:(Nspec + 1)),by=.Machine$integer.max/(numberTimeSeries^2*4))
      # if all the data fit into 1 block (matrix with 1 row)
      if(length(block1)==1){ block <- matrix(c(block1,length(2:(Nspec + 1))),nrow=1,byrow=TRUE)
      }else block <-cbind(block1,c(block1[-1],length(2:(Nspec + 1))))

    #apply the operation on each block
      lapply(1:nrow(block),function(k,...){
        myTable  <- array(0,dim=c(numberTimeSeries,numberTimeSeries,length(block[k,1]:block[k,2])))

        # extract all the value of the block for all the i,j combination and fill the array myTable
        myTableList <- lapply( 1:numberTimeSeries,function(i,...){
          do.call(rbind,lapply( 1:numberTimeSeries,function(j,..){

            ffload(paste0(getOption("fftempdir"),"/pgram",i,"-",j),overwrite =TRUE)
            complexNumber <- complex(real=res[1,block[k,1]:block[k,2]],imaginary=res[2,block[k,1]:block[k,2]])
            tores <- filename(res)
            close(res)
            file.remove(tores)
            return(complexNumber)
          }))
        })

        #convert myTableList to array
        for(i in 1:length(myTableList))myTable[i,,] <-  myTableList[[i]]

        # Inverse spectral density matrix
        myTable <-  array(apply(myTable,3,function(toSolve,...){
          solve(matrix(data=toSolve,nrow=numberTimeSeries,ncol=numberTimeSeries))
        }),dim=c(numberTimeSeries,numberTimeSeries,length(block[k,1]:block[k,2])))


        # Format the data back as it take by block (k) several vectors can be created for one i,j combination
        lapply( 1:numberTimeSeries,function(i,...){
          lapply(1:numberTimeSeries,function(j,..){
            res <- ff(rbind(Re(myTable[i,j,]),Im(myTable[i,j,])),dim=c(2,length(2:(Nspec + 1))),vmode="double")
            tores <- filename(res)
            ffsave(res,file=paste0(getOption("fftempdir"),"/pgram",i,"-",j,"_",k))
            close(res)
            file.remove(tores)
          })
        })
      })

      # merge the data from the different block back into 1 file per i,j combination
      lapply( 1:numberTimeSeries,function(i,...){
        lapply( 1:numberTimeSeries,function(j,..){

          tempFiles <- gsub(".ffData","",grep(paste0("pgram",i,"-",j,"_"),list.files(path = getOption("fftempdir"), full.names = TRUE, recursive = TRUE),value=TRUE)[seq(from=1,to=2*nrow(block),by=2)])

          complexNumber<-as.vector(do.call(cbind,lapply(tempFiles,function(File){
            ffload(File,overwrite =TRUE)
            res1 <- complex(real=res[1,],imaginary=res[2,])
            tores <- filename(res)
            close(res)
            file.remove(tores)
            return(res1)
          })))
          # Smooth inverse spectral density matrix
          complexNumber <- kernapply(complexNumber,kernel("modified.daniell",numberTimeSeries*2))
          res <- ff(rbind(Re(complexNumber),Im(complexNumber)),dim=c(2,length(complexNumber)),vmode="double")
          tores <- filename(res)
          ffsave(res,file=paste0(getOption("fftempdir"),"/pgram",i,"-",j))
          close(res)
          file.remove(tores)
        })
      })

      # remove the block files
      file.remove(grep(paste0("_"),list.files(path = getOption("fftempdir"), full.names = TRUE, recursive = TRUE),value=TRUE))

      # Partial spectral coherence and summary statistic
      S <- do.call(cbind,lapply( 1:numberTimeSeries,function(j,...){
        ffload(paste0(getOption("fftempdir"),"/pgram",j,"-",j),overwrite =TRUE)
        JJ <- complex(real=res[1,],imaginary=res[2,])
        tores <- filename(res)
        close(res)
        file.remove(tores)
        S1 <- unlist(lapply( j:numberTimeSeries,function(i,...){
          ffload(paste0(getOption("fftempdir"),"/pgram",i,"-",j),overwrite =TRUE)
          IJ <- complex(real=res[1,],imaginary=res[2,])
          tores <- filename(res)
          close(res)
          file.remove(tores)

          ffload(paste0(getOption("fftempdir"),"/pgram",i,"-",i),overwrite =TRUE)
          II <- complex(real=res[1,],imaginary=res[2,])
          tores <- filename(res)
          close(res)
          file.remove(tores)

          PSC=-IJ/sqrt(abs(II*JJ))
          return(max(abs(PSC)^2,na.rm=T))
        }))
        return(c(rep(0,numberTimeSeries-length(S1)),S1))
      }))



      # Order summary statistic ignoring diagonals
      diag(S)<-0
      Q1 <- order(S, decreasing=T)

      #############
      # Begin process of fitting constrained VAR models and
      # evaluating BIC. [Davis et al. Appendix A.1]
      #############
      print('Fitting constrained VAR models')

      # Range of model order to be examined
      if(is.null(Ms)){Ms <- (floor(numberTimeSeries/2)):floor(numberTimeSeries^2/4)}
      BIC=NULL
      for(M in Ms){
        print(paste("M=",M,", p=",p))
        # Make array for off diag VAR coeffs.
        # 1 for coef, 0 for no coef.
        A0 <- array(0, dim=c(numberTimeSeries,numberTimeSeries))
        if(M>0) A0[Q1[1:M]]=1
        A0 <- A0 + t(A0) + diag(numberTimeSeries)

        # Construct constraint matrix for constrained VAR model.


        coordonateR <- do.call(rbind,lapply(1:(numberTimeSeries+2*M),function(i,...){
          do.call(rbind,lapply(1:p,function(j,...){
            c(which(A0==1)[i]+(j-1)*numberTimeSeries^2,((j-1)*(numberTimeSeries+2*M)+i))
          }))
        }))
        R <- matrix(data=0 , nrow=numberTimeSeries^2*p, ncol=(numberTimeSeries+2*M)*p)
        R[coordonateR]=1

        ##### Estimate AR coefficeints ######
        # Iterate estimates of coefs and cov matrix

        A <-  lapply(1:p,matrix,data=0, nrow=numberTimeSeries, ncol=numberTimeSeries)
        A[[1]] <- diag(1,numberTimeSeries,numberTimeSeries)

        firstEval <- sVAR_BIC(pFunction=p, RFunction=R, A=A, BIC_weight=(numberTimeSeries+2*M)*p)
        BIC <- c(BIC, firstEval$BIC)




        p1 = p
        M1 = Ms[which(BIC==min(BIC), arr.ind=T)]

        # If new BIC is lowest so far, save outputs:
        if(BIC[which(Ms==M)]==BIC[which(Ms==M1)]){
          A1 <- firstEval$A
          alpha1 <- firstEval$alpha
          Sigma1 <- firstEval$Sigma
          invSigma1 <- firstEval$invSigma
          R1 <- firstEval$R
          y1 <- firstEval$y
        }

        ### Stopping Criterion ###
        if(length(BIC)>4){
          if(sum(tail(BIC,4)>min(BIC))==4){break}
        }
      }



      ###############
      print(paste0("Stage 1 Complete: Min(BIC) at M=", M1,"."))




      ##### STAGE 2 ########

      # Calculate standard errors
      Yy <- data[(p1+1):N0,]
      if(p1>1)Yy <- cbind(Yy,do.call(cbind,lapply(1:(p1-1),function(i,...)return(data[(p1+1-i):(N0-i),]))))
      Ycov <- cov(Yy)
      SE <- sqrt(diag(R1 %*% solve(t(R1) %*% kronecker(Ycov, invSigma1) %*% R1) %*% t(R1)))
      # Place standard errors in matrices corresponding to VAR coefficients

      Ase<-lapply(1:p1,function(i,...){
        matrix(SE[((i-1)*numberTimeSeries^2+1):(i*(numberTimeSeries^2))], nrow=numberTimeSeries, ncol=numberTimeSeries)
      })


      # Calculate t-statistics
      tijk <- do.call(rbind,lapply(1:p1,function(i,...)A1[[i]]/Ase[[i]]))

      # Order t-statistics
      Q2 <- order(abs(tijk), decreasing=T)

      ##### Stage 2 Model Constrained VAR Fitting #####
      #
      # Part 1: Coarse selection of ms.
      # Part 2: Fine selection of ms.
      #
      ############### STAGE 2 PART 1 ################
      print('Stage 2 Part 1')
      # Coarse selection of ms
      if(is.null(ms)){
        if(is.null(ms_start)){ms_start <- (numberTimeSeries+2*M1)*p1-round(numberTimeSeries/2)}
        ms <-  seq(ms_start,p1*numberTimeSeries,-5)
        stage2part1=TRUE
      }else{
        stage2part1=FALSE
      }
      #############

      if(stage2part1){
        BIC2=NULL
        for(m in ms){
          print(paste("m=",m))
        #############

          # Make array for VAR coeffs: 1 for coef, 0 for no coef
          A0 <- array(0, dim=c((numberTimeSeries*p1),numberTimeSeries))
          A0[abs(tijk) >= abs(tijk[Q2[m]]) ]=1

          # Construct constraint matrix for constrained VAR model

          R <- do.call(cbind,lapply(1:p1,function(j,...){
            mA0=sum(A0[((j-1)*numberTimeSeries+1):(j*numberTimeSeries),])
            if(mA0>0){
              do.call(cbind,lapply(1:mA0,function(i,...){
                Rtemp <- rep(0,numberTimeSeries^2*p1)
                Rtemp[which(A0[((j-1)*numberTimeSeries+1):(j*numberTimeSeries),]==1)[i]+(j-1)*numberTimeSeries^2]=1
              return(Rtemp)
                }))
            }
          }))

          #### Estimate coefficeints #####
          ### Same procedure as Part 1 ###
          A <-  lapply(1:p1,matrix,data=0, nrow=numberTimeSeries, ncol=numberTimeSeries)
          A[[1]] <- A0[1:numberTimeSeries,]

          BIC2 <- c(BIC2 , sVAR_BIC(pFunction=p1, RFunction=R, A=A, BIC_weight=m)$BIC)

          ### Stopping Criterion ###
          if(length(BIC2)>3){
            if(sum(tail(BIC2,1)>min(BIC2))==1){break}
          }

        }
        # Store Results
        ms1 <- ms[1:(length(BIC2)-2)]
        BIC2_1 <- BIC2[1:(length(BIC2)-2)]
      }else{
        ms1 <- NULL
        BIC2_1 <- NULL
      }


      ############### STAGE 2 PART 2 ################
      print('Stage 2 Part 2')
      # Fine selection of ms.
      if(stage2part1){
        ms <-  seq(ms[length(BIC2_1)]-1,ms[length(BIC2_1)]-15,-1)
      }
      #############
      # Same proceedure as S2P1
      #############
      BIC2=matrix(ncol=0, nrow=1)
      for(m in ms){
        print(paste("m=",m))
        #############


        # Make array for VAR coeffs: 1 for coef, 0 for no coef
        A0 <- array(0, dim=c((numberTimeSeries*p1),numberTimeSeries))
        A0[abs(tijk) >= abs(tijk[Q2[m]]) ]=1

        # Construct constraint matrix for constrained VAR model

        R <- do.call(cbind,lapply(1:p1,function(j,...){
          mA0=sum(A0[((j-1)*numberTimeSeries+1):(j*numberTimeSeries),])
          if(mA0>0){
            do.call(cbind,lapply(1:mA0,function(i,...){
              Rtemp <- rep(0,numberTimeSeries^2*p1)
              Rtemp[which(A0[((j-1)*numberTimeSeries+1):(j*numberTimeSeries),]==1)[i]+(j-1)*numberTimeSeries^2]=1
            return(Rtemp)
              }))
          }
        }))

        #### Estimate coefficeints #####
        finalEval <- sVAR_BIC(pFunction=p1, RFunction=R, A=A, BIC_weight=m,conv=fconverge)
        BIC2 <- c(BIC2 , finalEval$BIC)


        # If new BIC is lowest so far, save outputs:
        if(tail(BIC2,1)==min(BIC2)){
          m2 <- m
          A2 <- finalEval$A
          alpha2 <- finalEval$alpha
          Sigma2 <- finalEval$Sigma
          invSigma2 <- finalEval$invSigma
          R2 <- finalEval$R
          y2 <- finalEval$y
        }

        ### Stopping Criterion ###
        if(length(BIC2)>5){
          if(sum(tail(BIC2,5)>min(BIC2))==5){break}
        }

        ###############
      } # End Stage 2 Part 2
      ###############
      print('Finish')

      BIC2 <- c(BIC2_1,BIC2)
      ms2 <- c(ms1,ms)[1:length(BIC2)]

      return(list("coef"=A2,"Order"=c(p1,M1,m2),"ErrCov"=Sigma2,"R"=R2,"BIC1"=BIC,"BIC2"=BIC2,"ms"=ms2,"Ms"=Ms[1:length(BIC)]))
    }