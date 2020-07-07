#ifndef SD_h
#define SD_h 1

#include "G4VSensitiveDetector.hh"
#include "Hit.hh"
#include <fstream>

using namespace std;

class G4Step;
class G4HCofThisEvent;
class G4TouchableHistory;
class G4GenericMessenger;

/// Hodoscope sensitive detector

class SD : public G4VSensitiveDetector
{
public:
    SD(G4String name,G4String filename);
    virtual ~SD();
    
    virtual void Initialize(G4HCofThisEvent*HCE);
    virtual G4bool ProcessHits(G4Step*aStep,G4TouchableHistory*ROhist);
    
private:
    HitsCollection* fHitsCollection;
    G4int fHCID;
	G4double totalHits;
	G4double prevHit;
	G4GenericMessenger* fMessenger;
	ofstream file;
};

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

#endif
