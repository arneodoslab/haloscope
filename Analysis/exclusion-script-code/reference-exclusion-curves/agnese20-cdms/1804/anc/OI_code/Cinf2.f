      Real*8 Function Cinf(y,fin,Istat)
C Calculates C_\infty from a table.
C Input: y = deviation, fin = fraction of the range
C Output: Cinf=C_\infty(y,fin), Istat = return status code
C Istat  Meaning
C   0    Result interpolated from table ymintable.in
C   1    Result extrapolated from f0=.01 (lowest f in the table)
C   2    y especially low.  Returns Cinf=1.
C   3    y especially high.  Returns Cinf=0.
C   4    Result estimated using derfc (not implemented)
C   5    failure: fin > 1
C   6    failure: fin < 1.E-10
      Implicit none
      Integer*8 Nf,Nmin,Ntrials,Ntable,If,Ibin,Istat
      Real*8 y,ytemp,f,ytable,ylow,yhigh,flog,Table(2000,100),FNf,
     1 fbin,ybin,dfbin,dIbin,dy,fin,f0/.01D0/
      Real*4 ylow4,yhigh4,Table4(2000,100)
      Integer*4 Nmin4,Nf4,NTable4,Ntrials4
      Logical first/.true./
      Common/Cinfcom/Nf,Ntable,ylow,yhigh,dy,FNf,Table
      If(first) Then
       first=.false.
C       Open(50,file='ymintable.in',status='OLD',form='UNFORMATTED')
       Open(50,file='ymintable.txt',status='OLD',form='FORMATTED')
C       Read(50) ylow4,yhigh4,Nmin4,Nf4,NTable4,Ntrials4
       Read(50,5) ylow4,yhigh4,Nmin4,Nf4,NTable4,Ntrials4
 5     Format(2F9.5,3I5,I9)
       ylow=ylow4
       yhigh=yhigh4
       Nmin=Nmin4
       Nf=Nf4
       NTable=Ntable4
       Ntrials=Ntrials4
       Do If=1,Nf
C          Read(50) (Table4(Ibin,If),Ibin=1,Ntable)
          Read(50,10) (Table4(Ibin,If),Ibin=1,Ntable)
 10       Format(10F9.6)
          Do Ibin=1,Ntable
             Table(Ibin,If)=Table4(Ibin,If)
          EndDo
       EndDo
       dy=(yhigh-ylow)/dfloat(Ntable)
       FNf=dfloat(Nf)
       Close(50)
      EndIf
      Istat=0 ! Default for success
      Cinf=1.D0 ! Default for failure
      f=fin
      If(f.gt.1.D0) Then
         Istat=4
         Return
      EndIf
      If(f.lt.1.D-10) Then
         Istat=5
         Return
      EndIf
      If(f.lt.0.01D0) Then
         Istat=1
         f=f0
      EndIf
      flog=dlog(f)
      ytemp=y*(1.D0 - 0.3D0*flog) - 1.7D0*flog
      If(ytemp.lt.ylow) Then
         Istat=2
         Cinf=1.D0
         Return
      Elseif(ytemp.gt.yhigh) Then
         Istat=3
         Cinf=0.
         Return
      EndIf
      fbin=f*FNf
      If=fbin
      If(If.lt.1) If=1
C      If(If.gt.Nf-2) If=Nf-2
      If(If.gt.Nf-1) If=Nf-1
      dfbin=fbin-dFloat(If)
      ybin=(ytemp-ylow)/dy
      Ibin=ybin
      If(Ibin.lt.2) Ibin=2
      If(Ibin.gt.Ntable-1) Ibin=Ntable-1
      dIbin=ybin-dFloat(Ibin)
C To check the following interpolation formula, verify that it gives
C the correct 4 table entries when dfbin is close to 0 and 1 and when
C dIbin is close to 0 and 1.  Table(Ibin,If)=Cinf evaluated at
C ytemp=ylow+dy*Ibin, f=If/FNf.
      Cinf=(1.D0-dfbin)*(dIbin*Table(Ibin+1,If)+(1.D0-dIbin)*
     1 Table(Ibin,If)) +dfbin*(dIbin*Table(Ibin+1,If+1)+
     2 (1.D0-dIbin)*Table(Ibin,If+1))
      If(Istat.eq.1) Cinf=Cinf**((1.D0/fin - 0.94D0)/(1.D0/f0 - 0.94D0))
      Return
      End

