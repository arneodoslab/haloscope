
// $Id: PrimaryGeneratorAction.hh 76474 2013-11-11 10:36:34Z gcosmo $
//
/// \file PrimaryGeneratorAction.hh
/// \brief Definition of the PrimaryGeneratorAction class

#ifndef PrimaryGeneratorAction_h
#define PrimaryGeneratorAction_h 1

#include "G4VUserPrimaryGeneratorAction.hh"
#include "globals.hh"

class G4ParticleGun;
class G4GenericMessenger;
class G4Event;
class G4ParticleDefinition;
class G4GeneralParticleSource;

/// Primary generator
///
/// A single particle is generated, at a random position within the lens


class PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction
{
public:
    PrimaryGeneratorAction();
    virtual ~PrimaryGeneratorAction();
    
    virtual void GeneratePrimaries(G4Event*);
    
private:

	G4GeneralParticleSource* generator;
    G4ParticleGun* fParticleGun;
    G4GenericMessenger* fMessenger;
	G4ParticleDefinition* fPhoton;
};

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

#endif
