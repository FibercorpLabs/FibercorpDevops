############################################################################
#
# Functions used to analyze vdbench output data from All-Flash Array tests
#
############################################################################
suppressMessages(require(KernSmooth))
invisible(Sys.setlocale(category="LC_ALL",locale="en_US")) 
library("getopt",warn.conflicts=FALSE)
library("plotrix",warn.conflicts=FALSE)
library("gplots",warn.conflicts=FALSE)

simpleCap <- function(x) {
  s <- strsplit(x, " ")[[1]]
  paste(toupper(substring(s, 1, 1)), substring(s, 2),
        sep = "", collapse = " ")
}

# read.vdb() --
#   Parses vdbench output flatfile.html into an R Data Frame
# Arguments --	
#        file : Path to vdbench flatfile from test run
read.vdb = function(file,...) {
  col.names = c("tod","run","interval","reqrate","rate",
                 "MBps","iosz","rdmeaspct","resp","read_resp",
                 "write_resp","resp_max","resp_std","xfersize","threads",
                 "rdreqpct","rhpct","whpct","seekpct","lunsize",
                 "vers","compr","dedup","que","cpu_used",
                 "cpu_user","cpu_kernel","cpu_wait","cpu_idle")

  tbl = read.table(file=file,col.names=col.names, 
                  skip=41,na.strings="n/a",comment.char=">",...)
  tbl = tbl[grep("avg",tbl$interval,invert=TRUE),]
  
  tbl$run = factor(tbl$run)
  tbl$seekpct[is.na(tbl$seekpct)] = 0
  if (!is.integer(tbl$interval)) {
    tbl$interval = as.integer(levels(tbl$interval)[as.integer(tbl$interval)])
  }
  
  return(tbl)
}


# summary.vdb()	--
#   Summarizes vdbench Data Frame by running a summary function (by default
#		uses mean) across the various curve load points for IOPS, MB/s, and latency. 
#   Returns the summarized Data Frame for use by other functions.
# Arguments --
# 	        v : vdbench Data Frame (required)
#	     warmup : warmup time in the tests (defaults to 15 seconds if missing)
#	        fun : function used to summarize results (defaults to "mean" if 
#               missing)
#	     maxvdb : value used by vdbench to represent uncontrolled maximum 
#               requested rate
summary.vdb <- function(v=NULL, warmup = 15, fun = mean, maxvdb = 999977) {
  
  if(dim(v)[1]==0|is.null(v)) return()
  
  sz = sort(unique(v$iosz))
  rd = sort(unique(v$rdreqpct))
  th = sort(unique(v$threads))
  rr = sort(unique(v$run))
  l = length(sz) * length(th) * length(rd)
  
  i = 1
  iosz = list(rep(0,l))
  rpct = list(rep(0,l))
  thrd = list(rep(0,l))
  iops = list(rep(list(rep(0,length(rr)-1)),l))
  MBps = list(rep(list(rep(0,length(rr)-1)),l))
  resp = list(rep(list(rep(0,length(rr)-1)),l))
  
  for (s in sz) {
    for (r in rd) {
      for (t in th) {
        iosz[[1]][i] = s
        rpct[[1]][i] = r
        thrd[[1]][i] = t
        x <- subset(v,interval>warmup&iosz==s&threads==t&rdreqpct==r&reqrate!=maxvdb)
        iops[[1]][[i]] = sapply(split(x$rate,x$reqrate),fun)
        MBps[[1]][[i]] = sapply(split(x$MBps,x$reqrate),fun)
        resp[[1]][[i]] = sapply(split(x$resp,x$reqrate),fun)
        i = i+1
      }
    }
  }
  
  ans = data.frame(iosz = iosz[[1]], rpct = rpct[[1]], thrd = thrd[[1]])
  ans$iops = iops[[1]]
  ans$MBps = MBps[[1]]
  ans$resp = resp[[1]]
  filt = sapply(ans$iops,length) >= 2
  return(ans[filt,])              
}

# vdb.workload() --
#   Return human-readable string describing the workload
# Arguments --  
#        v : vdbench data frame
vdb.workload = function(v) {
  
  io = round(mean(v$iosz)/2^10) ; io = io[io!=0]
  str.io = paste0(io,"KB") ### IO size in KB
  sk = unique(v$seekpct) 
  str.sk = ifelse(sk,ifelse(sk==100,"Random",
                            paste0(sk,"% Random")),"Sequential")
  rd = unique(v$rdreqpct)
  str.rd = ifelse(rd,ifelse(rd==100,"Read",
                            paste0(rd,"% Read")),"Write")
  spd = unique(unlist(lapply(levels(factor(v$run)),
                      function(x){as.numeric(unlist(strsplit(x,"[[:punct:]]"))[3])})))
  str.spd = ifelse(is.na(spd),"Full Throttle",
                   paste0(spd,"% Throttle"))
  str.que = paste0(signif(mean(v$que),3)," Mean Queue Depth")
   
  work = paste(str.io,str.sk,str.rd,";",str.spd,";",str.que)
  return(work)
}

# print.vdb.precondition() -- 
#   Generates plots of throughput and latency over total GiB for the 
#   preconditioning runs. 
# Arguments --
#	    	 data : vdbench Data Frame (required). The data is expected to have 
#               two runs, one named "fill" and the other named "age" as present
#               in the All-Flash Array vdbench test specification.
#	   outfile	: path to PDF file used to print the graphs. If missing, the 
#               graph will be sent to the default graphical device (useful for
#               interactive calls)
print.vdb.precondition = function(data=NULL,outfile=NULL) {
  
  if(dim(data)[1]==0|is.null(data)) return()
  
  fill=subset(data,grepl("^fill",run))
  age=subset(data,grepl("^age",run))
  
  if(!is.null(outfile)) {
    pdf(outfile,title="Array Preconditioning Sequence",width=11,height=8.5)
  }
  op=par(mfrow=c(2,2))
  
  tot=cumsum(fill$MBps)/2^10
  wrk=vdb.workload(fill)
  plot(tot,fill$MBps,pch=".",col="LightBlue",
       main="Precondition Sequence: Fill Throughput over Time",
       ylab="MB/s",xlab="Total GiB Written",cex.sub=0.8,
       sub=paste0(wrk," (MeanTput=",signif(mean(fill$MBps),4)," MB/s)"))
  lines(smooth.spline(tot,fill$MBps,df=30),col="DarkBlue",lwd=3)

  plot(tot,fill$resp,pch=".",col="LightBlue",
       main="Precondition Sequence: Fill Latency over Time",
       ylab="milliseconds",xlab="Total GiB Written",cex.sub=0.8,
       sub=paste0(wrk," (MeanLat=",signif(mean(fill$resp),3),"ms)"))
  lines(smooth.spline(tot,fill$resp,df=30),col="DarkBlue",lwd=3)
  
  tot=cumsum(age$MBps)/2^10
  wrk=vdb.workload(age)
  plot(tot,age$rate,pch=".",col="LightBlue",
       main="Precondition Sequence: Aging IOPS over Time",
       ylab="IOPS",xlab="Total GiB Written",cex.sub=0.8,
       sub=paste0(wrk," (MeanTput=",signif(mean(age$rate),6)," IOPS)"))
  lines(smooth.spline(tot,age$rate,df=30),col="DarkBlue",lwd=3)
  
  plot(tot,age$resp,pch=".",col="LightBlue",
       main="Precondition Sequence: Aging Latency over Time",
       ylab="milliseconds",xlab="Total GiB Written",cex.sub=0.8,
       sub=paste0(wrk," (MeanLat=",signif(mean(age$resp),3),"ms)"))
  lines(smooth.spline(tot,age$resp,df=30),col="DarkBlue",lwd=3)
  
  if(!is.null(outfile)) {
    dev.off()
  }
  par(op)
}


