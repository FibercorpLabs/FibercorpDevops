######################################################################
# Helper Functions used for various phases of the tests
######################################################################

# run.vdb.phase.fill() --
#   Function to run vdbench for the fill phase of the AFA PoC toolkit. If the 
#   run ends successfully, the output directory will contain a fill subdirectory
#   which includes a flatfile with the measurement results. This function
#   should be run within the context of the afa_poc script to pick up required
#   environment variables. 
#         env : Path to the environment fileo
#         dur : Maximum duration of phase (for preflight)
#    capacity : Amount of IO to generate (capacity of LUNs to age)
#     threads : Number of threads per LUN to ensure sufficient load
#        seqn : Sequence number for phase name in run descriptionon
# Returns --
# success/skipped :  vdbench data frame with parsed results
#      fail/abort :  1
#             wtf : -1
run.vdb.phase.fill = function(env,dur,capacity,threads,seqn) 
{
  outdir = paste0(outdir,"/fill_",seqn,"/")
  dir.create(outdir,showWarnings=FALSE)
  vdbphase = "/root/AFA/fill_param.vdb"
  vdbcon = paste0(outdir,opt$tag,"-out.txt")
  vdberr = paste0(outdir,opt$tag,"-err.txt")
  vdbres = paste0(outdir,"flatfile.html")
  vdbarg = paste0(vdbsim," -f ",vdbphase," -o ",outdir," ENV=",env," TIME=",dur," SEQN=",seqn," CAPACITY=",capacity,"g"," THREAD=",threads)
  vdbmsg = paste0(vdbsim," -f ",vdbphase," -o ",outdir," SEQN=",seqn)
  if (!file.exists(vdbres) || !is.null(opt$redo)) {
    writeLines(paste0("**************************************************************",
                      "\n*** Starting Fill script (Sequence #",seqn,")",
                      "\n**************************************************************",
                      "\nTo monitor progress, run: \"tail -f ",vdbcon,"\" from another session."))
    writeLines(paste("Arguments for vdbench:",vdbmsg))
    tryRun = try(system2(command=vdbexe,args=vdbarg,stdout=vdbcon,stderr=vdberr))
    if (tryRun!=0) {
      writeLines(paste0("*** PoC Fill (Seqn #",seqn,
                        ") script did *NOT* complete successfully ***",
                        "\nPlease see: \n   CONSOLE -- ",vdbcon,
                        "\n   ERROR -- ",vdberr,"\nfor more information.\n"))
      return(1)
    } else {
      writeLines(paste0("*** SUCCESSFUL Fill (Seqn #",seqn,") script run! ***",
                        "\nResults data is in:",vdbres,"\n"))
      return(read.vdb(file = vdbres))
    }
  } else {
    writeLines(paste0("*** Skipping Fill (Seqn #",seqn,
                      ") script because results file exists and redo not requested. ***\n"))
    return(read.vdb(file = vdbres))
  }  
  # Should never get here
  return(-1)
}

# run.vdb.phase.age() --
#   Function to run vdbench for the aging phase of the AFA PoC toolkit. If the 
#   run ends successfully, the output directory will contain an age subdirectory
#   which includes a flatfile with the measurement results. This function 
#   should be run within the context of the afa_poc script to pick up required
#   environment variables. 
# Arguments --
#         env : Path to the environment fileo
#         dur : Maximum duration of phase (for preflight)
#    capacity : Amount of IO to generate (capacity of LUNs to age)
#     threads : Number of threads per LUN to ensure sufficient load
#        seqn : Sequence number for phase name in run description
# Returns --
# success/skipped :  vdbench data frame with parsed results
#      fail/abort :  1
#             wtf : -1
run.vdb.phase.age = function(env,dur,capacity,threads,seqn) 
{
  outdir = paste0(outdir,"/age_",seqn,"/")
  dir.create(outdir,showWarnings=FALSE)
  vdbphase = "/root/AFA/age_param.vdb"
  vdbcon = paste0(outdir,opt$tag,"-out.txt")
  vdberr = paste0(outdir,opt$tag,"-err.txt")
  vdbres = paste0(outdir,"flatfile.html")
  vdbarg = paste0(vdbsim," -f ",vdbphase," -o ",outdir," ENV=",env," TIME=",dur," SEQN=",seqn," CAPACITY=",capacity,"g"," THREAD=",threads)
  vdbmsg = paste0(vdbsim," -f ",vdbphase," -o ",outdir," SEQN=",seqn)
  if (!file.exists(vdbres) || !is.null(opt$redo)) {
    writeLines(paste0("**************************************************************",
                      "\n*** Starting Age script (Sequence #",seqn,")",
                      "\n**************************************************************",
                      "\nTo monitor progress, run: \"tail -f ",vdbcon,"\" from another session."))
    writeLines(paste("Arguments for vdbench:",vdbmsg))
    tryRun = try(system2(command=vdbexe,args=vdbarg,stdout=vdbcon,stderr=vdberr))
    if (tryRun!=0) {
      writeLines(paste0("*** PoC Age (Seqn #",seqn,
                        ") script did *NOT* complete successfully ***",
                        "\nPlease see: \n   CONSOLE -- ",vdbcon,
                        "\n   ERROR -- ",vdberr,"\nfor more information.\n"))
      return(1)
    } else {
      writeLines(paste0("*** SUCCESSFUL Age (Seqn #",seqn,") script run! ***",
                        "\nResults data is in:",vdbres,"\n"))
      return(read.vdb(file = vdbres))
    }
  } else {
    writeLines(paste0("*** Skipping Age (Seqn #",seqn,
                      ") script because results file exists and redo not requested. ***\n"))
    return(read.vdb(file = vdbres))
  }  
  # Should never get here
  return(-1)
}

