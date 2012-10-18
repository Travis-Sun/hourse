#-*- coding: utf-8 -*-
#coding==utf-8

#relation between editor and distirct
#Mingjia3 <- subset(lidata, as.numeric(factor(lidata$name))==6); Mingjia3
#examing
#choose(365,40)*factorial(40) / 365**40
#hist(rbinom(10000,size=40,prob=.9))
#hist(rpois(1000,1))
#lines(density(rpois(1000,1)))

#pic setting
Sys.setlocale(locale = 'C')
library(ggplot2)

#lijia
lihourse <- read.csv("D:\\HOME\\R\\hourse\\lihourse.summary.2012-07-20.csv",
                     sep=',', header=FALSE)
lidata <- data.frame(lihourse)
names(lidata) <- c('detailurl','totalprice','name','area','V1','buildyear', 'float','direct',
                   'downdate','V2','connector','V5','connectorphone','V6', 'address',
                   'title','unitprice','structure'
                   )
lidata$downdate <- as.Date(lidata$downdate, format="%Y.%m.%d")
head(lidata)

#class(lidata$unitprice)
#class(lidata$area)
#lidata$unitprice <- as.numeric(levels(lidata$unitprice)[lidata$unitprice])
#lidata$area <- as.numeric(levels(lidata$area)[lidata$area])
head(lidata[lidata$name=="望都家园",])

head(lidata[lidata$name=="望都家园"&lidata$structure=="2室2厅",])

qplot(downdate, unitprice,
      data=lidata[lidata$name=="望都家园"&lidata$structure=="2室2厅",],
      geom=c("point","smooth"), xlab="时间", ylab="单价",
      main="望都家园2室2厅均价"
      )

qplot(downdate, unitprice,
      data=lidata[lidata$name=="望都家园"&lidata$structure=="1室1厅",],
      geom=c("point","smooth"), xlab="时间", ylab="单价",
      main="望都家园1室1厅均价"
      )

qplot(downdate, unitprice,
      data=lidata[lidata$name=="名佳花园三区"&lidata$structure %in% c("3室2厅", "3室1厅"),],
      geom=c("point","smooth"), xlab="时间", ylab="单价",
      main="名佳花园3室2厅均价"
      )

qplot(downdate, unitprice,
      data=lidata[lidata$name=="望都家园"&lidata$structure %in% c("3室2厅", "3室1厅"),],
      geom=c("point","smooth"), xlab="时间", ylab="单价",
      main="望都家园3室均价"
      )

qplot(downdate, unitprice,
      data=lidata[lidata$name=="名佳花园三区"&lidata$structure=="2室2厅",],
      geom=c("point","smooth"), xlab="时间", ylab="单价",
      main="名佳花园2室2厅均价"
      )

qplot(downdate, unitprice,
      data=lidata[lidata$name=="名佳花园三区"&lidata$structure=="1室1厅",],
      geom=c("point","smooth"), xlab="时间", ylab="单价",
      main="名佳花园1室1厅均价"
      )

qplot(name, unitprice,
      data=lidata[lidata$structure=="3室2厅"&lidata$downdate>"2012-01-01",],
      geom="histogram")

likedirect <- c("名佳花园三区","名流花园兰苑","名流花园梅苑","名流花园竹苑",
                "名流花园菊苑","名流花园欧风苑","望都家园","西湖新村")
hourse3 <- lidata[lidata$structure=="3室2厅"&lidata$name %in%likedirect,]
hourse3$name <- as.factor(as.character(hourse3$name))
plot(hourse3$name, hourse3$unitprice, main="3室2厅价格", xlab="小区", ylab="单价")
levels(hourse3$name)

p <- ggplot(data=hourse3,aes(x=area,y=unitprice,colour=factor(name)))
p + geom_point() + geom_boxplot()


likedirect <- c("名佳花园三区","望都家园","西湖新村")
hourse3 <- lidata[lidata$structure=="3室2厅" & lidata$downdate>"2012-01-01" &
                  lidata$name %in%likedirect,]# &lidata$area<140,]
hourse3$name <- as.factor(as.character(hourse3$name))
levels(hourse3$name)
head(hourse3)

p <- ggplot(data=hourse3,aes(x=name,y=unitprice,colour=factor(name)))
p + geom_point() + geom_boxplot()

likedirect <- c("名佳花园三区","望都家园","西湖新村")
hourse3 <- lidata[lidata$structure=="3室2厅" & #lidata$downdate>"2012-01-01" &
                  lidata$name %in%likedirect,]# &lidata$area<140,]
hourse3$name <- as.factor(as.character(hourse3$name))
levels(hourse3$name)
p <- ggplot(data=hourse3,aes(x=totalprice,y=unitprice,colour=factor(name)))
p + geom_point() + geom_smooth()

p <- ggplot(data=hourse3,aes(x=area,y=totalprice,colour=factor(name)))
p + geom_point() + geom_smooth()

p <- ggplot(data=hourse3,aes(x=downdate,y=unitprice,colour=factor(name)))
p + geom_point() + geom_smooth()



p <- ggplot(data=hourse3,aes(x=area,y=unitprice,colour=factor(name)))
p + geom_point() + geom_smooth()


likedirect <- c("名佳花园三区","望都家园","西湖新村")
hourse3 <- lidata[lidata$structure=="3室2厅" &# lidata$downdate>"2012-01-01" &
                  lidata$name %in%likedirect,]# &lidata$area<140,]
hourse3$name <- as.factor(as.character(hourse3$name))
levels(hourse3$name)
p <- ggplot(data=hourse3,aes(x=downdate,y=unitprice,colour=factor(name)))
p + geom_point() + geom_smooth()

     

