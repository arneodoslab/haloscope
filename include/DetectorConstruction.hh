
// $Id: DetectorConstruction.hh 76474 2013-11-11 10:36:34Z gcosmo $
//
/// \file DetectorConstruction.hh
/// \brief Definition of the DetectorConstruction class

#ifndef DetectorConstruction_h
#define DetectorConstruction_h 1

#include "globals.hh"
#include "G4VUserDetectorConstruction.hh"
#include "G4RotationMatrix.hh"
#include "G4FieldManager.hh"

#include <vector>

class G4VPhysicalVolume;
class G4Material;
class G4VisAttributes;
class G4GenericMessenger;

/// Detector construction

class DetectorConstruction : public G4VUserDetectorConstruction
{
public:
    DetectorConstruction();
    virtual ~DetectorConstruction();
    
    //Here the geomtry is constructed. This method is called only by
    //master thread and all geometry built here is shared among threads
    virtual G4VPhysicalVolume* Construct();

    //This is just a convinience: a method where all materials needed
    //are created
    void ConstructMaterials();

	//These are some command methods
	void zPos(G4double pos);
	void filenameChange(G4String file);
    
private:

    G4GenericMessenger* fMessenger;
    
    std::vector<G4VisAttributes*> fVisAttributes;

	G4double fzPos;
	G4VPhysicalVolume* boxPhysical;
	G4String filename;
};

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

#endif
