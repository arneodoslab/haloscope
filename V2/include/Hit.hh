//
// ********************************************************************
// * License and Disclaimer                                           *
// *                                                                  *
// * The  Geant4 software  is  copyright of the Copyright Holders  of *
// * the Geant4 Collaboration.  It is provided  under  the terms  and *
// * conditions of the Geant4 Software License,  included in the file *
// * LICENSE and available at  http://cern.ch/geant4/license .  These *
// * include a list of copyright holders.                             *
// *                                                                  *
// * Neither the authors of this software system, nor their employing *
// * institutes,nor the agencies providing financial support for this *
// * work  make  any representation or  warranty, express or implied, *
// * regarding  this  software system or assume any liability for its *
// * use.  Please see the license in the file  LICENSE  and URL above *
// * for the full disclaimer and the limitation of liability.         *
// *                                                                  *
// * This  code  implementation is the result of  the  scientific and *
// * technical work of the GEANT4 collaboration.                      *
// * By using,  copying,  modifying or  distributing the software (or *
// * any work based  on the software)  you  agree  to acknowledge its *
// * use  in  resulting  scientific  publications,  and indicate your *
// * acceptance of all terms of the Geant4 Software license.          *
// ********************************************************************
//
// $Id: HodoscopeHit.hh 76474 2013-11-11 10:36:34Z gcosmo $
//
/// \file HodoscopeHit.hh
/// \brief Definition of the HodoscopeHit class

#ifndef AHit_h
#define AHit_h 1

#include "G4VHit.hh"
#include "G4THitsCollection.hh"
#include "G4Allocator.hh"
#include "G4ThreeVector.hh"
#include "G4LogicalVolume.hh"
#include "G4Transform3D.hh"
#include "G4RotationMatrix.hh"

class G4AttDef;
class G4AttValue;

/// Hit
///
/// It records:
/// - the strip ID
/// - the particle time

// =============================================
// Exercise 2 Step 1:
// Create a hit class for the hodoscpe
//    A hit is characterized by: an index (which hodoscope
//    tile has fired, and the time of the fire
//    Complete this class as appropriate
//  The following methods should be preapred:
//    - Constructor with two parameters (index and time)
//    - Operator new and delete that use an allocator
//    - Setters and Getters for index and time
//    - A Print method that dumps on G4cout the information
//      contained in the hit

class AHit : public G4VHit
{
public:
    AHit(G4int i,G4double t);
    virtual ~AHit() {}
    
    inline void *operator new(size_t);
    inline void operator delete(void*aHit);

    void Print();
    
    G4int GetID() const { return fId; }

    void SetTime(G4double val) { fTime = val; }
    G4double GetTime() const { return fTime; }
    
private:
    G4int fId;
    G4double fTime;
};

typedef G4THitsCollection<AHit> HitsCollection;

extern G4ThreadLocal G4Allocator<AHit>* HitAllocator;

inline void* AHit::operator new(size_t)
{
    if (!HitAllocator)
        HitAllocator = new G4Allocator<AHit>;
    return (void*)HitAllocator->MallocSingle();
}

inline void AHit::operator delete(void*aHit)
{
    HitAllocator->FreeSingle((AHit*) aHit);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

#endif
