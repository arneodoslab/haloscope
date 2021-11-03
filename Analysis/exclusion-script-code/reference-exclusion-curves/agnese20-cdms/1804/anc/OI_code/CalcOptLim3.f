      Program CalcOptLim3
C Get data from a file named "ULinput". ULinput in the present version of the
C Optimum Interval (OI) code contains one DM mass at a time (as opposed to all
C DM masses at once). The input information is listed in a single column:
C   * 1st entry in the column: probed parameter (e.g. the coupling of DM to a SM
C     particle, or in general a point on the ordinate of the limit curve). An initial
C     assumption is to be given here, which will be used as starting point for the
C     calculation.
C   * 2nd entry: model assumption (e.g. the DM mass, or in general a point on the
C     abscissa of the limit curve).
C   * All following entries: all events in order of increasing energy. For each event,
C     the probability is given for the event having lower energy. So, for example,
C     suppose the distribution of events is expected to be uniform from 5 to 100 keV,
C     and suppose there are 2 events, one at 10 keV and one at 50 keV. Then given an
C     event, it has probability (10-5)/(100-5) = 0.05263 of being below 10 keV and
C     probability (50-5)/(100-5) = 0.47368 of being below 50 keV.
C Append the results per model assumption (e.g. the DM mass) to the end of a file
C named "ULoutput". The results are listed in rows:
C   * 1st entry in the row: the value of the resulting parameter limit at 90% CL.
C   * 2nd entry: the model assumption (e.g. the DM mass).
C   * 3rd entry: status flag from the OI code. See comments in UpperLimNew3.f for details.
C   * 4th and 5th entry: the values of I in FC(I) for the endpoints of the OI.
C   * 6th and 7th entry: the lower and upper bound in case of an excluded range around
C     the 90% CL limit returned. If the status flag in the 3rd entry is >= 256, more than
C     one solution exists and the sixth and seventh entry define the range of solutions.
C Compile with
C  f77 -o CalcOptLim3 CalcOptLim3.f UpperLimNew3.f y_vs_CLf2.f CMaxinfNew2.f ConfLev2.f ConfLevNew2.f Cinf2.f CERN_Stuff2.f
C or "f77" -> "gfortran -frecord-marker=4".
      Implicit None
      Integer*8 If,N,Iflag,EP
      Real*8 sigma,mu0,sigma0,muB,CL,Mw,fc0
C     Must increase length FC if more than 500000 events!!!
      Real*8 UpperLim,FC(0:500000),FB(0:500000),El
      Common/UpperLimcom/EP(2),El(2)
      Open(unit=25,form='FORMATTED',file='ULoutput', access='APPEND')
      Call FillFC(FC,N,mu0,sigma0,Mw)
C Now fill the background vectors
C      Call FillFB(FB,muB)

      CL=0.9D0                    ! 90% Confidence level
      If=1                      ! fmin = 0.
      muB=0.D0                    ! Don't subtract background
      
C      fc0=UpperLim(CL,If,N,FC,muB,FC,Iflag,Ist,Ien)
      fc0=UpperLim(CL,If,N,FC,muB,FB,Iflag)

      sigma=(sigma0/mu0)*fc0
      El(1)=(sigma0/mu0)*El(1)
      El(2)=(sigma0/mu0)*El(2)
C      sigma = fc0

C     sigma is now the upper limit cross section.  Iflag is a status; 0 is good.
      Write(25,10) sigma,Mw,Iflag,EP(1),EP(2),El(1),El(2)
C     Write(25,20) FC
 10   Format(E13.6,E13.6,I5,I16,I16,E13.6,E13.6)
C     20   Format(E13.6)
      Stop
      End
C 
      Subroutine FillFC(FC,N,mu0,sigma0,Mw)
C FillFC reads from a table "ULinput" (see header of this file for its format).
      Implicit None
      Real*8 mu0,Mw,sigma0
      Real*8 FC(0:500000) ! FC(I) contains the probability for the I'th event.
      Integer*8 N ! The number of events read in
      Open(unit=50,form='FORMATTED',status='OLD',file='ULinput')
      Read(50,30) sigma0
      Read(50,20) Mw
      Read(50,30) mu0
      N=0
 10   continue
      N=N+1
      Read(50,30,END=100) FC(N)
 20   Format(F10.6)
      Go to 10
 30   Format(E12.6)
      Go to 10
 100  N = N-1
      Return
      End


      Subroutine FillFB(FB,muB)
C Same as FillFC, but reads from a table "BGinput" for the background vectors. If no
C backgrounds are subtracted, BGinput simply contains one entry: 0.0e+00.
      Implicit None
      Real*8 muB
      Real*8 FB(0:500000) ! FB(I) contains the probability for the I'th event.
      Integer*8 N                 ! The number of events read in
      Open(unit=50,form='FORMATTED',status='OLD',file='BGinput')
      Read(50,30) muB
      N=0
 10   continue
      N=N+1
      Read(50,30,END=100) FB(N)
 20   Format(F10.6)
      Go to 10
 30   Format(E12.6)
      Go to 10
 100  N = N-1
      Return
      End
