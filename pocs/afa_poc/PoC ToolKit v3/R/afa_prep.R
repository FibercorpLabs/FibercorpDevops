#!/usr/bin/Rscript

######################################################################
# All-Flash Array (AFA) PoC Preparation Utility - v3.0 
# Run this utility to prepare and validate the PoC testing
# environment. It will verify connectivity to the workers, gather
# test LUN sizes, and distribute vdbench to all workers.
######################################################################

### Set options and variables
options(echo=FALSE,scipen=10)
library("getopt")

### Parse command line options
spec = matrix(c(
  'luns','l',1,"integer","Number of LUNs per Load Generator host (e.g., 8)",
  'numhosts','n',1,"integer","Number of Load Generator hosts (e.g., 8)",
  'pattern','p',1,"character","Load Generator name pattern in /etc/hosts (e.g., vdb-0)",
  'dir','d',2,"character","Target directory for vdbench specification file (optional; defaults to ~/AFA)",
  'verbose','v',0,"logical","Print more status messages",
  'help','h',0,"logical","This help message"),ncol=5,byrow=T)
opt = getopt(spec)

if (!is.null(opt$help) || is.null(opt$pattern) || 
      is.null(opt$luns) || !is.numeric(opt$luns) ||
      is.null(opt$numhosts) || !is.numeric(opt$numhosts)) {
  cat(paste(getopt(spec, usage=T),"\n"))
  quit(save="no",status="-1",runLast=FALSE)
}

opt$luns=floor(opt$luns)
opt$numhosts=floor(opt$numhosts)
opt$verbose=ifelse(is.null(opt$verbose),FALSE,TRUE)

opt$dir = ifelse(is.null(opt$dir),"~/AFA",gsub("/$","",opt$dir))

### Look in /etc/hosts for hosts matching the pattern and verify correct number
writeLines("**************************************************************")
writeLines("***       Starting All-Flash Array PoC Preparations        ***")
writeLines("**************************************************************")
cat("Looking for load generators in /etc/hosts: ")
x=readLines("/etc/hosts")
vdbs=unlist(lapply(strsplit(x[grep(opt$pattern,x)],"[[:space:]]+"),function(x) x[2]))
if (length(vdbs) < opt$numhosts) {
  cat(paste0("\nStopping! Number of matching hosts in /etc/hosts (",
             length(vdbs),") is less than the supplied numhosts parameter (",
             opt$numhosts,")\n"))
  quit(save="no",status="-1",runLast=FALSE)
}
cat(paste("Found",length(vdbs),"\n"))
vdbs=vdbs[1:opt$numhosts]

### Check network connectivity for all the load generators found in /etc/hosts
writeLines("**************************************************************")
if (!opt$verbose) cat("Checking load generator network connectivity: ")
for (v in vdbs) {
  if (system(paste("ping -c 5 -i 0.2 -q",v,"| grep '0% packet loss'"),
             ignore.stdout=TRUE,ignore.stderr=TRUE)) {
    cat(paste("\nStopping! Encountered errors pinging",v,"\n"))
    quit(save="no",status="-1",runLast=FALSE)
  }
  if (opt$verbose) writeLines(paste("Successfully pinged",v))
}
if (!opt$verbose) cat("All Alive!\n")


### Try to SSH to the load generator as root
writeLines("**************************************************************")
if (!opt$verbose) cat("Checking load generator SSH access: ")
for (v in vdbs) {
  id=system(paste("ssh",v,"id"),intern=TRUE,ignore.stderr=TRUE)
  if (!is.null(attributes(id)$status) || !grepl("root",id)) {
    cat(paste("\nStopping! Encountered errors trying root SSH",v,"\n"))
    quit(save="no",status="-1",runLast=FALSE)
  }
  if (opt$verbose) writeLines(paste("Successfully accessed",v,"as root via SSH"))
}
if (!opt$verbose) cat("All Accessible!\n")


### Check for vdbench and unzip it if it doesn't exist
writeLines("**************************************************************")
toolsdir="~/tools"
vdbdir="~/vdbench"
vdbjar=paste0(vdbdir,"/vdbench.jar")
vdbclass=paste0(vdbdir,"/classes/Vdb")

