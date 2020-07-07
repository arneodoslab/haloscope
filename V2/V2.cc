// example.cc 70284 2013-05-28 17:26:43Z perl $
//
/// \file V2.cc
/// \brief Main program of the analysis

#include "DetectorConstruction.hh"
#include "ActionInitialization.hh"
#include "G4ScoringManager.hh"

//#define G4MULTITHREADED

#ifdef G4MULTITHREADED
#include "G4MTRunManager.hh"
#else
#include "G4RunManager.hh"
#endif

#include "G4UImanager.hh"
#include "FTFP_BERT.hh"
#include "G4OpticalPhysics.hh"
#include "G4EmStandardPhysics_option4.hh"

#include "G4StepLimiterPhysics.hh"

#include "G4VisExecutive.hh"
#include "G4UIterminal.hh"
#include "G4UItcsh.hh"

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

int main(int argc,char** argv)
{
  // Construct the default run manager
  // Note that if we have built G4 with support for Multi-threading we set it here
#ifdef G4MULTITHREADED
    G4MTRunManager* runManager = new G4MTRunManager;
    //Set the default number of threads to be the number of available cores of the machine
    //If not specified use 2 threads
    runManager->SetNumberOfThreads( 4 );
    G4cout << "\t\t\t\tMULTITHREADING ON!" << G4endl;
#else
    G4RunManager* runManager = new G4RunManager;
    G4cout << "\t\t\t\tMULTITHREADING OFF!" << G4endl;
#endif
    
	//====================
	//Command Scoring
    G4ScoringManager * scManager = G4ScoringManager::GetScoringManager();
    scManager->SetVerboseLevel(1);
    // Mandatory user initialization classes
    
    //====================
    //The Geometry
    runManager->SetUserInitialization(new DetectorConstruction);
    
    //====================
    //The Physics

	//Adding Optical Physics
	G4VModularPhysicsList* physicsList = new FTFP_BERT;
	physicsList->ReplacePhysics(new G4EmStandardPhysics_option4());
	G4OpticalPhysics* opticalPhysics = new G4OpticalPhysics();
	opticalPhysics->SetWLSTimeProfile("delta");

	opticalPhysics->SetScintillationYieldFactor(1.0);
	opticalPhysics->SetScintillationExcitationRatio(0.0);

	opticalPhysics->SetMaxNumPhotonsPerStep(10000);
	opticalPhysics->SetMaxBetaChangePerStep(10.0);

	opticalPhysics->SetTrackSecondariesFirst(kCerenkov, true);

	physicsList->RegisterPhysics(opticalPhysics);
	runManager->SetUserInitialization(physicsList);

    
    //====================
    // User action initialization
    runManager->SetUserInitialization(new ActionInitialization());
    
    // Visualization manager construction
    G4VisManager* visManager = new G4VisExecutive;
    // G4VisExecutive can take a verbosity argument - see /vis/verbose guidance.
    // G4VisManager* visManager = new G4VisExecutive("Quiet");
    visManager->Initialize();
    
    // Get the pointer to the User Interface manager
    G4UImanager* UImanager = G4UImanager::GetUIpointer();

    if (argc>1) {
        // execute an argument macro file if exist
        G4String command = "/control/execute ";
        G4String fileName = argv[1];
        UImanager->ApplyCommand(command+fileName);
    }
    else {
      //We have visualization, initialize defaults: look in init_vis.mac macro
      UImanager->ApplyCommand("/control/execute init_vis.mac");
      auto ui = new G4UIterminal(new G4UItcsh);
      ui->SessionStart();
      delete ui;
    }
    // Job termination
    delete visManager;
    delete runManager;
    
    return 0;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......
