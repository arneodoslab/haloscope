#include "SD.hh"
#include "Hit.hh"

#include "G4HCofThisEvent.hh"
#include "G4TouchableHistory.hh"
#include "G4Track.hh"
#include "G4Step.hh"
#include "G4SDManager.hh"
#include "G4ios.hh"
#include "G4SystemOfUnits.hh"
#include "G4GenericMessenger.hh"

#include <stdio.h>

using namespace std;

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

SD::SD(G4String name,G4String filename)
: G4VSensitiveDetector(name), fHitsCollection(0), fHCID(-1), totalHits(0), prevHit(0)
{
    G4String HCname = "Coll";
    collectionName.insert(HCname);
	G4cout << "\tCreated Sensitive detector.\n\n\t" << filename << endl;
	
	file.open(filename,ofstream::app);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

SD::~SD()
{
	delete fMessenger;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SD::Initialize(G4HCofThisEvent* hce)
{
    fHitsCollection = new HitsCollection(SensitiveDetectorName,collectionName[0]);
    if (fHCID<0)
    { fHCID = G4SDManager::GetSDMpointer()->GetCollectionID(fHitsCollection); }
    hce->AddHitsCollection(fHCID,fHitsCollection);
	prevHit = 0;
	G4cout << "\t\t\t\tInitialized Sensitive detector\n\n"; 
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

G4bool SD::ProcessHits(G4Step* step, G4TouchableHistory*)
{
    G4cout << "\t\t\t\tProcessing a step!\n";
    G4double edep = step->GetTotalEnergyDeposit();
	G4cout << "\t\t\t\tEnergy Deposited: " << edep << G4endl;
	
	G4cout << "\t\t\t\tTotal Photons: " << totalHits << G4endl;
    if (edep!=0.){
		if(prevHit == 0){
				totalHits++;
				prevHit = 1;
			}
		G4StepPoint* preStepPoint = step->GetPreStepPoint();

    	G4TouchableHistory* touchable = (G4TouchableHistory*)(preStepPoint->GetTouchable());
		G4int copyNo = touchable->GetVolume()->GetCopyNo();
    	G4double hitTime = preStepPoint->GetGlobalTime();
		AHit* hit = new AHit(copyNo,hitTime);
      	fHitsCollection->insert(hit);

		G4cout << "Position: "<< preStepPoint->GetPosition();
		file << preStepPoint->GetPosition()[0]/mm <<","<< preStepPoint->GetPosition()[1]/mm << "," << preStepPoint->GetPosition()[2]/mm << " ";


		G4StepPoint* postStepPoint = step->GetPostStepPoint();

    	G4TouchableHistory* touchable2 = (G4TouchableHistory*)(postStepPoint->GetTouchable());
		G4int copyNo2 = touchable2->GetVolume()->GetCopyNo();
    	G4double hitTime2 = postStepPoint->GetGlobalTime();
		AHit* hit2 = new AHit(copyNo2,hitTime2);
      	fHitsCollection->insert(hit2);

		G4cout << " "<< postStepPoint->GetPosition() << G4endl;
		file << postStepPoint->GetPosition()[0]/mm <<","<< postStepPoint->GetPosition()[1]/mm << "," << postStepPoint->GetPosition()[2]/mm << endl;
		
		return true;
	}
    
    G4StepPoint* preStepPoint = step->GetPreStepPoint();

    G4TouchableHistory* touchable
      = (G4TouchableHistory*)(preStepPoint->GetTouchable());
    
	G4int copyNo = touchable->GetVolume()->GetCopyNo();
    G4double hitTime = preStepPoint->GetGlobalTime();
    
    // check if this detector already has a hit
    G4int ix = -1;
    for (G4int i=0;i<fHitsCollection->entries();i++)
    {
        if ((*fHitsCollection)[i]->GetID()==copyNo)
        {
            ix = i;
            break;
        }
    }

    if (ix>=0)
        // if it has, then take the earlier time
    {
        if ((*fHitsCollection)[ix]->GetTime()>hitTime)
        { (*fHitsCollection)[ix]->SetTime(hitTime); }
    }
    else
        // if not, create a new hit and set it to the collection
    {
		AHit* hit = new AHit(copyNo,hitTime);
      	fHitsCollection->insert(hit);
    }    
    return true;
}