# print.vdb.profile.iops() -- 
#   Prints Latency vs. IOPS by IO Sizes for different Read%
# Arguments --
#           s : Summary vdbench Data Frame (result of summary.vdb() function) 
# 	  outfile : Path to PDF file used to print the graphs. If missing, the graph will
#			          be sent to the default graphical device (useful for interactive calls)
#        lmax : Maximum latency to draw on the plot
#         fit : Draw predicted curve fit (defaults to FALSE)
#         lat : List of latency values at which to report IOPS. Default will 
#               automatically generate values based on observations
print.vdb.profile.iops = function(s=NULL,outfile=NULL,lmax=30,fit=FALSE,
                                  lat=NULL) {

  if(dim(s)[1]==0|is.null(s)) return()
  
  rd = sort(unique(s$rpct))
  th = sort(unique(s$thrd))
  sz = sort(unique(s$iosz))
  generate.latency = is.null(lat)
  
  par(mfrow=c(1,1),mar=c(5,4,4,2)+0.1)
  if(!is.null(outfile)) {
    pdf(outfile,title="Latency vs. IOPS by IO Sizes and Different Read Percent",
    	width=11,height=8.5)
  }
    
  legnam=paste0(rd,"% Read")
  cl=rainbow(length(rd))
  if (length(cl)>1) palette(cl) else palette(rainbow(2))

  for (i in sz) {
    ss=subset(s,iosz==i)
    lgax="" ### ; if(max(unlist(ss$resp)>100)) lgax = "y"
    
    rng=list(x=range(ss$iops),y=range(ss$resp))
    rng$y[2]=min(lmax,rng$y[2])
    
    plot(rng,type="n", log=lgax,
         xlab="IOPS",ylab="Latency (milliseconds)",
         main=paste0("Latency vs. IOPS for ",i/2^10,"K IO Size and ",
                     th," Threads/LUN"),cex.sub=0.75,sub=outfile)
    grid(col="darkgrey",lty=3,lwd=1)
    if(lgax=="y") abline(h=1:10,lty=5,col="darkgreen")
    
    cln=1
    for (r in rd) {
      mask=ss$iosz==i&ss$rpct==r
      tmp = data.frame(x=ss$iops[mask][[1]],y=ss$resp[mask][[1]])
      if(fit) {
        ord = order(tmp$x)
        o = smooth.spline(x=tmp$x[ord],y=tmp$y[ord],cv=TRUE)
        lines(predict(o,seq(min(tmp$x),max(tmp$x),length=1000)),col=cl[cln],lty=3,lwd=2)  
      } 
      lines(tmp,col=cl[cln],lty=1,lwd=3)
      points(tmp,col=cl[cln],lwd=5)
      ### intr=approx(x=tmp$y,y=tmp$x,xout=c(1,1.5,2))
      ### abline(v=intr$y,lty=1,col=cl[cln])
      cln=cln+1
    }
    
    if (generate.latency) {
      r=as.numeric(unlist(ss$resp))
      h=hist(log(r),breaks=20,plot=FALSE)
      lat=signif(exp(h$mids[h$counts>0]),3)
      if (length(lat)>7)
        lat=lat[order(h$count[h$counts>0],decreasing=TRUE)[1:7]]
      lat=sort(lat)
    }
    tput=as.data.frame(t(sapply(split(ss,ss$rpct),
                                function(r) format(round(approx(x=r$resp[[1]],
                                                                y=r$iops[[1]],
                                                                xout=lat)$y,0),
                                                   big.mark=","))))
    tput=data.frame(as.numeric(rownames(tput)),tput)
    names(tput)=c("ReadPct",paste0(lat,"ms"))
    addtable2plot(x=rng$x[1],y=rng$y[2],table=tput,
                  title="IOPS at Target Latency",
                  hlines=TRUE,vlines=TRUE,bg="white",
                  yjust=0,cex=0.8,bty="o",xpad=0.05,ypad=0.35)
    
    legend("topright",legend=legnam,ncol=length(cl),col=cl,bty="n",
           lwd=5,cex=0.6,inset=c(0,-0.03),xpd=TRUE)
  }

  if(!is.null(outfile)) {
    dev.off()
  }

}

# print.vdb.table.iops() -- 
#   Prints IOPS at Varying Latency Threshold by IO Size and Read Percent
# Arguments --
#           s : Summary vdbench Data Frame (result of summary.vdb() function) 
#     outfile : Path to PDF file used to print the graphs. If missing, the graph will
#			          be sent to the default graphical device (useful for interactive calls)
#      breaks : Target number of latency points to display in the table
print.vdb.table.iops = function(s=NULL,outfile=NULL,breaks=40) {
  
  if(dim(s)[1]==0|is.null(s)) return()
  
  rd = sort(unique(s$rpct))
  th = sort(unique(s$thrd))
  sz = sort(unique(s$iosz))
  
  par(mfrow=c(1,1),mar=c(5,4,4,2)+0.1)
  if(!is.null(outfile)) {
    pdf(outfile,
        title="IOPS at Varying Latency Threshold by IO Size and Read Percent",
        width=8.5,height=11)
  }
  
  for (i in sz) {
    ss=subset(s,iosz==i)
    r=as.numeric(unlist(ss$resp))
    lat=signif(exp(hist(log(r),breaks=breaks,plot=FALSE)$mids),3)
    lat=lat[lat>=min(r) & lat<=max(r)]
    tput=as.data.frame(sapply(split(ss,ss$rpct),
                                function(r) format(round(approx(x=r$resp[[1]],
                                                                y=r$iops[[1]],
                                                                xout=lat)$y,0),
                                                   big.mark=",")))
    rownames(tput)=lat
    tput=data.frame(as.numeric(rownames(tput)),tput)
    names(tput)=c("Latency",paste0(rd,"% Read"))
    textplot(tput,halign="center",valign="top",show.row=FALSE,cex=0.90)
    title(main=paste0("Table of IOPS at Given Latency for ",
                      i/2^10,"K IO Size and ",th," Threads/LUN"),
          sub=outfile,cex.main=1.25,cex.sub=0.75)
  }
  
  if(!is.null(outfile)) {
    dev.off()
  }
}


