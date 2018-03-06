#!/usr/bin/Rscript

######################################################################
# All-Flash Array PoC Test Script -- Runs all the requested phases of
# the AFA PoC toolkit. Includes modes to check parsing and run a short
# test to make sure all the host connectivity is solid.
######################################################################

### Set options and variables
### options(error=expression(NULL))  ### Uncomment to ignore all R errors and keep running
options(echo=FALSE,scipen=10)
suppressMessages(require(KernSmooth))
library("getopt",warn.conflicts=FALSE,quietly=TRUE)
library("plotrix",warn.conflicts=FALSE,quietly=TRUE)
library("gplots",warn.conflicts=FALSE,quietly=TRUE)


### Parse command line options
spec = matrix(c(
  'out','o',1,"character","Output directory (required)",
  'tag','t',2,"character","Tag identifier for this run...usually the system being tested (optional)",
  'queue','q',2,"integer","Target queue depth for the whole array divided across target LUNs (optinal; defaults to 512)",
  'cap','c',2,"integer","Array capacity in base-10 gigabytes to age during the PoC test (optional if afa_check succeeded)",    
  'luns','l',2,"integer","Number of test LUNs accessed during the PoC test (optional if afa_check succeeded)",  
  'nowait','w',0,"logical","Avoid interactive wait after preparation phases",
  'preflight','p',0,"logical","Pre-flight run to check all access and IO flow (default is FALSE)",
  'redo','r',0,"logical","Run vdbench again even if results file already exists (default is FALSE)",
  'simulate','s',0,"logical","Simulate running vdbench but don't actually run it",
  'help','h',0,"logical","This help message"),ncol=5,byrow=T)
opt = getopt(spec)

if (!is.null(opt$help) || is.null(opt$out)) {
  cat(paste(getopt(spec, usage=T),"\n"))
  quit(save="no",status="-1",runLast=FALSE)
}
opt$out = gsub("/$","",opt$out)
if (substr(opt$out,1,1)!="/") {
  opt$out = paste0(getwd(),"/",opt$out)
}

if (is.null(opt$tag)) 
  opt$tag = paste0("AFA.",format(Sys.time(),"%Y.%m.%d.%H.%M"))

if (is.null(opt$cap)) {
    if (file.exists("~/discovered_capacity")) {
        opt$cap = as.integer(readLines(con="~/discovered_capacity"))
		opt$snapcap = as.integer(opt$cap/2)
    }
    else {
        writeLines("Array capacity missing and couldn't be discovered.\nPlease specify with -c parameter or rerun afa_prep.")
        quit(save="no",status="-1",runLast=FALSE)
    }
}

if (is.null(opt$queue)) {
    opt$queue = ifelse(is.null(opt$preflight),512,512)
}

if (!is.null(opt$simulate)) {
  opt$simulate = TRUE
} else {
  opt$simulate = FALSE
}

if (!is.null(opt$nowait)) {
  opt$nowait = TRUE
} else {
  opt$nowait = FALSE
}

if (is.null(opt$luns)) {
    if (file.exists("~/discovered_luns")) {
        opt$luns = as.integer(readLines(con="~/discovered_luns"))
    }
    else {
        writeLines("Number of test LUNs missing and couldn't be discovered.\nPlease specify with -l parameter or rerun afa_prep.")
        quit(save="no",status="-1",runLast=FALSE)
    }
}

if (!is.null(opt$preflight)) {
    opt$preflight = TRUE
    opt$cap = min(opt$cap,(opt$luns*5))
	opt$env = "/root/AFA/pre-env.vdb"
} else {
  opt$preflight = FALSE
  opt$env = "/root/AFA/poc-env.vdb"
}