if (file.exists(vdbjar)) {
    if (file.info(vdbjar)$size > 5e5) {
        writeLines("Found vdbench.jar in the expected location...assuming vdbench installed in ~/vdbench/")
    }
} else {
    zips=list.files(toolsdir,pattern="^vdbench[0-9]+\\.zip$")
    if (length(zips)>0) {
        zip=paste0(toolsdir,"/",zips[length(zips)])
        vdbversion=na.omit(as.numeric(unlist(strsplit(zip,"[^0-9]+"))))
        unzip(zipfile=zip,exdir=vdbdir)
        writeLines(paste("Populating",vdbdir,"from",zip))
    } else {
        writeLines(paste("Stopping! Vdbench doesn't exist in",vdbdir,"and vdbench zip file doesn't exist in",toolsdir))
        writeLines(paste0("Please download the vdbench zip file from Oracle at\n",
                         "   ===>   http://www.oracle.com/technetwork/server-storage/vdbench-downloads-1901681.html\n",
                         "and place it in ",toolsdir,"\n"))
        quit(save="no",status="-1",runLast=FALSE)
    }
}


### Patch vdbench with adjusted memory limits
writeLines("**************************************************************")
if (!opt$verbose) cat("Copying vdbench with adjusted memory limits : ")
vdbpath=paste0(vdbdir,"/vdbench")
vdborig=paste0(vdbpath,".orig")
vdbclkr=paste0(vdbdir,"/linux/linux_clock.redhat")
vdbclks=paste0(vdbdir,"/linux/linux_clock.suse")
srcSstr="  \\$java -client -Xmx1024m -Xms128m -cp \\$cp Vdb.SlaveJvm \\$\\*"
dstSstr="  \\$java -d64    -Xmx896m  -Xms448m -cp \\$cp Vdb.SlaveJvm \\$\\*"
srcMstr="  \\$java -client -Xmx512m  -Xms64m  -cp \\$cp Vdb.Vdbmain \\$\\*"
dstMstr="  \\$java -d64    -Xmx512m  -Xms64m  -cp \\$cp Vdb.Vdbmain \\$\\*"

if (file.exists(vdbpath)) {
    if (!Sys.chmod(vdbpath,mode="0744")) {
        writeLines(paste("Something went wrong setting",vdbpath,"executable mode bits."))
        quit(save="no",status="-1",runLast=FALSE)
    }
} else {
    writeLines(paste("Something went wrong. Can't find",vdbpath,"even though it should exist by this point."))
    quit(save="no",status="-1",runLast=FALSE)
}

if (!file.exists(vdborig)) {
    invisible(file.copy(vdbpath,vdborig,overwrite=FALSE))
} else {
    writeLines(paste("Backup copy of vdbench already exists at",vdborig))
}

original=readLines(vdborig)
writeLines(gsub(srcSstr,dstSstr,gsub(srcMstr,dstMstr,original)),con=vdbpath)
patched=readLines(vdbpath)
if (opt$verbose) {
    writeLines(original[grep("Vdb.SlaveJvm",original)])
    writeLines("...patched to: ")
    writeLines(patched[grep("Vdb.SlaveJvm",patched)])
    writeLines(original[grep("Vdb.Vdbmain",original)])
    writeLines("...patched to: ")
    writeLines(patched[grep("Vdb.Vdbmain",patched)])
    writeLines("Successfully patched vdbench memory settings.")
}
if (!opt$verbose) cat("Done!\n")


### Copy vdbench to all the load generators
writeLines("**************************************************************")
if (!opt$verbose) cat("Copying vdbench to load generators : ")
for (v in vdbs) {
  if (system(paste0("scp -rpq ~/vdbench/ ",v,":~/"),
             ignore.stdout=TRUE,ignore.stderr=TRUE)) {
    cat(paste("\nStopping! Encountered errors copying vdbench directory to",v,"\n"))
    quit(save="no",status="-1",runLast=FALSE)
  }
  if (opt$verbose) writeLines(paste("Successfully copied vdbench directory to",v))
}
if (!opt$verbose) cat("All have a copy!\n")

### Track total number of test LUNs and aggregate capacity
totlun = 0
totgb = 0

