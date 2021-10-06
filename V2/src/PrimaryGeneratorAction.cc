
// $Id: PrimaryGeneratorAction.cc 77781 2013-11-28 07:54:07Z gcosmo $
//
/// \file PrimaryGeneratorAction.cc
/// \brief Implementation of the PrimaryGeneratorAction class

#include "PrimaryGeneratorAction.hh"

#include "G4Event.hh"
#include "G4ParticleGun.hh"
#include "G4GeneralParticleSource.hh"
#include "G4OpticalPhoton.hh"
#include "G4ParticleTable.hh"
#include "G4ParticleDefinition.hh"
#include "G4GenericMessenger.hh"
#include "G4SystemOfUnits.hh"
#include "Randomize.hh"
#include "globals.hh"

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

PrimaryGeneratorAction::PrimaryGeneratorAction()
{
	generator = new G4GeneralParticleSource();

    G4int n_particle = 1;
    fParticleGun  = new G4ParticleGun(n_particle);
    
    G4ParticleTable* particleTable = G4ParticleTable::GetParticleTable();
    G4String particleName;
	fPhoton = particleTable->FindParticle(particleName="opticalphoton");
    
    // default particle kinematics
	fParticleGun->SetParticleEnergy(2.*eV);
    fParticleGun->SetParticleDefinition(G4OpticalPhoton::OpticalPhotonDefinition());
	fParticleGun->SetParticleMomentumDirection(G4ThreeVector(0.,0.,1.));
	
	G4double angle = G4UniformRand() * 360.0*deg;
	G4ThreeVector polar = std::cos(angle)*G4ThreeVector(1,0,0) + std::sin(angle)*G4ThreeVector(0,1,0);
	fParticleGun->SetParticlePolarization(polar);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

PrimaryGeneratorAction::~PrimaryGeneratorAction()
{
    delete fParticleGun;
    //delete fMessenger;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* event)
{   
    fParticleGun->GeneratePrimaryVertex(event);
	G4double r = G4UniformRand()*4.25/2*cm;
	G4double theta = G4UniformRand()*360*deg;
	G4double pos3 = G4UniformRand()*10*um;
    fParticleGun->SetParticlePosition(G4ThreeVector(r*std::cos(theta),r*std::sin(theta),pos3));
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......