# run.vdb.phase.profile() --
#   Function to run vdbench for the profiling phase of the AFA PoC toolkit. If  
#   the run ends successfully, the output directory will contain a profile 
#   subdirectory which includes a flatfile with the measurement results. This  
#   function should be run within the context of the afa_poc script to pick up 
#   required environment variables. 
# Arguments --
#         env : Path to the environment fileo
#         dur : Duration of each measured Profile run
#    capacity : Amount of IO to generate (capacity of LUNs to age)
#    curvepts : Percentage of maximum to measure for Profile curve
#     readpct : Read percent points to measure during Profiling
#       smthr : Number of threads per LUN for Small IO sizes
#       lgthr : Number of threads per LUN for Large IO sizes
#        seqn : Sequence number for phase name in run description
# Returns --
# success/skipped :  vdbench data frame with parsed results
#      fail/abort :  1
#             wtf : -1
run.vdb.phase.profile = function(env,dur,capacity,curvepts,readpct,smthr,lgthr,seqn) 
{
  outdir = paste0(outdir,"/profile_",seqn,"/")
  dir.create(outdir,showWarnings=FALSE)
  vdbphase = "/root/AFA/profile_param.vdb"
  vdbcon = paste0(outdir,opt$tag,"-out.txt")
  vdberr = paste0(outdir,opt$tag,"-err.txt")
  vdbres = paste0(outdir,"flatfile.html")
  vdbarg = paste0(vdbsim," -f ",vdbphase," -o ",outdir," ENV=",env," TIME=",dur," CAPACITY=",capacity,"g"," SEQN=",seqn," CURVEPTS=",curvepts," READPCT=",readpct," SM_THREAD=",smthr," LG_THREAD=",lgthr)
  vdbmsg = paste0(vdbsim," -f ",vdbphase," -o ",outdir," SEQN=",seqn)
  if (!file.exists(vdbres) || !is.null(opt$redo)) {
    writeLines(paste0("**************************************************************",
                      "\n***                      Starting Profile script (Sequence #",seqn,")",
                      "\n**************************************************************",
                      "\nTo monitor progress, run: \"tail -f ",vdbcon,"\" from another session."))
    writeLines(paste("Arguments for vdbench:",vdbmsg))
    tryRun = try(system2(command=vdbexe,args=vdbarg,stdout=vdbcon,stderr=vdberr))
    if (tryRun!=0) {
      writeLines(paste0("*** PoC Profile (Seqn #",seqn,
                        ") script did *NOT* complete successfully ***",
                        "\nPlease see: \n   CONSOLE -- ",vdbcon,
                        "\n   ERROR -- ",vdberr,"\nfor more information.\n"))
      return(1)
    } else {
      writeLines(paste0("*** SUCCESSFUL Profile (Seqn #",seqn,") script run! ***",
                        "\nResults data is in:",vdbres,"\n"))
      return(read.vdb(file = vdbres))
    }
  } else {
    writeLines(paste0("*** Skipping Profile (Seqn #",seqn,
                      ") script because results file exists and redo not requested. ***\n"))
    return(read.vdb(file = vdbres))
  }  
  # Should never get here
  return(-1)
}

