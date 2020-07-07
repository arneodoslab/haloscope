// Id: ActionInitialization.hh 68058 2013-03-13 14:47:43Z gcosmo $
//
/// \file ActionInitialization.hh
/// \brief Definition of the ActionInitialization class

#ifndef ActionInitialization_h
#define ActionInitialization_h 1

#include "G4VUserActionInitialization.hh"

/// Action initialization class.

class ActionInitialization : public G4VUserActionInitialization
{
  public:
    ActionInitialization();
    virtual ~ActionInitialization();

    //This is called by the master thread.
    //You may want to create here an instance of RunAction
    //To allow merging of results from threads
    virtual void BuildForMaster() const;
    
    //This is called by each worker thread.
    //Create here the user-actions needed by each thread:
    // RunAction, EventAction, SteppingAction, StackingAction
    virtual void Build() const;

};

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

#endif

    
