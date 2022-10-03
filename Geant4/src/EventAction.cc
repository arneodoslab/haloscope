#include "EventAction.hh"
#include "Hit.hh"

#include "G4Event.hh"
#include "G4RunManager.hh"
#include "G4EventManager.hh"
#include "G4HCofThisEvent.hh"
#include "G4VHitsCollection.hh"
#include "G4SDManager.hh"
#include "G4SystemOfUnits.hh"
#include "G4ios.hh"

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

EventAction::EventAction()
: G4UserEventAction(), 
  det(-1)
{
  // set printing per each event
  G4RunManager::GetRunManager()->SetPrintProgress(1);     
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

EventAction::~EventAction()
{}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void EventAction::BeginOfEventAction(const G4Event*)
{
    if (det==-1) {
      G4SDManager* sdManager = G4SDManager::GetSDMpointer();
      det = sdManager->GetCollectionID("detector/Coll");
    }
}     

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void EventAction::EndOfEventAction(const G4Event* event)
{   


		

    G4HCofThisEvent* hce = event->GetHCofThisEvent();
    if (!hce) 
    {
        G4ExceptionDescription msg;
        msg << "No hits collection of this event found.\n"; 
        G4Exception("EventAction::EndOfEventAction()",
                    "Code001", JustWarning, msg);
        return;
    }   

    // Get hits collections 
    HitsCollection* detC 
      = static_cast<HitsCollection*>(hce->GetHC(det));
      
      
    if (!detC)
    {
        G4ExceptionDescription msg;
        msg << "Some of hits collections of this event not found.\n"; 
        G4Exception("EventAction::EndOfEventAction()",
                    "Code001", JustWarning, msg);
        return;
    }   
    
    //
    // Print diagnostics
    // 
    
    G4int printModulo = G4RunManager::GetRunManager()->GetPrintProgress();
    if ( printModulo==0 || event->GetEventID() % printModulo != 0) return;
    
    G4PrimaryParticle* primary = event->GetPrimaryVertex(0)->GetPrimary(0);
    G4cout << G4endl
           << ">>> Event " << event->GetEventID() << " >>> Simulation truth : "
           << primary->GetG4code()->GetParticleName()
           << " " << primary->GetMomentum() << G4endl;
    
    // Step 3: Loop on the two collections and dump on screen hits
    G4int n_hit = detC->entries();
    G4cout << "Detector has " << n_hit << " hits." << G4endl;
    for (G4int i=0;i<n_hit;i++)
    {
        AHit* hit = (*detC)[i];
        hit->Print();
    }

    
}