# print.vdb.profile.mbps() --
#   Prints Latency vs. MB/s by IO Sizes for different Read%
# Arguments --
# 	        s	: Summary vdbench Data Frame (result of summary.vdb() function)
# 	  outfile	: path to PDF file used to print the graphs. If missing, the graph will
#			          be sent to the default graphical device (useful for interactive calls)
#        lmax : Maximum latency to draw on the plot
#         fit : Draw predicted curve fit (defaults to FALSE)
#         lat : List of latency values at which to report MB/s. Default will 
#               automatically generate values based on observations
print.vdb.profile.mbps = function(s=NULL,outfile=NULL,lmax=30,fit=FALSE,
                                  lat=NULL) {
  
  if(dim(s)[1]==0|is.null(s)) return()
  
  rd = sort(unique(s$rpct))
  th = sort(unique(s$thrd))
  sz = sort(unique(s$iosz))
  generate.latency = is.null(lat)

  par(mfrow=c(1,1),mar=c(5,4,4,2)+0.1)
  if(!is.null(outfile)) {
    pdf(outfile,title="Latency vs. MB/s by IO Sizes and Different Read Percent",
    	width=11,height=8.5)
  }
    
  legnam=paste0(rd,"% Read")
  cl=rainbow(length(rd))
  if (length(cl)>1) palette(cl) else palette(rainbow(2))

  for (i in sz) {
    ss=subset(s,iosz==i)
    lgax="" ### ; if(max(unlist(ss$resp)>100)) lgax = "y"

    rng=list(x=range(ss$MBps),y=range(ss$resp))
    rng$y[2]=min(lmax,rng$y[2])
    
    plot(rng,type="n", log=lgax,
         xlab="MB/s",ylab="Latency (milliseconds)",
         main=paste0("Latency vs. MB/s for ",i/2^10,"K IO Size and ",
                     th," Threads/LUN"),cex.sub=0.75,sub=outfile)
    grid(col="darkgrey",lty=3,lwd=1)
    if(lgax=="y") abline(h=1:10,lty=5,col="darkgreen")
        
    cln=1
    for (r in rd) {
      mask=ss$iosz==i&ss$rpct==r
      tmp = data.frame(x=ss$MBps[mask][[1]],y=ss$resp[mask][[1]])
      if(fit) {
        ord = order(tmp$x)
        o = smooth.spline(x=tmp$x[ord],y=tmp$y[ord],cv=TRUE)
        lines(predict(o,seq(min(tmp$x),max(tmp$x),length=1000)),col=cl[cln],lty=3,lwd=2)  
      } 
      lines(tmp,col=cl[cln],lty=1,lwd=3)
      points(tmp,col=cl[cln],lwd=5)
      cln=cln+1
    }
    
    if (generate.latency) {
      r=as.numeric(unlist(ss$resp))
      h=hist(log(r),breaks=20,plot=FALSE)
      lat=signif(exp(h$mids[h$counts>0]),3)
      if (length(lat)>7)
        lat=lat[order(h$count[h$counts>0],decreasing=TRUE)[1:7]]
      lat=sort(lat)
    }
    tput=as.data.frame(t(sapply(split(ss,ss$rpct),
                                function(r) format(round(approx(x=r$resp[[1]],
                                                                y=r$MBps[[1]],
                                                                xout=lat)$y,0),
                                                   big.mark=","))))
    tput=data.frame(as.numeric(rownames(tput)),tput)
    names(tput)=c("ReadPct",paste0(lat,"ms"))
    addtable2plot(x=rng$x[1],y=rng$y[2],table=tput,title="MB/s at Target Latency",
                  hlines=TRUE,vlines=TRUE,bg="white",yjust=0,cex=0.7,bty="o")
    
    legend("topright",legend=legnam,ncol=length(cl),col=cl,bty="n",
           lwd=5,cex=0.6,inset=c(0,-0.03),xpd=TRUE)
  }

  if(!is.null(outfile)) {
    dev.off()
  }
  
}

# print.vdb.table.mbps() -- 
#   Prints MB/s at Varying Latency Threshold by IO Size and Read Percent
# Arguments --
#           s : Summary vdbench Data Frame (result of summary.vdb() function) 
#     outfile : Path to PDF file used to print the graphs. If missing, the graph will
#  		          be sent to the default graphical device (useful for interactive calls)
#      breaks : Target number of latency points to display in the table
print.vdb.table.mbps = function(s=NULL,outfile=NULL,breaks=40) {
  
  if(dim(s)[1]==0|is.null(s)) return()
  
  rd = sort(unique(s$rpct))
  th = sort(unique(s$thrd))
  sz = sort(unique(s$iosz))
  
  par(mfrow=c(1,1),mar=c(5,4,4,2)+0.1)
  if(!is.null(outfile)) {
    pdf(outfile,
        title="MB/s at Varying Latency Threshold by IO Size and Read Percent",
        width=8.5,height=11)
  }
  
  for (i in sz) {
    ss=subset(s,iosz==i)
    r=as.numeric(unlist(ss$resp))
    lat=signif(exp(hist(log(r),breaks=breaks,plot=FALSE)$mids),3)
    lat=lat[lat>=min(r) & lat<=max(r)]
    tput=as.data.frame(sapply(split(ss,ss$rpct),
                              function(r) format(round(approx(x=r$resp[[1]],
                                                              y=r$MBps[[1]],
                                                              xout=lat)$y,0),
                                                 big.mark=",")))
    rownames(tput)=lat
    tput=data.frame(as.numeric(rownames(tput)),tput)
    names(tput)=c("Latency",paste0(rd,"% Read"))
    textplot(tput,halign="center",valign="top",show.row=FALSE,cex=0.90)
    title(main=paste0("Table of MB/s at Given Latency for ",
                      i/2^10,"K IO Size and ",th," Threads/LUN"),
          sub=outfile,cex.main=1.25,cex.sub=0.75)
  }
  
  if(!is.null(outfile)) {
    dev.off()
  } 
}

# print.vdb.profile.queue()	--
#   Prints characterization of IOPS and Latency as a function of observed queue depth 
#		for different IO sizes.
# Arguments --
# 	        d : vdbench Data Frame that contains a single run type (e.g., "small")
#	    outfile : path to PDF file used to print the graphs. If missing, the graph will
#			  	      be sent to the default graphical device (useful for interactive calls)
#	     warmup : warmup time in the tests (defaults to 15 seconds if missing)
#	     maxvdb : value used by vdbench to represent uncontrolled maximum requested rate
#	       bins : how many different queue depth boxes to draw (defaults to 128)
#	       minq : minimum queue depth to consider
#	       maxq : maximum queue depth to consider
print.vdb.profile.queue = function(d=NULL,outfile=NULL,warmup=5,
                                   maxvdb=999977,bins=128,minq=8,maxq=512) {
  
  if(dim(d)[1]==0|is.null(d)) return()
  
  if(!is.null(outfile)) {
    pdf(outfile,title="Array Queue Depth",width=11,height=8.5)
  }
  op=par(mfrow=c(2,1),mar=c(5,4,4,2)+0.1)
  
  for(sz in sort(unique(d$iosz))) {
    s = subset(d,que>=minq&que<=maxq&interval>warmup&reqrate!=maxvdb&iosz==sz)
    bucket = floor(max(s$que)/bins)
    s$que = bucket*ceiling(s$que/bucket)
    
    b = boxplot(rate~que,s,outline=TRUE,range=0,col="lightblue",pch="o",
                main=paste0("IOPS versus Array Queue Length for ",sz/1024,"KB Requests"),
                xlab="Queue Length",ylab="IOPS",cex.sub=0.75,sub=outfile)
    ss=smooth.spline(b$stats[3,],w=b$n,df=10)
    peak=min(ss$x[ss$y==max(ss$y)])
    lines(ss,col="darkblue",lwd=5)
    abline(v=peak,col="darkred",lwd=3,lty=1)
    grid(nx=round(max(s$que)/10),ny=round(max(s$rate)/10000),col="darkgrey",lty=3,lwd=1)
    legend("topleft",ncol=2,bty="n",lty=1,lwd=5,cex=0.7,inset=c(0,-0.125),xpd=TRUE,
           legend=c("1st to 3rd Quartiles","Smoothed Medians"),
          col=c("lightblue","darkblue"))
  
    b = boxplot(log2(resp*1000)~que,s,outline=TRUE,range=0,col="lightblue",pch="o",
                main=paste0("Latency versus Array Queue Length for ",sz/1024,"KB Requests"),
                xlab="Queue Length",ylab="Log2 Latency (microseconds)",cex.sub=0.75,sub=outfile)
    lines(smooth.spline(b$stats[3,],w=b$n,df=10),col="darkblue",lwd=5)
    abline(v=peak,col="darkred",lwd=3,lty=1)
    grid(nx=round(max(s$que)/10),ny=round(max(log2(s$resp*1000))),col="darkgrey",lty=3,lwd=1)
    abline(h=log2(1:10*1000),lty=4,lwd=2,col="darkgreen")
    legend("topleft",ncol=3,bty="n",lty=1,lwd=5,cex=0.7,inset=c(0,-0.125),xpd=TRUE,
           legend=c("1st to 3rd Quartiles","Smoothed Medians","Latency Levels"),
           col=c("lightblue","darkblue","darkgreen"))
  }
  
  if(!is.null(outfile)) {
    dev.off()
  }
  invisible(par(op))
  
}


