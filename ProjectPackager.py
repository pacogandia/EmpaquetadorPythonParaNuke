#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PROJECT PACKAGER 1.0    By Disposable Apps

http://disposableapps.com

===

Description:

This script creates a copy of the files used in the project,
while keeping the folder structure.

It prompts for a source folder and a destination folder,
runs through every node in the open nuke file,
and creates the necessary folders
to build a copy with every file the project uses.

Restrictions:

- The destination folder cannot be a subfolder of the source folder

- If a file is located outside the source folder,
the code copies it in a folder called COMPLEMENTOS (the spanish word for Accesories)

===

Installation Notes:

1. Copy "ProjectPackager.py” to your nuke plugins directory
2. Open "Init.py" located on your nuke plugins directory
3. Paste:
import ProjectPackager
nuke.menu( "Nuke" ).addCommand("Edit/ProjectPackager", "ProjectPackager.clone_project()" )
4. Restart Nuke
5. Under the Edit menu you will find the option “ProjectPackager”

===

Run:
clone_project()

===

Last Updated: March 22, 2017.
All Rights Reserved .

"""


import os
import shutil
import nuke
import re


def clone_project():
    # Paso 1 - averiguamos carpeta origen y carpeta destino
    # Averiguamos el filepath (FP) del archivo nuke abierto y ofrecemos carpetas superiores como origen de la copia
    elFP_nk_abierto = nuke.Root().name()
    #si no hay path porque no hay ningun nk abierto, alertamos y abandonamos
    if elFP_nk_abierto == 'Root':
        nuke.message('No nuke file is active')
        return None  # salimos de la funcion muestroPanelActualizarRead

    # construyo las opciones para el listado para Pulldown
    # primero formo la lista de strings
    elFPtuneado = elFP_nk_abierto
    opciones_delFP_nk_abierto = []
    while (elFPtuneado.rfind("/") > 0):
        elFPtuneado = elFPtuneado[:(elFPtuneado.rfind("/"))]
        opciones_delFP_nk_abierto.append(elFPtuneado)
    # luego la adapto para su listado para Pulldown
    opciones_delFP_nk_abierto_Pull = " ".join(opciones_delFP_nk_abierto)


    ## Construimos un panel-interfaz para que el usuario elija dos cosas:
    # 1) la carpeta a partir de la cual empezar la copia
    # 2) la carpeta destino de la copia
    p = nuke.Panel('Project Packager (by DisposableApps)')
    p.addEnumerationPulldown('Choose the source folder', opciones_delFP_nk_abierto_Pull)
    p.addFilenameSearch("Choose the destination folder", elFP_nk_abierto)
    # multilineTextInput = "ATENCIÓN - Al pulsar OK, también se guardará el actual script de nuke y después se clonará en la carpeta de destino"
    # p.addMultilineTextInput("Multiline Text Input:", multilineTextInput)
    p.addButton("Cancel")
    p.addButton("OK")
    # Abrimos el panel:
    result = p.show()

    # -- lo que sigue se ejecuta despues de pulsar OK

    # guardamos el nuke actual
    lo_he_grabado = 0
    lo_he_grabado = nuke.scriptSave()
    # print ("lo he GRABADO?", lo_he_grabado)
    if not lo_he_grabado:
        nuke.message('The current nuke file could not be saved')
        return None  # salimos de la funcion muestroPanelActualizarRead



    carpeta_origen_copia = p.value("Choose the source folder")
    carpeta_destino_pull = p.value("Choose the destination folder")

    #si el destino está dentro de la carpeta que vamos a clonar, alertamos y abandonamos
    if carpeta_destino_pull.find(carpeta_origen_copia) > -1:
        nuke.message('The destination folder cannot be a Source subfolder')
        return None  # salimos de la funcion muestroPanelActualizarRead


    carpeta_destino_base = carpeta_destino_pull + carpeta_origen_copia[(carpeta_origen_copia.rfind("/")+1):]
    #el "+1" es para evitar parejas "//"
    #print ("la copia se realiza desde %s  -- y va a parar a %s") % (carpeta_origen_copia, carpeta_destino_base)

    # Fin Fase 1

    # Fase 2 - Recopilamos los archivos a clonar
    # Repasamos todos los nodos (incluye Read, ReadGeo, ReadGeo2, Axis2, Camera2,...)
    try:
        Todos_los_Nodos = nuke.allNodes(recurseGroups=True)
    except:
        Todos_los_Nodos = nuke.allNodes()
    #print (Todos_los_Nodos)

    direcciones_completas_de_los_archivos=[]   # antes tmpDir
    nombres_de_los_nodos=[]                    # antes rs
    nombres_de_los_archivos=[]                 # antes tmpF
    nueva_carpeta_de_los_archivos=[]           # antes nuevaubicacion
    ya_no_existen_y_lo_alerto=[]

    for nodo in Todos_los_Nodos:
        if nodo.knob('file'):   #si existe el campo file
            if not "Write" in nodo.Class():  #si NO es un nodo Write
                if len(nodo.knob('file').value())>2 :     #a veces aparece un nodo Viewer con un file de 0 caracteres. Lo evito aqui.


                    ##if re.search('\%\d+d|D', nodo.knob('file').value()):     #es secuencia
                    if re.match('.*\.%0.*', nodo.knob('file').value()):  #es secuencia
                        elfile= nodo.knob('file').value()
                        finalcadena = elfile[elfile.rfind("%") + 1:]
                        paddenstring = finalcadena[:finalcadena.find("d")]
                        padd = int(paddenstring)
                        #print ("ES SECUENCIA EL NODO",  nodo, " con files" , elfile)

                        nombreprenumeros= elfile[:elfile.rfind("%")]
                        raizpostnumeros= finalcadena[finalcadena.find("d")+1:]

                        # Obtenemos el rango para copiar
                        try:
                            firstF = int(nodo.knob('first').getValue())
                            lastF = int(nodo.knob('last').getValue())
                        except:
                                firstF = int(nodo.knob('range_first').getValue())
                                lastF = int(nodo.knob('range_last').getValue())


                        #print (firstF, lastF)

                        for numsec in range(firstF, lastF):
                            numconceros= str(numsec).zfill(padd)  ##le añadimos tantos zeros como manda padd
                            nomfile= nombreprenumeros+numconceros+raizpostnumeros
                            #print nomfile
                            direcciones_completas_de_los_archivos.append(nomfile)
                            nombres_de_los_nodos.append(nodo.knob('name').value())


                    else:   #no es secuencia
                        direcciones_completas_de_los_archivos.append(nodo.knob('file').value())
                        # print (nodo.knob('name').value, " es ", nodo.Class() )
                        nombres_de_los_nodos.append(nodo.knob('name').value())


    # Fin Fase 2

    # Fase 3 - Generamos los paths de destino: si no existe la carpeta la fabricamos


    # mostramos una barra de progreso-- basado en NathanR1 - http://community.foundry.com/discuss/topic/102895
    task = nuke.ProgressTask('Copying files...')
    progIncr = 100.0 / len(direcciones_completas_de_los_archivos)

    for indice, direccion_completa_original in enumerate(direcciones_completas_de_los_archivos, start=0):

        la_carpeta_del_archivo = os.path.dirname(direccion_completa_original)
        la_carpeta_con_barra = la_carpeta_del_archivo + '/'
        longitud_carpeta = len(la_carpeta_del_archivo) + 1
        nombre_del_archivo = direccion_completa_original[longitud_carpeta:]
        nombres_de_los_archivos.append(nombre_del_archivo)

        # chequeo sobre cada fuente si está dentro o fuera de mi arbol de clonacion
        if la_carpeta_con_barra.find(carpeta_origen_copia) == -1:
            # No esta en mi arbol de clonacion: lo clono en la carpeta generica COMPLEMENTOS
            #print("ESTA EN OTRO SITIO", direccion_completa_original)
            dondelameto = carpeta_destino_base + "/COMPLEMENTOS/"
        else:
            # parámetros -> re.sub('substring_que_busco', 'substring_que_la_reemplaza', la_string)
            dondelameto = re.sub(carpeta_origen_copia, carpeta_destino_base, la_carpeta_con_barra)

        nueva_carpeta_de_los_archivos.append(dondelameto)

        if not os.path.isdir(dondelameto):
            #print("la carpeta %s no existe, voy a  crearla") % (dondelameto)
            os.makedirs(dondelameto)

        #print("VOY A COPIAR el archivo %s en %s") % (direccion_completa_original, dondelameto + nombre_del_archivo)


        # gestionamos la barra de progreso
        if task.isCancelled():
            nuke.message("File copy was canceled!")
            return

        task.setProgress(int(indice * progIncr))
        task.setMessage(direccion_completa_original)


        if (os.path.exists(direccion_completa_original)):   # si tengo acceso al archivo LO COPIO
            #print ("/n", "EXISTE ", direccion_completa_original)
            shutil.copy(direccion_completa_original, dondelameto + nombre_del_archivo)
        else:
            # si el archivo fuente ya no está en ese sitio LO ALMACENO PARA ALERTAR
            #print("\n"+"\n"+"no tengo acceso a %s") % (direccion_completa_original)
            ya_no_existen_y_lo_alerto.append(indice)



    # cerramos la barra de progreso borrando la variable asociada
    del task

    # Fin Fase 3


    # Fase 4 : clono el nuke en el que estoy trabajando (lo he salvado previamente)
    nukeactual = elFP_nk_abierto
    nukedestino = re.sub (carpeta_origen_copia, carpeta_destino_base, nukeactual)
    carpetanukedestino= nukedestino[:(nukedestino.rfind("/"))]
    if not os.path.isdir(carpetanukedestino):
        #print("la carpeta %s no existe, voy a  crearla") % (carpetanukedestino)
        os.makedirs(carpetanukedestino)

    #print("VOY A COPIAR el NUKE %s en SU NUEVA UBICACION %s") % (nukeactual, nukedestino)
    #print("la carpeta nuke destino es %s") % (carpetanukedestino)
    shutil.copy(nukeactual, nukedestino)

    # Fin Fase 4




    # Fase 5 : Si después de repasar los nodos hay archivos faltantes, los alerto:
    mensaje=""

    #la parte de los archivos no encontrados
    if len(ya_no_existen_y_lo_alerto)>0:
        plural=""
        if len(ya_no_existen_y_lo_alerto)>1: plural="S"
        mensaje= mensaje+"WE COULD NOT FIND "+ str(len(ya_no_existen_y_lo_alerto)) + " FILE" +plural+ ":" + "\n"
        for numfaltante in ya_no_existen_y_lo_alerto:
            archivo_faltante = direcciones_completas_de_los_archivos[numfaltante]
            nodo_conflictivo = nombres_de_los_nodos[numfaltante]
            mensaje=mensaje +"-- " + archivo_faltante+" (in node "+  nodo_conflictivo +")\n"

    # la parte de los gizmos no encontrados
    gizmos_para_alertar=[]
    for nodo in Todos_los_Nodos:
        if 'gizmo_file' in nodo.knobs():
            gizmos_para_alertar.append(nodo.knob('name').value())

    if len (gizmos_para_alertar)>0:
        alosplural=""
        if len(gizmos_para_alertar) > 1: alosplural="S"
        mensaje = mensaje + "\n" + "\n" + "WE COULD NOT CLONE THE GIZMOS ASSIGNED TO THE NODE"+alosplural +":"+ "\n"
        coma=""
        for nodogizmo in gizmos_para_alertar:
            mensaje = mensaje + coma+ nodogizmo
            coma=", "

    if mensaje == "":
        mensaje="Ready!"

    nuke.message(mensaje)
    # print mensaje
    # Fin Fase 5

#clone_project()




