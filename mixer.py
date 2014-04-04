import pygame
import time
from random import randrange

pygame.init()
pygame.mixer.init()

#Load audio files into Sound objects
fear_track = pygame.mixer.Sound('Fear.wav')
sadness_track = pygame.mixer.Sound('Sadness.wav')
joviality_track = pygame.mixer.Sound('Joviality.wav')
fatigue_track = pygame.mixer.Sound('Fatigue.wav')
hostility_track = pygame.mixer.Sound('Hostility.wav')
serenity_track = pygame.mixer.Sound('Serenity.wav')
guilty_track = pygame.mixer.Sound('Guilty.wav')
positivity_track = pygame.mixer.Sound('Positivity.wav')

#Play Sound objects in infinite loop
fear_track.play(-1)
sadness_track.play(-1)
joviality_track.play(-1)
fatigue_track.play(-1)
hostility_track.play(-1)
serenity_track.play(-1)
guilty_track.play(-1)
positivity_track.play(-1)

#Set all tracks to volume 0
fear_track.set_volume(0.0)
sadness_track.set_volume(0.0)
joviality_track.set_volume(0.0)
fatigue_track.set_volume(0.0)
hostility_track.set_volume(0.0)
serenity_track.set_volume(0.0)
guilty_track.set_volume(0.0)
positivity_track.set_volume(0.0)

#pre-define a variable for random numbers
irand = 0.0

# function to return a random number between 0.0 - 1.0
def Randomizer(irand):
    irand = randrange(0,10)
    #print "generated random:"
    #print irand
    irand = irand * .1
    return irand;

# Main control loop: delay of 16 seconds

while True:
# Each track 

############  Fear Track ########
    
    if Randomizer(irand) > .6:
        volume_set = Randomizer(irand)
        fear_track.set_volume(volume_set) 
        print("Fear Track Volume Set to:")
        print(volume_set)
    else:
        fear_track.set_volume(0.0)
        print("----- Fear Track disabled")

########### Sadness   ##### 
    
    if Randomizer(irand) > .6:
        volume_set = Randomizer(irand)
        sadness_track.set_volume(volume_set)
        print("Sadness Track Volume Set to:")
        print(volume_set)
    else:
        sadness_track.set_volume(0.0)
        print("----- Sadness Track disabled")

########### joviality  ##### 
    
    if Randomizer(irand) > .6:
        volume_set = Randomizer(irand)
        joviality_track.set_volume(volume_set)
        print("Joviality Track Volume Set to:")
        print(volume_set)
    else:
        joviality_track.set_volume(0.0)
        print("----- Joviality Track disabled")


########### Fatigue  ##### 
    
    if Randomizer(irand) > .6:
        volume_set = Randomizer(irand)
        fatigue_track.set_volume(volume_set)
        print("Fatigue Track Volume Set to:")
        print(volume_set)
    else:
        fatigue_track.set_volume(0.0)
        print("----- Fatigue Track disabled")


########### Hostility  ##### 
    
    if Randomizer(irand) > .6:
        volume_set = Randomizer(irand)
        hostility_track.set_volume(volume_set)
        print("Hostility Track Volume Set to:")
        print(volume_set)
    else:
        hostility_track.set_volume(0.0)
        print("----- Hostility Track disabled")
        
########### Serenity  ##### 
    
    if Randomizer(irand) > .6:
        volume_set = Randomizer(irand)
        serenity_track.set_volume(volume_set)
        print("Serenity Track Volume Set to:")
        print(volume_set)
    else:
        serenity_track.set_volume(0.0)
        print("----- Serenity Track disabled")
       
########### Guilty  ##### 
    
    if Randomizer(irand) > .6:
        volume_set = Randomizer(irand)
        guilty_track.set_volume(volume_set)
        print("Guilty Track Volume Set to:")
        print(volume_set)
    else:
        guilty_track.set_volume(0.0)
        print("----- Guilty Track disabled")

########### Positivity  ##### 
    
    if Randomizer(irand) > .6:
        volume_set = Randomizer(irand)
        positivity_track.set_volume(volume_set)
        print("Positivity Track Volume Set to:")
        print(volume_set)
    else:
        positivity_track.set_volume(0.0)
        print("----- Positivity Track disabled")
    
    time.sleep(16)