# print.vdb.profile.rdpct()	--
#   Prints characterization of IOPS and Latency as a function
#		of IO Size across all curve points (queue depths).
# Arguments --
#           d : vdbench Data Frame that contains a single run type (e.g., "small")
#	    outfile : path to PDF file used to print the graphs. If missing, the graph will
#			  	      be sent to the default graphical device (useful for interactive calls)
#	     warmup : warmup time in the tests (defaults to 15 seconds if missing)
#	     maxvdb : value used by vdbench to represent uncontrolled maximum requested rate
#	     bucket : how many different queue depths per summary point
#	       minq : minimum queue depth to consider
#	       maxq : maximum queue depth to consider
print.vdb.profile.rdpct = function(d=NULL,outfile=NULL,warmup=5,maxvdb=999977,bucket=4,minq=8,maxq=512) {
  
  if(dim(d)[1]==0|is.null(d)) return()
  
  if(!is.null(outfile)) {
    pdf(outfile,title="Array IOPS and Latency by Read Percentage",width=11,height=8.5)
  }
  op=par(mfrow=c(1,2),mar=c(5,4,5,2)+0.1)
  
  for(sz in sort(unique(d$iosz))) {
    s = subset(d,que>=minq&que<=maxq&interval>warmup&reqrate!=maxvdb&iosz==sz)
  
    b = boxplot(rate~rdreqpct,s,outline=FALSE,range=0,varwidth=FALSE,notch=FALSE,
                main=paste0("IOPS versus Read Percentage for ",sz/1024,"KB Requests"),
                col="lightblue",xlab="Percent Read",ylab="IOPS",cex.sub=0.75,sub=outfile)
    o = smooth.spline(b$stats[3,],w=b$n)
    lines(predict(o,seq(min(o$x),max(o$x),length=100)),col="darkblue",lwd=7)
    grid(col="darkgrey",lty=3,lwd=1)
    legend("topleft",bty="n",lty=1,lwd=5,cex=0.7,inset=c(0,-0.04),xpd=TRUE,
            legend=c("1st to 3rd Quartiles","Smoothed Medians"),
            col=c("lightblue","darkblue"),ncol=2)
  
    b = boxplot(resp~rdreqpct,s,outline=FALSE,range=0,varwidth=FALSE,notch=FALSE,
                main=paste0("Latency versus Read Percentage for ",sz/1024,"KB Requests"),
                col="lightblue",xlab="Percent Read",ylab="Latency (milliseconds)",cex.sub=0.75,sub=outfile)
    o = smooth.spline(b$stats[3,],w=b$n)
    lines(predict(o,seq(min(o$x),max(o$x),length=100)),col="darkblue",lwd=7)
    grid(col="darkgrey",lty=3,lwd=1)
    legend("topleft",bty="n",lty=1,lwd=5,cex=0.7,inset=c(0,-0.04),xpd=TRUE,
           legend=c("1st to 3rd Quartiles","Smoothed Medians"),
           col=c("lightblue","darkblue"),ncol=2)
  }
  
  if(!is.null(outfile)) {
    dev.off()
  }
  invisible(par(op))
  
}

# print.vdb.profile.rdcurve() --
#   Plot Latency vs. MB/s for different IO sizes. 
# Arguments --
#           s : Summary vdbench Data Frame (result of summary.vdb() function) for a single
#               type of test (e.g., run==small)
#     outfile : path to PDF file used to print the graphs. If missing, the graph will
#			          be sent to the default graphical device (useful for interactive calls)
#        lmax : Maximun latency to draw on the curve (default 30ms)
#         fit : Draw predicted curve fit (defaults to FALSE)
print.vdb.profile.rdcurve = function(d=NULL,outfile=NULL,lmax=30,fit=FALSE) {
  
  if(dim(d)[1]==0|is.null(d)) return()
  
  if(!is.null(outfile)) {
    pdf(outfile,title="Performance by IO Size for Different Read Percentages",width=11,height=8.5)
  }
  op=par(mfrow=c(1,1),mar=c(5,4,4,2)+0.1)
  
  for (r in sort(unique(d$rpct))) {
    ss=subset(d,rpct==r)
    lgax="" ### ; if(max(unlist(ss$resp)>100)) lgax = "y"
    
    rng=list(x=range(ss$MBps),y=range(ss$resp))
    rng$y[2]=min(lmax,rng$y[2])
    
    plot(rng,type="n",log=lgax,
         main=paste0("Latency vs. MiB/s for ",r,"% Reads"),
         xlab="MiB/s",ylab="Mean Latency (milliseconds)",cex.sub=0.75,sub=outfile)
    grid(col="darkgrey",lty=3,lwd=1)
    if (lgax == "y") abline(h=1:10,lty=4,col="darkgreen")
    
    cln=1
    sz=sort(unique(ss$iosz))
    l=length(sz)
    cl=rainbow(l)
    legnam=rep("",l)
    legcol=rep("",l)
    
    lgn=1
    cln=1
    for (i in sz) {
      tmp = data.frame(x=ss$MBps[ss$iosz==i][[1]],y=ss$resp[ss$iosz==i][[1]])
      if(fit) {
        ord = order(tmp$x)
        o = smooth.spline(x=tmp$x[ord],y=tmp$y[ord],cv=TRUE)
        lines(predict(o,seq(min(tmp$x),max(tmp$x),length=1000)),col=cl[cln],lty=3,lwd=2)  
      } 
      lines(tmp,col=cl[cln],lty=1,lwd=3)
      points(tmp,col=cl[cln],lwd=5)
      legnam[lgn]=paste0(i/2^10," KiB")
      legcol[lgn]=cl[cln]
      cln=cln+1
      lgn=lgn+1
    }
    legend("topleft",legend=legnam,bty="n",ncol=length(legcol),
           col=legcol,lty=1,lwd=3,cex=0.7,inset=c(0,-0.03),xpd=TRUE)
  }
  
  if(!is.null(outfile)) {
    dev.off()
  }
  par(op)
}

