#! /usr/bin/env python

#Programa desarrollado por Pablo Sotres para el proyecto Asi se siente mi Barrio 

# Todo esta conectado de la siguiente manera:
## Relays: 2(5V), 38(20) y 40(21) Relays
## RFID: 1(3.3), 6(GND) 19(MOSI),21(MISO),23(SCK), 24(SDA)
## Boton Rei: 7(4), 17(3.3)
## Boton Apa: 11(17), 17(3.3)
## LED: 36(16), 34(GND)
## Sensor: 4(5V), 14(GND), 16(23)

#
import pygame
import RPi.GPIO as GPIO
import SimpleMFRC522
import logging
import glob
import os
import time
import signal
from subprocess import call


#Se inicializa el lector con reader
reader = SimpleMFRC522.SimpleMFRC522()

#Se inicializa el mixer de pygame para correr los audios
pygame.mixer.pre_init(44100,-16,2, 1024) 
pygame.mixer.init()

#Variables para guardar valores
id = ""
ligaV = ""

trueIDN= ''
trueId = ''

contador=0
nhn = 2 

# Valores a modificar
tiempoEspera = 210
tiempoCorte = 6


# Declarar los pines de relevadores y ponerlos en HIGH 
pinList = [21, 20]
GPIO.setmode(GPIO.BCM)
for i in pinList: 
    GPIO.setup(i, GPIO.OUT) 
    GPIO.output(i, GPIO.HIGH)

GPIO.output(20, GPIO.HIGH)
GPIO.output(21, GPIO.LOW)

# Pines de los botones para reiniciar y apagar.
GPIO.setup(17,GPIO.IN,pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(4,GPIO.IN,pull_up_down=GPIO.PUD_DOWN) 

# Led de Funcionamiento 
GPIO.setup(16,GPIO.OUT)
GPIO.output(16,GPIO.HIGH)
#Funcion para correr los audios
def playAudio(audio):
    directorio = "/home/pi/Desktop/rpi-rfid-video-master/"+audio
    pygame.mixer.music.load(directorio)
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(1)

    # while pygame.mixer.music.get_busy() == True:
    #     continue

#Ligas a audios de funcionamiento
audioPrueba = 'audios/introduccion_01.mp3'
apagando = 'audios/apagando.mp3' 
encendido = 'audios/encendido.mp3'
reiniciando = 'audios/reiniciando.mp3'
listo = 'audios/listo.mp3'
adios = 'audios/adios.mp3'

#Variables para botones e inicio
inicio=0
apagar = 0
reiniciar = 0

#####################################################################################
#Comienza el loop 
try:
    while True: 
        #Script que corre al inicio 
        if(inicio ==0):
            playAudio(encendido)
            time.sleep(1)
            # playAudio(audioPrueba)
            # time.sleep(13)
            inicio =1
        

        #Script para apagar con el boton 
        apagado=GPIO.input(17)
        if ( apagado == GPIO.HIGH):
            GPIO.output(20, GPIO.HIGH)
            GPIO.output(21, GPIO.LOW)
            playAudio(apagando)
            time.sleep(1)
            apagar = apagar +1
            print("Apagar presionado: " + str(apagar))
            if ( apagar  > 5):
                print("apagando")
                playAudio(adios)
                time.sleep(1)
                call("sudo poweroff",shell=True)      
        else:
            apagar = 0

        #Script para reiniciar con el boton
        reiniciado = GPIO.input(4)
        if(reiniciado ==GPIO.HIGH):
            GPIO.output(20, GPIO.HIGH)
            GPIO.output(21, GPIO.LOW)
            playAudio(reiniciando)
            time.sleep(1)
            reiniciar = reiniciar+1
            print("Reiniciado presionado: " + str(reiniciar))
            if(reiniciar>5):
                print('reiniciando')
                playAudio(listo)
                time.sleep(1)
                call("sudo reboot",shell=True)
        else:
            reiniciar = 0        
            
        #Se lee tarjeta
        idL, ligaL = reader.read_no_block()
        
        #Si el id es vacio colocar lectura
        if id == "":
			id = idL
            
        if ligaL == "":
        	ligaV = ligaL

        #Si el id nuevo es None y ID es none entonces no hay nada 
        if idL is None and id is None:     
            nhn +=1
            if nhn == tiempoCorte:
                pygame.mixer.music.pause()
                pygame.mixer.stop()
                trueId=''
                trueIDN=''

        elif ligaL is None and ligaV is None:
            print('Hay un error')
            trueLiga = ''
            ligaV = ''

        #Coloca en variable el valor de cualquiera de los dos. 
        else:
            trueId = id or idL
            trueliga = ligaV or ligaL
            id = idL

        #Darle tiempo al lector
        time.sleep(1)

        #Si los ID son iguales es el mismo y no cambia entonces regresa si
        #Si llega al tiempo de espera, reproduce un audio. 
        if trueId == trueIDN:
            # print('Es el mismo')
            contador +=1
            print(contador)
            if contador%tiempoEspera == 0:
                contador =0
                GPIO.output(20, GPIO.HIGH)
                GPIO.output(21, GPIO.LOW)
                playAudio(audioPrueba)

            continue    

        # Imprime la informacion del lector
        print("ID: %s" % id)
        print("Liga Audio: %s" % ligaL)
        print("Coloca Nueva tarjeta")

        #Reproduce Audio y resetea nhn y contador
        if trueIDN != trueId:
            nhn = 2
            contador =0
            print('Nuevo Audio')
            if(ligaL is None):
                print("is nonetype")
                pygame.mixer.music.pause()
                pygame.mixer.stop()
                trueId=''
                trueIDN=''
                continue

            if(ligaL.startswith("audios") ):
                ligaL = ligaL.strip()
                GPIO.output(20, GPIO.LOW)
                GPIO.output(21, GPIO.HIGH)
                playAudio(ligaL)
                print('corrio audio')
                trueIDN = trueId
            
            else:
                continue
            

except KeyboardInterrupt:
	GPIO.cleanup()
	print("\nAll Done")