writeLines("**************************************************************")
writeLines("***           Starting All-Flash Array PoC Run             ***")
writeLines("**************************************************************")
writeLines(paste("Output Directory:",opt$out))
writeLines(paste("Run Tag:",opt$tag))
writeLines(paste("Queue:",opt$queue))
writeLines(paste("Capacity:",opt$cap))
writeLines(paste("LUNs:",opt$luns))
writeLines(paste("Overwrite existing flatfile.html results:",ifelse(is.null(opt$redo),"No","Yes")))
writeLines(paste("Run short Pre-Flight test:",ifelse(opt$preflight,"Yes","No")))
writeLines(paste("Wait for User Input:", ifelse(opt$nowait,"No","Yes")))
writeLines(paste("Run vdbench in Simulate-only mode:",ifelse(opt$simulate,"Yes","No")))
writeLines("\n")

# Define where to find important files and source helper functions
vdbexe = "/root/vdbench/vdbench"
vdbfun = "/root/R/vdbench_functions.R"
vdbphasefun = "/root/R/phase_functions.R"
vdbphasefile = "/root/AFA/phases.vdb"
vdbsim = ifelse(opt$simulate,"-s","")
source(vdbfun)
source(vdbphasefun)

### Prepare file paths and output directories
cwd = getwd()
outdir = opt$out
dir.create(outdir,showWarnings=FALSE)
setwd(outdir)

### Read the requested Test Phases
if (file.exists(vdbphasefile)) {
  writeLines(paste0("**************************************************************",
                    "\n***               Reading Requested Phases                 ***",
                    "\n**************************************************************"))
  phases = read.table(vdbphasefile,col.names = c("Sequence","Phase"))
  phases = phases[order(phases$Sequence),]
  writeLines("Discovered the following Sequence Numbers and Phases:")
  writeLines("+----------------+--------------------------+")
  for (i in 1:dim(phases)[1]) {
    writeLines(sprintf("| Sequence = %3d | Phase = %16s |",
                       as.numeric(phases[i,1]),
                       as.character(phases[i,2])))
  }
  writeLines("+----------------+--------------------------+\n\n")
} else {
  writeLines(paste("Phase file does not exist at",vdbphasefile))
  quit(save="no",status="-1",runLast=FALSE)
}

### Prepare stuff for results
cum.res = data.frame()


### Start Main Phases Loop