# print.vdb.sequential.sizes() --
#   Plots array sequential throughput and latency by IO size. Data is based on the highest
#   controlled request rate. One page for Reads, and another for Writes.
# Arguments --
#           d : vdbench Data Frame that contains a single run type (e.g., "small")
#	    outfile : path to PDF file used to print the graphs. If missing, the graph will
#			  	      be sent to the default graphical device (useful for interactive calls)
#	     warmup : warmup time in the tests (defaults to 15 seconds if missing)
#	     maxvdb : value used by vdbench to represent uncontrolled maximum requested rate
#	     bucket : how many different queue depths per summary point
#	       minq : minimum queue depth to consider
#	       maxq : maximum queue depth to consider
print.vdb.sequential.sizes = function(d=NULL,outfile=NULL,warmup=5,maxvdb=999977,bucket=4,minq=8,maxq=512) {
  
  if(dim(d)[1]==0|is.null(d)) return()
  
  if(!is.null(outfile)) {
    pdf(outfile,title="Array Sequential Performance",width=11,height=8.5)
  }
  op=par(mfrow=c(2,1))
  
  d$run = factor(d$run)
  m = max(unlist(lapply(levels(d$run),function(x){as.numeric(unlist(strsplit(x,"[[:punct:]]"))[3])})),na.rm=T)
  rname = paste0(levels(d$run)[1],"_(",m,"%)")
  d = subset(d,run==rname&interval>warmup&que>=minq&que<=maxq)
  
  # Reads
  s = subset(d,rdreqpct==100)
  b = boxplot(MBps~iosz,s,outline=FALSE,
              main=paste0("Sequential Read Throughput by IO Size"),
              col="lightblue",xlab="IO Size",ylab="MB/s",cex.sub=0.75,sub=outfile)
  o = smooth.spline(b$stats[3,],w=b$n)
  lines(predict(o,seq(min(o$x),max(o$x),length=100)),col="darkblue",lwd=7)
  grid(col="darkgrey",lty=3,lwd=1)
  legend("topleft",legend=c("1st to 3rd Quartiles","Smoothed Medians"),
         col=c("lightblue","darkblue"),bty="n",lty=1,lwd=5,cex=0.7,
         ncol=2,inset=c(0,-0.1),xpd=TRUE)
  
  b = boxplot(resp~iosz,s,outline=FALSE,
              main=paste0("Sequential Read Latency by IO Size"),
              col="lightblue",xlab="IO Size",ylab="Latency (milliseconds)",cex.sub=0.75,sub=outfile)
  o = smooth.spline(b$stats[3,],w=b$n)
  lines(predict(o,seq(min(o$x),max(o$x),length=100)),col="darkblue",lwd=7)
  grid(col="darkgrey",lty=3,lwd=1)
  legend("topleft",legend=c("1st to 3rd Quartiles","Smoothed Medians"),
         col=c("lightblue","darkblue"),bty="n",lty=1,lwd=5,cex=0.7,
         ncol=2,inset=c(0,-0.1),xpd=TRUE)
  
  # Writes
  s = subset(d,rdreqpct==0)
  b = boxplot(MBps~iosz,s,outline=FALSE,
              main=paste0("Sequential Write Throughput by IO Size"),
              col="lightblue",xlab="IO Size",ylab="MB/s",cex.sub=0.75,sub=outfile)
  o = smooth.spline(b$stats[3,],w=b$n)
  lines(predict(o,seq(min(o$x),max(o$x),length=100)),col="darkblue",lwd=7)
  grid(col="darkgrey",lty=3,lwd=1)
  legend("topleft",legend=c("1st to 3rd Quartiles","Smoothed Medians"),
         col=c("lightblue","darkblue"),bty="n",lty=1,lwd=5,cex=0.7,
         ncol=2,inset=c(0,-0.1),xpd=TRUE)
  
  b = boxplot(resp~iosz,s,outline=FALSE,
              main=paste0("Sequential Write Latency by IO Size"),
              col="lightblue",xlab="IO Size",ylab="Latency (milliseconds)",cex.sub=0.75,sub=outfile)
  o = smooth.spline(b$stats[3,],w=b$n)
  lines(predict(o,seq(min(o$x),max(o$x),length=100)),col="darkblue",lwd=7)
  grid(col="darkgrey",lty=3,lwd=1)
  legend("topleft",legend=c("1st to 3rd Quartiles","Smoothed Medians"),
         col=c("lightblue","darkblue"),bty="n",lty=1,lwd=5,cex=0.7,
         ncol=2,inset=c(0,-0.1),xpd=TRUE)
  
  if(!is.null(outfile)) {
    dev.off()
  }
  par(op)
  
}


# print.vdb.steady() --
#   Plots the IOPS and Latency versus total MB/s to find anomolies 
#   due to garbage collection, post-processing, or similar.
# Arguments --
#           d : Subset of vdbench Data Frame representing the steady-state run.
#     outfile : path to PDF file used to print the graphs. If missing, the graph will
#			          be sent to the default graphical device (useful for interactive calls)
#      warmup : Number of initial intervals to remove as warmup
print.vdb.steady = function(d=NULL,outfile=NULL,warmup=5,metric="rate",phase=NULL,seqn=NULL) {
  
  if(dim(d)[1]==0|is.null(d)) return()
  
  if (!is.null(phase) & !is.null(seqn)) {
    grafPhase = paste0(simpleCap(phase),"(Seq#",as.character(seqn),")")
    strPhase = paste0(phase,"_",as.character(seqn))
  } else {
    grafPhase = "Undefined"
    strPhase = "Unfiltered"
  }
  d = subset(d,interval>warmup)
  
  if(!is.null(outfile)) {
    pdf(outfile,title=paste(grafPhase,"Steady-State Performance"),width=11,height=8.5)
  }
  op=par(mfrow=c(2,1),mar=c(5,4,4,7)+.1)
  
  wrk = vdb.workload(d)
  tot=cumsum(d$MBps)/2^10
  
  if (metric == "MBps") {
    Y = d$MBps
    m=mean(Y)
    tit = paste0(grafPhase," MB/s over Time (",wrk,")")
    ylab = "MB/s"
    sub = paste0(outfile,": Mean MB/s = ",format(signif(m,6),big.mark=","))
  } else {
    Y = d$rate
    m=mean(Y)
    tit = paste0(grafPhase," IOPS over Time (",wrk,")")
    ylab = "IOPS"
    sub = paste0(outfile,": Mean IOPS = ",format(signif(m,6),big.mark=","))
  }
  
  plot(x=tot,y=Y,pch=".",col="LightBlue",
       main=tit,ylab=ylab,xlab="Total GiB Transferred",cex.sub=0.75,sub=sub)
  lines(smooth.spline(x=tot,y=Y,df=30),col="DarkBlue",lwd=3)
  abline(h=c(.9*m,.95*m,m,1.05*m,1.1*m),lty=c(4,3,2,3,4),
         col=c("red","goldenrod","darkgreen","goldenrod","red"),lwd=3)
  grid(col="darkgrey",lty=3,lwd=1)
  legend("right",
         legend=c("Measured","Smoothed Mean","Sample Mean","+/-5% of Mean","+/-10% of Mean"),
         col=c("lightblue","darkblue","darkgreen","goldenrod","red"),seg.len=2,
         bty="n",bg="white",lty=c(1,1,1,1,1),lwd=5,cex=0.5,inset=c(-0.13,0),xpd=TRUE)
  
  plot(x=tot,y=d$resp,pch=".",col="LightBlue",log="y",
       main=paste0(grafPhase," Latency over Time (",wrk,")"),
       ylab="Log milliseconds",xlab="Total GiB Transferred",cex.sub=0.75,
       sub=paste0(outfile,": Mean Latency = ",signif(mean(d$resp),3),
                  " ms ; StdDev = ",signif(sd(d$resp),3)))
  lines(smooth.spline(x=tot,y=d$resp,df=50),col="DarkBlue",lwd=3)
  m=mean(d$resp)
  abline(h=c(.9*m,.95*m,m,1.05*m,1.1*m),lty=c(4,3,2,3,4),
         col=c("red","goldenrod","darkgreen","goldenrod","red"),lwd=3)
  s=sd(d$resp) ; f=d$resp>m+3*s
  points(x=tot[f],y=d$resp[f],pch="o",col="magenta")
  grid(col="darkgrey",lty=3,lwd=1)
  legend("right",
         legend=c("Measured","Smoothed Mean","Sample Mean","+/-5% of Mean","+/-10% of Mean","+3 StdDev > Mean"),
         col=c("lightblue","darkblue","darkgreen","goldenrod","red","magenta"),seg.len=2,
         bty="n",bg="white",lty=c(1,1,1,1,1),lwd=5,cex=0.5,inset=c(-0.13,0),xpd=TRUE)
  
  if(!is.null(outfile)) {
    dev.off()
  }
  par(op)
  
}