### Find all the non-system disks on the hosts. Count number of LUNs and GiB.
writeLines("**************************************************************")
if (!opt$verbose) cat("Checking for number of LUNs: ")
for (v in vdbs) {
  fdisk=system(paste("ssh",v,"fdisk -lu | grep 'Disk /dev/sd'"),intern=TRUE)
  fdisk=fdisk[!grepl("/dev/sda",fdisk)]
  luns=sort(unlist(lapply(strsplit(fdisk,"[[:space:]:]+"),function(x) x[2])))
  bytes=unlist(lapply(strsplit(fdisk,"[[:space:]:]+"),function(x) x[5]))
  l=length(luns)
  gb = sum(as.numeric(bytes))/10^9
  lunscap = sum(as.numeric(bytes))/1024/1024/1024
  lunsize = lunscap/l
  if (l!=opt$luns) {
    cat(paste0("\nStopping! Found ",l," LUNs for ",v,
               " but was expecting ",opt$luns,"\n"))
    quit(save="no",status="-1",runLast=FALSE)
  }
  if (opt$verbose) writeLines(paste("Found",l,"LUNs on",v,"totaling",gb,"GB (base 10)"))
  totlun = totlun + l
  totgb = totgb + gb
}
if (!opt$verbose) cat("All load generator have correct LUN count!\n")

writeLines("**************************************************************")
writeLines(paste("Successfully verified! Testing will be conducted on",totlun,
                 "LUNs totaling",ceiling(totgb),"GB (base 10) across",opt$numhosts,
                 "Load Generators"))
writeLines("**************************************************************")

writeLines("Preparing test files...")

writeLines(as.character(ceiling(totgb)),con="~/discovered_capacity")
writeLines(as.character(ceiling(totlun)),con="~/discovered_luns")
writeLines("Wrote discovered capacity into ~/discovered_capacity and discovered LUN count into ~/discovered_luns")

fn=paste0(opt$dir,"/pre-env.vdb")
pocfile=file(fn,"w")
writeLines("hd=default,user=root,shell=ssh,jvms=4",con=pocfile)
writeLines(sprintf("hd=%s,system=%s",vdbs,vdbs),con=pocfile)
writeLines("sd=default,openflags=directio",con=pocfile)
writeLines(sprintf("sd=sd%d_$host,host=$host,lun=%s,size=5g",1:length(luns),luns),con=pocfile)
close(pocfile)

fn1=paste0(opt$dir,"/poc-env.vdb")
pocfile=file(fn1,"w")
writeLines("hd=default,user=root,shell=ssh,jvms=4",con=pocfile)
writeLines(sprintf("hd=%s,system=%s",vdbs,vdbs),con=pocfile)
writeLines("sd=default,openflags=directio",con=pocfile)
writeLines(sprintf("sd=sd%d_$host,host=$host,lun=%s",1:length(luns),luns),con=pocfile)
close(pocfile)

#Build phases.vdb, snap_start.sh and snap_stop.sh scripts
writeLines("**************************************************************")
setmkscripts = "/root/tools/mk_scripts.sh"
system(setmkscripts)

#Build snap_prep.sh
offset = lunsize/2
seek = offset
fn2=paste0(toolsdir,"/snap_prep.sh")
pocfile=file(fn2,"w")
writeLines("#!/bin/bash",con=pocfile)
writeLines(" ",con=pocfile)
writeLines(sprintf("#Discovered LUN Size: %s",lunsize),con=pocfile)
writeLines(" ",con=pocfile)
for (v in vdbs){
	for (l in luns){
		writeLines(sprintf("ssh root@%s blkdiscard -o %sG -l %sG -p 1G %s &",v,offset,seek,l),con=pocfile)
	}
}
writeLines(" ",con=pocfile)
writeLines("# include snap_prep progress message",con=pocfile)
writeLines("source /root/tools/progress",con=pocfile)
close(pocfile)

fn3=paste0(opt$dir,"/snap-env.vdb")
pocfile=file(fn3,"w")
writeLines("hd=default,user=root,shell=ssh,jvms=4",con=pocfile)
writeLines(sprintf("hd=%s,system=%s",vdbs,vdbs),con=pocfile)
writeLines("sd=default,openflags=directio",con=pocfile)
writeLines(sprintf("sd=sd%d_$host,host=$host,lun=%s,size=%sG",1:length(luns),luns,offset),con=pocfile)
close(pocfile)

### Set permissions on /root/vdbench/linux/config.sh
writeLines("**************************************************************")
setpermfile = "/root/tools/set_perm.sh"
system(setpermfile)

writeLines("**************************************************************")
writeLines(paste("Created Pre-flight hosts and LUNs specification in",fn))
writeLines(paste("Created PoC hosts and LUNs specification in",fn1))
          
writeLines("**************************************************************")
writeLines("*** Successfully Completed All-Flash Array PoC Preparation ***")
writeLines("**************************************************************")
quit(save="yes")