# run.vdb.phase.steady() --
#   Function to run vdbench for the steady-state phase of the AFA PoC toolkit.  
#   If the run ends successfully, the output directory will contain an age 
#   subdirectorywhich includes a flatfile with the measurement results. This  
#   function should be run within the context of the afa_poc script to pick up 
#   required environment variables. 
# Arguments --
#         env : Path to the environment fileo
#         dur : Maximum duration of phase (for preflight)
#    capacity : Amount of IO to generate (capacity of LUNs to age)
#     threads : Number of threads per LUN to ensure sufficient load
#        seqn : Sequence number for phase name in run description
# Returns --
# success/skipped :  vdbench data frame with parsed results
#      fail/abort :  1
#             wtf : -1
run.vdb.phase.steady = function(env,dur,capacity,threads,seqn) 
{
  outdir = paste0(outdir,"/steady_",seqn,"/")
  dir.create(outdir,showWarnings=FALSE)
  vdbphase = "/root/AFA/steady_param.vdb"
  vdbcon = paste0(outdir,opt$tag,"-out.txt")
  vdberr = paste0(outdir,opt$tag,"-err.txt")
  vdbres = paste0(outdir,"flatfile.html")
  vdbarg = paste0(vdbsim," -f ",vdbphase," -o ",outdir," ENV=",env," TIME=",dur," CAPACITY=",capacity,"g"," SEQN=",seqn," THREAD=",threads)
  vdbmsg = paste0(vdbsim," -f ",vdbphase," -o ",outdir," SEQN=",seqn)
  if (!file.exists(vdbres) || !is.null(opt$redo)) {
    writeLines(paste0("**************************************************************",
                      "\n***                 Starting Steady-State script (Sequence #",seqn,")",
                      "\n**************************************************************",
                      "\nTo monitor progress, run: \"tail -f ",vdbcon,"\" from another session."))
    writeLines(paste("Arguments for vdbench:",vdbmsg))
    tryRun = try(system2(command=vdbexe,args=vdbarg,stdout=vdbcon,stderr=vdberr))
    if (tryRun!=0) {
      writeLines(paste0("*** PoC Steady-State (Seqn #",seqn,
                        ") script did *NOT* complete successfully ***",
                        "\nPlease see: \n   CONSOLE -- ",vdbcon,
                        "\n   ERROR -- ",vdberr,"\nfor more information.\n"))
      return(1)
    } else {
      writeLines(paste0("*** SUCCESSFUL Steady-State (Seqn #",seqn,") script run! ***",
                        "\nResults data is in:",vdbres,"\n"))
      return(read.vdb(file = vdbres))
    }
  } else {
    writeLines(paste0("*** Skipping Steady-State (Seqn #",seqn,
                      ") script because results file exists and redo not requested. ***\n"))
    return(read.vdb(file = vdbres))
  }  
  # Should never get here
  return(-1)
}

### Run script to prepare the array for snapshot testing
run.vdb.phase.snapprep = function() {
}

# run.vdb.phase.snapsteady() --
#   Function to run vdbench for the snapsteady phase of the AFA PoC toolkit.  
#   If the run ends successfully, the output directory will contain a snapsteady 
#   subdirectory which includes a flatfile with the measurement results. This  
#   function should be run within the context of the afa_poc script to pick up 
#   required environment variables. 
# Arguments --
#         env : Path to the environment fileo
#         dur : Maximum duration of phase (for preflight)
#    capacity : Amount of IO to generate (capacity of LUNs to age)
#     threads : Number of threads per LUN to ensure sufficient load
#        seqn : Sequence number for phase name in run description
# Returns --
# success/skipped :  vdbench data frame with parsed results
#      fail/abort :  1
#             wtf : -1
run.vdb.phase.snapsteady = function(dur,capacity,threads,seqn) 
{
  outdir = paste0(outdir,"/snapsteady_",seqn,"/")
  dir.create(outdir,showWarnings=FALSE)
  vdbphase = "/root/AFA/snapsteady_param.vdb"
  vdbcon = paste0(outdir,opt$tag,"-out.txt")
  vdberr = paste0(outdir,opt$tag,"-err.txt")
  vdbres = paste0(outdir,"flatfile.html")
  vdbarg = paste0(vdbsim," -f ",vdbphase," -o ",outdir," TIME=",dur," CAPACITY=",capacity,"g"," SEQN=",seqn," THREAD=",threads)
  vdbmsg = paste0(vdbsim," -f ",vdbphase," -o ",outdir," SEQN=",seqn)
  if (!file.exists(vdbres) || !is.null(opt$redo)) {
    writeLines(paste0("**************************************************************",
                      "\n***                  Starting SnapSteady script (Sequence #",seqn,")",
                      "\n**************************************************************",
                      "\nTo monitor progress, run: \"tail -f ",vdbcon,"\" from another session."))
    writeLines(paste("Arguments for vdbench:",vdbmsg))
    tryRun = try(system2(command=vdbexe,args=vdbarg,stdout=vdbcon,stderr=vdberr))
    if (tryRun!=0) {
      writeLines(paste0("*** PoC snapsteady (Seqn #",seqn,
                        ") script did *NOT* complete successfully ***",
                        "\nPlease see: \n   CONSOLE -- ",vdbcon,
                        "\n   ERROR -- ",vdberr,"\nfor more information.\n"))
      return(1)
    } else {
      writeLines(paste0("*** SUCCESSFUL snapsteady (Seqn #",seqn,") script run! ***",
                        "\nResults data is in:",vdbres,"\n"))
      return(read.vdb(file = vdbres))
    }
  } else {
    writeLines(paste0("*** Skipping snapsteady (Seqn #",seqn,
                      ") script because results file exists and redo not requested. ***\n"))
    return(read.vdb(file = vdbres))
  }  
  # Should never get here
  return(-1)
}