# print.vdb.steady.hist() --
#   Plots the steady-state IOPS and Latency histograms to summarize the the
#   steady-state performance.
# Arguments --
#           d : Subset of vdbench Data Frame representing the steady-state run.
#     outfile : path to PDF file used to print the graphs. If missing, the graph will
#  		          be sent to the default graphical device (useful for interactive calls)
#      warmup : Number of initial intervals to remove as warmup
print.vdb.steady.hist = function(d=NULL,outfile=NULL,warmup=5,metric="rate",phase=NULL,seqn=NULL) {
  
  if(dim(d)[1]==0|is.null(d)) return()
  
  if (!is.null(phase) & !is.null(seqn)) {
    grafPhase = paste0(simpleCap(phase),"(Seq#",as.character(seqn),")")
    strPhase = paste0(phase,"_",as.character(seqn))
  } else {
    grafPhase = "Undefined"
    strPhase = "Unfiltered"
  }
  d = subset(d,interval>warmup)
  
  if(!is.null(outfile)) {
    pdf(outfile,title=paste(grafPhase,"Histogram"),width=11,height=8.5)
  }
  op=par(mfrow=c(2,1),mar=c(5,4,4,2)+.1)
  
  wrk=vdb.workload(d)
  if (metric == "MBps") {
    Y = d$MBps
    m = mean(Y)
    tit = paste0(grafPhase," MB/s Histogram (",wrk,")")
    xlab = "Observed MB/s for Interval"
    sub = paste0(outfile,": Mean MB/s = ",format(signif(m,6),big.mark=","))
  } else {
    Y = d$rate
    m = mean(Y)
    tit = paste0(grafPhase," IOPS Histogram (",wrk,")")
    xlab = "Observed IOPS for Interval"
    sub = paste0(outfile,": Mean IOPS = ",format(signif(m,6),big.mark=","))
  }
  

  hist(Y,breaks=100,plot=TRUE,col="LightBlue",main=tit,xlab=xlab,cex.sub=0.75,sub=sub)
  abline(v=m,lwd=5,col="DarkBlue")
  
  x=hist(log(d$resp),breaks=100,plot=FALSE)
  m=mean(d$resp)
  plot(x,xaxt="n",col="LightBlue",
       main=paste0(grafPhase," Latency Histogram (",wrk,")"),
       xlab="Observed Milliseconds Latency for Interval (Log Axis)",
       sub=paste0(outfile,": Mean Latency (ms) = ",signif(m,3)),cex.sub=0.75)
  axis(1,at=x$mids,labels=as.character(signif(exp(x$mids),4)),cex.sub=0.75)
  abline(v=log(m),lwd=5,col="DarkBlue")
  
  if(!is.null(outfile)) {
    dev.off()
  }
  par(op)
}


# compare.vdb.steady() --
#   Plots the steady-state IOPS and latency for two data sets on the same set of
#   graphs. The function allows the X-Axis to be based on time or total MB 
#   transferred. It's also possible to trim the datasets to be equal length,
#   and specify whether they should be trimmed from the beginning or end of the
#   dataset. Typically for steady-state, the end of the dataset is more 
#   meaningful.
# Arguments --
#          us : Subset of vdbench Data Frame representing the steady-state run 
#               of the first dataset.
#      us.tag : Character string used in the graph to name the first dataset.
#        them : Subset of vdbench Data Frame representing the steady-state run 
#               of the second dataset.
#    them.tag : Character string used in the graph to name the second dataset.
#     outfile : path to PDF file used to print the graphs. If missing, the graph
#               will be sent to the default graphical device (useful for 
#  		          interactive calls).
#      warmup : Number of initial intervals to remove as warmup.
#     onepage : Draw both graphs on a single page. Usually most convenient. If 
#               more detail is needed, set to FALSE and then IOPS and latency 
#               are each drawn on their own pages.
#       xaxis : Which value to use for the X axis. Valid values are "xfer" (the 
#               default) and "time". If "xfer" is used, the X-Axis is the 
#               cumulative MB transfered in the dataset. If "time" is used, the
#               X-Axis is the time interval in the dataset. The assumption is 
#               that each interval is one second.
#        trim : Whether to trim the datasets to be roughly the same length along
#               the X-Axis. The default is FALSE. If set to TRUE, the graphs 
#               will be trimmed.
#    trim.fun : Which function to use to trim the datasets, with the valid 
#               values being "head" or "tail" (the default). If "head" is 
#               selected, points are taken from the beginning of the dataset. 
#               If "tail" is selected, points are taken from the end of the 
#               dataset.
compare.vdb.steady = function(us=NULL,us.tag="Us",them,them.tag="Them",
                              outfile=NULL,warmup=5,onepage=TRUE,
                              xaxis="xfer",trim=FALSE,trim.fun="tail") {
  
  if(dim(us)[1]==0|is.null(us)|dim(them)[1]==0|is.null(them)) return()
  
  if(!is.null(outfile)) {
    pdf(outfile,title="Steady-State Comparison",width=11,height=8.5)
  }
  
  if (onepage) {
    op=par(mfrow=c(2,1),mar=c(5,4,4,2)+.1)
    inset=c(0,-0.08)
  }
  else {
    op=par(mfrow=c(1,1),mar=c(5,4,4,2)+.1)
    inset=c(0,-0.03)
  }
  
  us = subset(us,interval>warmup&rate>0&resp>0)
  them = subset(them,interval>warmup&rate>0&resp>0)
  
  switch (xaxis,
          "xfer" = {
            xlab = "Total GiB Transferred"
            us.xpts = cumsum(us$MBps)/2^10
            them.xpts = cumsum(them$MBps)/2^10
            if (trim) {
              s = min(max(us.xpts),max(them.xpts))
              if (trim.fun=="head") {
                us = us[us.xpts<=s,]
                them = them[them.xpts<=s,]
              } else { 
                ### trim.fun == "tail"
                x = cumsum(rev(us$MBps))/2^10
                y = cumsum(rev(them$MBps))/2^10
                us.l = length(x[x<=s])
                them.l = length(y[y<=s])
                us = eval(call(trim.fun,us,us.l))
                them = eval(call(trim.fun,them,them.l))
              }
              us.xpts = cumsum(us$MBps)/2^10
              them.xpts = cumsum(them$MBps)/2^10
            } 
          },
          "time" = {
            xlab = "Time (seconds)"
            if (trim) {
              m=min(length(us$interval),length(them$interval))
              us = eval(call(trim.fun,us,m))
              them = eval(call(trim.fun,them,m))
            } 
            us.xpts = us$interval - (us$interval[1]-1)
            them.xpts = them$interval - (them$interval[1]-1)
          },
          {
            ### No match
            return()
          }
  ) ### End of X-Axis Switch 
  xrng = c(min(us.xpts,them.xpts),max(us.xpts,them.xpts))
  yrng.tput = c(min(us$rate,them$rate),max(us$rate,them$rate))
  yrng.resp = c(min(us$resp,them$resp),min(1000,max(us$resp,them$resp)))
  
  plot(x=xrng,y=yrng.tput,type="n",ylab="IOPS",xlab=xlab,
       main=paste(us.tag,"and",them.tag,"Steady-State IOPS over Time"))
  points(x=us.xpts,y=us$rate,pch=".",col="LightBlue")
  lines(smooth.spline(x=us.xpts,y=us$rate,df=50),col="DarkBlue",lwd=5)
  m=mean(us$rate) ;  abline(h=m,lty=3,col="DarkBlue",lwd=2)
  points(x=them.xpts,y=them$rate,pch=".",col="LightGoldenrod2")
  lines(smooth.spline(x=them.xpts,y=them$rate,df=50),col="DarkOrange2",lwd=5)
  m=mean(them$rate) ;  abline(h=m,lty=3,col="DarkOrange2",lwd=2)
  grid(col="darkgrey",lty=1,lwd=1)
  legend("topright",ncol=6,
         legend=c(paste(us.tag,c("Data","Fit","Mean     ")),
                  paste(them.tag,c("Data","Fit","Mean"))),
         col=c("LightBlue","DarkBlue","DarkBlue","LightGoldenrod2","DarkOrange2","DarkOrange2"),
         lty=c(1,1,3,1,1,3),seg.len=5,bty="n",bg="white",
         lwd=3,cex=0.5,inset=inset,xpd=TRUE)
  
  plot(x=xrng,y=yrng.resp,type="n",log="y",xlab=xlab,ylab="Milliseconds Latency (Log Scale)",
       main=paste(us.tag,"and",them.tag,"Steady-State Latency over Time"))
  points(x=us.xpts,y=us$resp,pch=".",col="LightBlue")
  lines(smooth.spline(x=us.xpts,y=us$resp,df=50),col="DarkBlue",lwd=5)
  m=mean(us$resp) ;  abline(h=m,lty=3,col="DarkBlue",lwd=2)
  points(x=them.xpts,y=them$resp,pch=".",col="LightGoldenrod2")
  lines(smooth.spline(x=them.xpts,y=them$resp,df=50),col="DarkOrange2",lwd=5)
  m=mean(them$resp) ;  abline(h=m,lty=3,col="DarkOrange2",lwd=2)
  grid(col="darkgrey",lty=1,lwd=1)
  legend("topright",ncol=6,
         legend=c(paste(us.tag,c("Data","Fit","Mean     ")),
                  paste(them.tag,c("Data","Fit","Mean"))),
         col=c("LightBlue","DarkBlue","DarkBlue","LightGoldenrod2","DarkOrange2","DarkOrange2"),
         lty=c(1,1,3,1,1,3),seg.len=5,bty="n",bg="white",
         lwd=3,cex=0.5,inset=inset,xpd=TRUE)
  
  if(!is.null(outfile)) {
    dev.off()
  }
  par(op)
}


