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
// $Id: PrimaryGeneratorAction.cc 77781 2013-11-28 07:54:07Z gcosmo $
//
/// \file PrimaryGeneratorAction.cc
/// \brief Implementation of the PrimaryGeneratorAction class
/*
#include "PrimaryGeneratorAction.hh"

#include "G4Event.hh"
#include "G4ParticleGun.hh"
#include "G4GeneralParticleSource.hh"
#include "G4ParticleTable.hh"
#include "G4ParticleDefinition.hh"
#include "G4GenericMessenger.hh"
#include "G4SystemOfUnits.hh"
#include "Randomize.hh"

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

PrimaryGeneratorAction::PrimaryGeneratorAction()
: G4VUserPrimaryGeneratorAction(),     
  fParticleGun(0), fMessenger(0), 
  fPositron(0), fMuon(0), fPion(0), fKaon(0), fProton(0),fPhoton(0),
  fMomentum(1000.*MeV),
  fSigmaMomentum(50.*MeV),
  fSigmaAngle(5.*deg),
  fRandomizePrimary(false)
{
	generator = new G4GeneralParticleSource();

    G4int n_particle = 1;
    fParticleGun  = new G4ParticleGun(n_particle);
    
    G4ParticleTable* particleTable = G4ParticleTable::GetParticleTable();
    G4String particleName;
    fPositron = particleTable->FindParticle(particleName="e+");
    fMuon = particleTable->FindParticle(particleName="mu+");
    fPion = particleTable->FindParticle(particleName="pi+");
    fKaon = particleTable->FindParticle(particleName="kaon+");
    fProton = particleTable->FindParticle(particleName="proton");
	fPhoton = particleTable->FindParticle(particleName="gamma");
    
    // default particle kinematics
    fParticleGun->SetParticlePosition(G4ThreeVector(0.,0.,-0.5*m));
    fParticleGun->SetParticleDefinition(fPhoton);
    
    // define commands for this class
    DefineCommands();
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

PrimaryGeneratorAction::~PrimaryGeneratorAction()
{
    delete fParticleGun;
    delete fMessenger;
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* event)
{   
	generator -> GeneratePrimaryVertex(event);

    G4double pp = fMomentum + (G4UniformRand()-0.5)*fSigmaMomentum;
    G4double mass =  fParticleGun->GetParticleDefinition()->GetPDGMass();
    G4double Ekin = std::sqrt(pp*pp+mass*mass)-mass;
    fParticleGun->SetParticleEnergy(Ekin);
    
    G4double angle = (G4UniformRand()-0.5)*fSigmaAngle;
    fParticleGun->SetParticleMomentumDirection(G4ThreeVector(std::sin(angle),0.,
                                                             std::cos(angle)));
    
    //fParticleGun->GeneratePrimaryVertex(event);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void PrimaryGeneratorAction::DefineCommands()
{
    // Define //generator command directory using generic messenger class
    fMessenger 
      = new G4GenericMessenger(this, 
                               "/tutorial/generator/", 
                               "Primary generator control");
              
    // momentum command
    G4GenericMessenger::Command& momentumCmd
      = fMessenger->DeclarePropertyWithUnit("momentum", "GeV", fMomentum, 
                                    "Mean momentum of primaries.");
    momentumCmd.SetParameterName("p", true);
    momentumCmd.SetRange("p>=0.");                                
    momentumCmd.SetDefaultValue("1.");
    // ok
    //momentumCmd.SetParameterName("p", true);
    //momentumCmd.SetRange("p>=0.");                                
    
    // sigmaMomentum command
    G4GenericMessenger::Command& sigmaMomentumCmd
      = fMessenger->DeclarePropertyWithUnit("sigmaMomentum",
          "MeV", fSigmaMomentum, "Sigma momentum of primaries.");
    sigmaMomentumCmd.SetParameterName("sp", true);
    sigmaMomentumCmd.SetRange("sp>=0.");                                
    sigmaMomentumCmd.SetDefaultValue("50.");

    // sigmaAngle command
    G4GenericMessenger::Command& sigmaAngleCmd
      = fMessenger->DeclarePropertyWithUnit("sigmaAngle", "rad", fSigmaAngle, 
                                    "Sigma angle divergence of primaries.");
    sigmaAngleCmd.SetParameterName("t", true);
    sigmaAngleCmd.SetRange("t>=0.");                                
    sigmaAngleCmd.SetDefaultValue("2.");
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......
*/
