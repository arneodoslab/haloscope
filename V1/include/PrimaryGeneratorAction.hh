
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
/// A single particle is generated.
/// User can select 
/// - the initial momentum and angle
/// - the momentum and angle spreads
/// - random selection of a particle type from proton, kaon+, pi+, muon+, e+ 


class PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction
{
public:
    PrimaryGeneratorAction();
    virtual ~PrimaryGeneratorAction();
    
    virtual void GeneratePrimaries(G4Event*);
    
    //void SetMomentum(G4double val) { fMomentum = val; }
    //G4double GetMomentum() const { return fMomentum; }

    //void SetSigmaMomentum(G4double val) { fSigmaMomentum = val; }
    //G4double GetSigmaMomentum() const { return fSigmaMomentum; }

   // void SetSigmaAngle(G4double val) { fSigmaAngle = val; }
    //G4double GetSigmaAngle() const { return fSigmaAngle; }

    //void SetRandomize(G4bool val) { fRandomizePrimary = val; }
    //G4bool GetRandomize() const { return fRandomizePrimary; }
    
private:
    //void DefineCommands();

	G4GeneralParticleSource* generator;
    G4ParticleGun* fParticleGun;
    G4GenericMessenger* fMessenger;
    //G4ParticleDefinition* fPositron;
    //G4ParticleDefinition* fMuon;
    //G4ParticleDefinition* fPion;
    //G4ParticleDefinition* fKaon;
    //G4ParticleDefinition* fProton;
	G4ParticleDefinition* fPhoton;
    //G4double fMomentum;
    //G4double fSigmaMomentum;
    //G4double fSigmaAngle;
    //G4bool fRandomizePrimary;
};

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

#endif