# compare.vdb.table() -- 
#   Outputs a table comparing two datasets at Varying Latency Threshold 
#   by IO Size and Read Percent
# Arguments --
#          us : Summary vdbench Data Frame (result of summary.vdb() function) 
#               of the first dataset.
#      us.tag : Character string used in the graph to name the first dataset.
#        them : Summary vdbench Data Frame (result of summary.vdb() function) 
#               of the second dataset.
#    them.tag : Character string used in the graph to name the second dataset.
#     outfile : path to PDF file used to print the graphs. If missing, the graph
#               will be sent to the default graphical device (useful for 
#  		          interactive calls).
#      breaks : Target number of latency points to display in the table
compare.vdb.table = function(us=NULL,us.tag="Us",them,them.tag="Them",
                             outfile=NULL,breaks=40,metric="rate") {
  
  if(dim(us)[1]==0|is.null(us)|dim(them)[1]==0|is.null(them)) return()
  
  rd = sort(unique(c(us$rpct,them$rpct)))
  th = sort(unique(c(us$thrd,them$thrd)))
  sz = sort(unique(c(us$iosz,them$iosz)))
  
  par(mfrow=c(1,1),mar=c(5,4,4,2)+0.1)
  if(!is.null(outfile)) {
    if (metric=="rate") {
      tit="Comparison of IOPS at Varying Latency Threshold by IO Size and Read Percent"
    } else {
      tit="Comparison of MB/s at Varying Latency Threshold by IO Size and Read Percent"
    }
    pdf(outfile,title=tit,width=8.5,height=11)
  }
  
  for (i in sz) {
    us.ss=subset(us,iosz==i)
    them.ss=subset(them,iosz==i)
    r=as.numeric(unlist(c(us$resp,them$resp)))
    lat=signif(exp(hist(log(r),breaks=breaks,plot=FALSE)$mids),3)
    lat=lat[lat>=min(r) & lat<=max(r)]
    
    if (metric=="rate") {
      fun = function(r) format(round(approx(x=r$resp[[1]],y=r$iops[[1]],xout=lat)$y,0),big.mark=",")
      tit = paste0("Table of IOPS at Given Latency for ",i/2^10,"K IO Size and ",th," Threads/LUN")
    } else {
      ### metric assumed to be MBps
      fun = function(r) format(round(approx(x=r$resp[[1]],y=r$MBps[[1]],xout=lat)$y,0),big.mark=",")
      tit = paste0("Table of MB/s at Given Latency for ",i/2^10,"K IO Size and ",th," Threads/LUN")
    }
    
    us.tput=as.data.frame(sapply(split(us.ss,us.ss$rpct),fun))
    them.tput=as.data.frame(sapply(split(them.ss,them.ss$rpct),fun))
    rownames(us.tput) = lat ; rownames(them.tput) = lat
    us.tput=data.frame(as.numeric(rownames(us.tput)),us.tput)
    them.tput=data.frame(as.numeric(rownames(them.tput)),them.tput)
    names(us.tput)=c("Latency",paste0(rd,"% Read"))
    names(them.tput)=c("Latency",paste0(rd,"% Read"))
    
    textplot(us.tput,halign="center",valign="top",show.row=FALSE,cex=0.90)
    title(main=paste0(us.tag," Table of IOPS at Given Latency for ",
                      i/2^10,"K IO Size and ",th," Threads/LUN"),
          sub=outfile,cex.main=1.25,cex.sub=0.75)
    textplot(them.tput,halign="center",valign="top",show.row=FALSE,cex=0.90)
    title(main=paste0(them.tag," Table of IOPS at Given Latency for ",
                      i/2^10,"K IO Size and ",th," Threads/LUN"),
          sub=outfile,cex.main=1.25,cex.sub=0.75)
  }
  
  if(!is.null(outfile)) {
    dev.off()
  } 
}