for (i in 1:dim(phases)[1]) {
  seqn = as.numeric(phases[i,1])
  phase = as.character(phases[i,2])
  
  switch(phase,
         "fill" = {
           if (!opt$preflight) {
             tmp.res = run.vdb.phase.fill(env=opt$env,dur=172800,capacity=opt$cap,threads=4,seqn=seqn)
           } else {
             tmp.res = run.vdb.phase.fill(env=opt$env,dur=300,capacity=opt$cap,threads=4,seqn=seqn)
           }
           if (!is.numeric(tmp.res)) {
             cum.res = rbind(cum.res,tmp.res)
             grafPhase = paste0(simpleCap(phase),"_",as.character(seqn))
             if (!opt$simulate) {
               tmp.res$run = factor(tmp.res$run)
               print.vdb.steady(tmp.res,paste0(opt$tag,"_",grafPhase,"_MBPSvsTime.pdf"),
                                metric="MBps",phase=phase,seqn=seqn)
               print.vdb.steady.hist(tmp.res,paste0(opt$tag,"_",grafPhase,"_Hist.pdf"),
                                     metric="MBps",phase=phase,seqn=seqn)
               writeLines(paste0("Generated graphs for Phase ",grafPhase," in ",outdir,".\n"))
             } else {
               writeLines(paste0("Simulate Only. Skipping graphs for ",grafPhase,".\n"))
             }
           }
         },
         "age" = {
           thr=ceiling(opt$queue/opt$luns)
           if (!opt$preflight) {
             tmp.res = run.vdb.phase.age(env=opt$env,dur=172800,capacity=opt$cap,threads=thr,seqn=seqn)
           } else {
             tmp.res = run.vdb.phase.age(env=opt$env,dur=300,capacity=opt$cap,threads=thr,seqn=seqn)
           }
           if (!is.numeric(tmp.res)) {
             cum.res = rbind(cum.res,tmp.res)
             grafPhase = paste0(simpleCap(phase),"_",as.character(seqn))
             if (!opt$simulate) {
               tmp.res$run = factor(tmp.res$run)
               print.vdb.steady(tmp.res,paste0(opt$tag,"_",grafPhase,"_IOvsTime.pdf"),phase=phase,seqn=seqn)
               print.vdb.steady.hist(tmp.res,paste0(opt$tag,"_",grafPhase,"_Hist.pdf"),phase=phase,seqn=seqn)
               writeLines(paste0("Generated graphs for Phase ",grafPhase," in ",outdir,".\n"))
             } else {
               writeLines(paste0("Simulate Only. Skipping graphs for ",grafPhase,".\n"))
             }
           }
         },
         "profile" = {
           thr=ceiling(opt$queue/(2*opt$luns))
           if (!opt$preflight) {
             crv="10,20,30,40,50,60,70,80,90,92,94,96,98"
             rdp="0,35,50,80,100"
             tim=120
           } else {
             crv="10,50,90"
             rdp="0,50,100"
			 tim=30
           }
           tmp.res = run.vdb.phase.profile(env=opt$env,dur=tim,curvepts=crv,readpct=rdp,capacity=opt$cap,
                                           smthr=2*thr,lgthr=thr,seqn=seqn)
           if (!is.numeric(tmp.res)) {
             cum.res = rbind(cum.res,tmp.res)
             grafPhase = paste0(simpleCap(phase),"_",as.character(seqn))
             if (!opt$simulate) {
               small = subset(tmp.res,grepl("^small",run)) ; small$run = factor(small$run)
               ssmall = summary.vdb(small)
               print.vdb.profile.iops(ssmall,paste0(opt$tag,"_",grafPhase,"_Small_IOPS.pdf"))
               print.vdb.profile.mbps(ssmall,paste0(opt$tag,"_",grafPhase,"_Small_MBps.pdf"))
               print.vdb.table.iops(ssmall,paste0(opt$tag,"_",grafPhase,"_Small_TableIOPS.pdf"))
               print.vdb.table.mbps(ssmall,paste0(opt$tag,"_",grafPhase,"_Small_TableMBps.pdf"))
               print.vdb.profile.rdcurve(ssmall,paste0(opt$tag,"_",grafPhase,"_Small_ReadCurve.pdf"))
               large = subset(tmp.res,grepl("^large",run)) ; large$run = factor(large$run)
               slarge = summary.vdb(large)
               print.vdb.profile.iops(slarge,paste0(opt$tag,"_",grafPhase,"_Large_IOPS.pdf"))
               print.vdb.profile.mbps(slarge,paste0(opt$tag,"_",grafPhase,"_Large_MBps.pdf"))
               print.vdb.table.iops(slarge,paste0(opt$tag,"_",grafPhase,"_Large_TableIOPS.pdf"))
               print.vdb.table.mbps(slarge,paste0(opt$tag,"_",grafPhase,"_Large_TableMBps.pdf"))
               print.vdb.profile.rdcurve(slarge,paste0(opt$tag,"_",grafPhase,"_Large_ReadCurve.pdf"))
               writeLines(paste0("Generated graphs for Phase ",grafPhase," in ",outdir,".\n"))
             } else {
               writeLines(paste0("Simulate Only. Skipping graphs for ",grafPhase,".\n"))
             }
           }
         },
         "steady" = {
           thr=ceiling(opt$queue/opt$luns)
           if (!opt$preflight) {
             tmp.res = run.vdb.phase.steady(env=opt$env,dur=43200,capacity=opt$cap,threads=thr,seqn=seqn)
           } else {
             tmp.res = run.vdb.phase.steady(env=opt$env,dur=300,capacity=opt$cap,threads=thr,seqn=seqn)
           }
           if (!is.numeric(tmp.res)) {
             cum.res = rbind(cum.res,tmp.res)
             grafPhase = paste0(simpleCap(phase),"_",as.character(seqn))
             if (!opt$simulate) {
               tmp.res$run = factor(tmp.res$run)
               print.vdb.steady(tmp.res,paste0(opt$tag,"_",grafPhase,"_IOvsTime.pdf"),phase=phase,seqn=seqn)
               print.vdb.steady.hist(tmp.res,paste0(opt$tag,"_",grafPhase,"_Hist.pdf"),phase=phase,seqn=seqn)
               writeLines(paste0("Generated graphs for Phase ",grafPhase," in ",outdir,".\n"))
             } else {
               writeLines(paste0("Simulate Only. Skipping graphs for ",grafPhase,".\n"))
             }
           }
         },
         "snapprep" = {
		   if (!opt$preflight) {
		     ### Run script to prepare the array for snapshot testing
		     setprepfile = "/root/tools/snap_prep.sh"
		     system(setprepfile)
		     system("touch /tmp/snap_prep.tmp")
		     if (file.exists("/tmp/snap_prep.tmp")) {
		     	writeLines(paste0("\n**************************************************************\n",
		     					"***            Snapshot Prepartion is Complete             ***\n",
		     					"**************************************************************\n"))
		     	system("rm -f /tmp/snap_prep.tmp")
		     }
		   }
		 },
         "snapsteady" = {
           if (!opt$preflight) {
		     thr=ceiling(opt$queue/opt$luns)
			 ### Set permissions and ensure unix format of snapshot scripts
			 setpermfile = "/root/tools/set_perm.sh"
			 system(setpermfile)
             ### Run script to enable snapshot scheduler /root/tools/snap_start.sh
             setstartfile = "/root/tools/snap_start.sh"
             system(setstartfile)
             tmp.res = run.vdb.phase.snapsteady(dur=7200,capacity=opt$snapcap,threads=thr,seqn=seqn)
           }
           if (!is.numeric(tmp.res)) {
             cum.res = rbind(cum.res,tmp.res)
             grafPhase = paste0(simpleCap(phase),"_",as.character(seqn))
             if (!opt$simulate) {
               tmp.res$run = factor(tmp.res$run)
               print.vdb.steady(tmp.res,paste0(opt$tag,"_",grafPhase,"_IOvsTime.pdf"),phase=phase,seqn=seqn)
               print.vdb.steady.hist(tmp.res,paste0(opt$tag,"_",grafPhase,"_Hist.pdf"),phase=phase,seqn=seqn)
               writeLines(paste0("Generated graphs for Phase ",grafPhase," in ",outdir,".\n"))
             } else {
               writeLines(paste0("Simulate Only. Skipping graphs for ",grafPhase,".\n"))
             }
             ### Run script to disable snapshot scheduler /root/tools/snap_start.sh
             setstopfile = "/root/tools/snap_stop.sh"
             system(setstopfile)
		   }
         },
         {
           ### No match
           grafPhase = paste0(simpleCap(phase),"_",as.character(seqn))
           writeLines(paste0("*** Don't recognize Phase ",grafPhase,"!!! Skipping.\n"))
         }
  ) ### End of Switch Statement
} ### End of Phase Loop

if (!opt$simulate) {
### Save everything including the flatfile
  assign(make.names(opt$tag),cum.res)
  files=list.files(pattern=opt$tag)
  system(paste0("zip -q ",opt$tag,"_All.zip ",gsub(", "," ",toString(files)),
                " ./*/flatfile.html ./*/parmfile.html ./*/histogram.html ./*/skew.html"))
  unlink("Rplots.pdf")
  setwd(cwd)
} else {
    writeLines("Simulate Only. Skipping results file processing.\n")
}

writeLines("**************************************************************")
writeLines("***           All-Flash Array PoC Run Completed            ***")
writeLines("**************************************************************")

quit(save="yes")


