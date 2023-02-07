# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterDistance,
                       QgsProcessingParameterVectorDestination)
from qgis import processing


class LieuxPropicesAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    
    gare = 'gare'        # couche qui servira à créer le buffer 
    espaceV = 'espaceV'  # couche qui servira à créer le buffer 
    metro = 'metro'      # couche qui servira à créer le buffer 
    piscine = 'piscine'  # couche qui servira à créer le buffer 
    
    
    

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return LieuxPropicesAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'lieux_propices'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Lieux Propices')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Scripts PyQGIS')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'scriptspyqgis'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Trouve les zones situés en même temps à des distances définis des gares, espaces verts, métros et piscines.")
        

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # GARES SNCF
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.gare,
                self.tr('Couche des gares SNCF'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )        
        # Distance du tampon
        self.addParameter(
            QgsProcessingParameterDistance(
                'BUFFERDIST_gare',
                self.tr('Distance du tampon pour les gares SNCF'),
                defaultValue = 1000.0,
                # Make distance units match the INPUT layer units:
                parentParameterName='gare'
            )
        )
        
        # ESPACES VERTS
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.espaceV,
                self.tr('Couche des espaces verts'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        # Distance du tampon
        self.addParameter(
            QgsProcessingParameterDistance(
                'BUFFERDIST_espaceV',
                self.tr('Distance du tampon pour les espaces verts'),
                defaultValue = 200.0,
                # Make distance units match the INPUT layer units:
                parentParameterName='espaceV'
            )
        )
        
        # METROS
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.metro,
                self.tr('Couche des entrées et sorties de métro'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        # Distance du tampon
        self.addParameter(
            QgsProcessingParameterDistance(
                'BUFFERDIST_metro',
                self.tr('Distance du tampon pour les métros'),
                defaultValue = 300.0,
                # Make distance units match the INPUT layer units:
                parentParameterName='metro'
            )
        )
        
        # PISCINES
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.piscine,
                self.tr('Couche des piscines'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        # Distance du tampon
        self.addParameter(
            QgsProcessingParameterDistance(
                'BUFFERDIST_piscine',
                self.tr('Distance du tampon pour les piscines'),
                defaultValue = 500.0,
                # Make distance units match the INPUT layer units:
                parentParameterName='piscine'
            )
        )


        # Récupération de la destination.
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT,
                self.tr('Sortie')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # récupération des valeurs des paramètres
        gare = self.parameterAsSource(parameters, self.gare, context)
        espaceV = self.parameterAsSource(parameters, self.espaceV, context)
        metro = self.parameterAsSource(parameters, self.metro, context)
        piscine = self.parameterAsSource(parameters, self.piscine, context)
        
        bufferdist_gare = self.parameterAsDouble(parameters, 'BUFFERDIST_gare', context)
        bufferdist_espaceV = self.parameterAsDouble(parameters, 'BUFFERDIST_espaceV', context)
        bufferdist_metro = self.parameterAsDouble(parameters, 'BUFFERDIST_metro', context)
        bufferdist_piscine = self.parameterAsDouble(parameters, 'BUFFERDIST_piscine', context)
    
    
        outputFile = self.parameterAsOutputLayer(parameters,self.OUTPUT, context)
        

        # Vérification qu'il y a bien deux couches en entrée
        # des erreurs sont levées si une couche est manquante
        if gare is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.gare))
        if espaceV is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.espaceV))
        if metro is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.metro))
        if piscine is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.piscine))

        
        
        # Il est possible d'afficher des informations
        # à destination de l'utilisateur
        feedback.pushInfo('Gare CRS is {}'.format(gare.sourceCrs().authid()))
        feedback.pushInfo('espaceV CRS is {}'.format(espaceV.sourceCrs().authid()))
        feedback.pushInfo('metro CRS is {}'.format(metro.sourceCrs().authid()))
        feedback.pushInfo('piscine CRS is {}'.format(piscine.sourceCrs().authid()))

        # Calcul du tampon gare
        tampon_gare = processing.run(
            "native:buffer",{
                'INPUT': parameters['gare'],
                'DISTANCE' : bufferdist_gare,
                'SEGMENTS' :5,
                'END CAP STYLE' : 0,
                'JOIN STYLE': 0,
                'MITER LIMIT' :2,
                'DISSOLVE' : True,
                'OUTPUT' : 'TEMPORARY_OUTPUT'
                },
            context=context,
            feedback=feedback)['OUTPUT']
            
        # Calcul du tampon espaceV
        tampon_espaceV = processing.run(
            "native:buffer",{
                'INPUT': parameters['espaceV'],
                'DISTANCE' : bufferdist_espaceV,
                'SEGMENTS' :5,
                'END CAP STYLE' : 0,
                'JOIN STYLE': 0,
                'MITER LIMIT' :2,
                'DISSOLVE' : True,
                'OUTPUT' : 'TEMPORARY_OUTPUT'
                },
            context=context,
            feedback=feedback)['OUTPUT']
            
        # Calcul du tampon metro
        tampon_metro = processing.run(
            "native:buffer",{
                'INPUT': parameters['metro'],
                'DISTANCE' : bufferdist_metro,
                'SEGMENTS' :5,
                'END CAP STYLE' : 0,
                'JOIN STYLE': 0,
                'MITER LIMIT' :2,
                'DISSOLVE' : True,
                'OUTPUT' : 'TEMPORARY_OUTPUT'
                },
            context=context,
            feedback=feedback)['OUTPUT']
            
        # Calcul du tampon piscine
        tampon_piscine = processing.run(
            "native:buffer",{
                'INPUT': parameters['piscine'],
                'DISTANCE' : bufferdist_piscine,
                'SEGMENTS' :5,
                'END CAP STYLE' : 0,
                'JOIN STYLE': 0,
                'MITER LIMIT' :2,
                'DISSOLVE' : True,
                'OUTPUT' : 'TEMPORARY_OUTPUT'
                },
            context=context,
            feedback=feedback)['OUTPUT']
            
        ## Intersection du tampon gare et tampon espace vert 
        intersection_1 = processing.run(
                "native:intersection", 
                {'INPUT': tampon_gare,
                'OVERLAY': tampon_espaceV,
                'INPUT_FIELDS':[],
                'OVERLAY_FIELDS':[],
                'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
                
        ## Intersection du tampon gare et tampon espace vert 
        intersection_2 = processing.run(
                "native:intersection", 
                {'INPUT': tampon_metro,
                'OVERLAY': tampon_piscine,
                'INPUT_FIELDS':[],
                'OVERLAY_FIELDS':[],
                'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
                
        ## Intersection finale 
        intersection_finale = processing.run(
                "native:intersection", 
                {'INPUT': intersection_1,
                'OVERLAY': intersection_2,
                'INPUT_FIELDS':[],
                'OVERLAY_FIELDS':[],
                'OUTPUT':outputFile})['OUTPUT']

        # Return the results of the algorithm. In this case our only result is
        # the intersection.
        return {self.OUTPUT: intersection_finale}