# process.vdb.all() --
#   Function to automate the process of generating all the vdbench analysis PDF plots from
#   the raw flatfile.html. It takes path information and a tag to use when naming the output.
# Arguments --
#           d : Existing parsed vdbench data frame (to avoid repeated parsing)
#    flatfile : Path to the vdbench flatfile.html to parse for test results
#         tag : String to prepend to the output filename as the test identifier
#      outdir : Path to output directory where all the plots will be generated
#         adv : Should "advanced" graphs be generated (defaults to no)
process.vdb.all = 
  function(d=NULL,flatfile=NULL,tag="Latest",outdir=tempdir(),adv=FALSE) {
    
    if(is.null(d)) {
      if(is.null(flatfile))
        stop("Need either vdbench data frame or flatfile")
      d = read.vdb(flatfile)
      print("Flatfile parsed")
    } else {
      print("Using provided data frame")
    }
    
    # Get rid of any wacky data from partial lines in input
    d = subset(d,iosz!=0)
    
    od=getwd()
    setwd(outdir)
    
    ### Empty Small
    if(any(grepl("^emptysmall",levels(d$run)))) {
      esmall = subset(d,grepl("^emptysmall",run)) ; esmall$run = factor(esmall$run)
      essmall = summary.vdb(esmall)
      print.vdb.profile.iops(essmall,paste0(tag,"_Empty_Small_IOPS.pdf"))
      print.vdb.profile.mbps(essmall,paste0(tag,"_Empty_Small_MBps.pdf"))
      print.vdb.profile.rdcurve(essmall,paste0(tag,"_Empty_Small_ReadCurve.pdf"))
      if(adv) {
        print.vdb.profile.queue(esmall,paste0(tag,"_Empty_Small_Queue.pdf"))
        print.vdb.profile.rdpct(esmall,paste0(tag,"_Empty_Small_ReadPct.pdf"))
      }
      print("Processed Empty Small Dataset")
    }

    ### Empty Large
    if(any(grepl("^emptylarge",levels(d$run)))) {
      elarge = subset(d,grepl("^emptylarge",run)) ; elarge$run = factor(elarge$run)
      eslarge = summary.vdb(elarge)
      print.vdb.profile.iops(eslarge,paste0(tag,"_Empty_Large_IOPS.pdf"))
      print.vdb.profile.mbps(eslarge,paste0(tag,"_Empty_Large_MBps.pdf"))
      print.vdb.profile.rdcurve(eslarge,paste0(tag,"_Empty_Large_ReadCurve.pdf"))
      if(adv) {  
        print.vdb.profile.queue(elarge,paste0(tag,"_Empty_Large_Queue.pdf"))
        print.vdb.profile.rdpct(elarge,paste0(tag,"_Empty_Large_ReadPct.pdf"))
      }
      print("Processed Empty Large Dataset")
    }

    ### Empty Sequential
    if(any(grepl("^emptyseqn",levels(d$run)))) {
      eseqn  = subset(d,grepl("^emptyseqn",run)) ; eseqn$run = factor(eseqn$run)
      esseqn  = summary.vdb(eseqn)
      print.vdb.profile.mbps(esseqn,paste0(tag,"_Empty_Sequential_MBps.pdf"))
      print.vdb.profile.rdcurve(esseqn,paste0(tag,"_Empty_Sequential_ReadCurve.pdf"))
      if(adv) {
        print.vdb.sequential.sizes(eseqn,paste0(tag,"_Empty_SequentialSizes.pdf"))
      }
      print("Processed Empty Sequential Dataset")
    }

    ### Empty Steady
    if(any(grepl("^emptysteady",levels(d$run)))) {
      estead = subset(d,grepl("^emptysteady",run)) ; estead$run = factor(estead$run)
      print.vdb.steady(estead,paste0(tag,"_Empty_SteadyState.pdf"))
      print("Processed Empty Steady-State Dataset")
    }

    ### Precondition
    if(all(c(any(grepl("^fill",levels(d$run))),
             any(grepl("^age",levels(d$run)))))) {
      prec = subset(d,grepl("^fill",run)|grepl("^age",run)) ; prec$run = factor(prec$run)
      print.vdb.precondition(prec,paste0(tag,"_Precondition.pdf"))
      print("Processed Preconditioning Dataset")
    }

    ### Small
    if(any(grepl("^small",levels(d$run)))) {
      small = subset(d,grepl("^small",run)) ; small$run = factor(small$run)
      ssmall = summary.vdb(small)
      print.vdb.profile.iops(ssmall,paste0(tag,"_Small_IOPS.pdf"))
      print.vdb.profile.mbps(ssmall,paste0(tag,"_Small_MBps.pdf"))
      print.vdb.table.iops(ssmall,paste0(tag,"_Small_TableIOPS.pdf"))
      print.vdb.table.mbps(ssmall,paste0(tag,"_Small_TableMBps.pdf"))
      print.vdb.profile.rdcurve(ssmall,paste0(tag,"_Small_ReadCurve.pdf"))
      if(adv) {
        print.vdb.profile.queue(small,paste0(tag,"_Small_Queue.pdf"))
        print.vdb.profile.rdpct(small,paste0(tag,"_Small_ReadPct.pdf"))
      }
      print("Processed Preconditioned Small Dataset")
    }

    ### Large
    if(any(grepl("^large",levels(d$run)))) {
      large = subset(d,grepl("^large",run)) ; large$run = factor(large$run)
      slarge = summary.vdb(large)
      print.vdb.profile.iops(slarge,paste0(tag,"_Large_IOPS.pdf"))
      print.vdb.profile.mbps(slarge,paste0(tag,"_Large_MBps.pdf"))
      print.vdb.table.iops(slarge,paste0(tag,"_Large_TableIOPS.pdf"))
      print.vdb.table.mbps(slarge,paste0(tag,"_Large_TableMBps.pdf"))
      print.vdb.profile.rdcurve(slarge,paste0(tag,"_Large_ReadCurve.pdf"))
      if(adv) {  
        print.vdb.profile.queue(large,paste0(tag,"_Large_Queue.pdf"))
        print.vdb.profile.rdpct(large,paste0(tag,"_Large_ReadPct.pdf"))
      }
      print("Processed Preconditioned Large Dataset")
    }

    ### Sequential
    if(any(grepl("^seqn",levels(d$run)))) {
      seqn= subset(d,grepl("^seqn",run)) ; seqn$run = factor(seqn$run)
      sseqn  = summary.vdb(seqn)  
      print.vdb.profile.iops(sseqn,paste0(tag,"_Sequential_IOPS.pdf"))
      print.vdb.profile.mbps(sseqn,paste0(tag,"_Sequential_MBps.pdf"))
      print.vdb.table.iops(sseqn,paste0(tag,"_Sequential_TableIOPS.pdf"))
      print.vdb.table.mbps(sseqn,paste0(tag,"_Sequential_TableMBps.pdf"))
      print.vdb.profile.rdcurve(sseqn,paste0(tag,"_Sequential_ReadCurve.pdf"))
      if(adv) {
        print.vdb.sequential.sizes(seqn,paste0(tag,"_SequentialSizes.pdf"))
      }
      print("Processed Preconditioned Sequential Dataset")
    }

    ### Steady
    if(any(grepl("^steady",levels(d$run)))) {
      stead = subset(d,grepl("^steady",run)) ; stead$run = factor(stead$run)
      print.vdb.steady(stead,paste0(tag,"_SteadyState.pdf"))
      print.vdb.steady.hist(stead,paste0(tag,"_SteadyState_Hist.pdf"))
      print("Processed Preconditioned Steady-State Dataset")
    }
    
    print("**********************************************")
    print(paste("Plots for",tag,"generated in",outdir))
    ### files=list.files(pattern=tag)
    ### system(paste0("zip -q ",tag,"_Plots.zip ",gsub(", "," ",toString(files))))
    invisible(setwd(od))
}


