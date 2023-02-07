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


class ProximiteAlgorithm(QgsProcessingAlgorithm):
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

    OUTPUT = 'OUTPUT'  # couche en sortie
    SOURCE = 'SOURCE'  # couche qui sera intersectée:
    SUPERPOSITION = 'SUPERPOSITION' # couche qui servira à créer le buffer 
    #BUFFER_OUTPUT = 'BUFFER_OUTPUT' # stockage du buffer

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ProximiteAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'proximite'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Objets à proximité')

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
        return self.tr("Trouve les objets d'une couche situé à un certain rayon des objets d'une autre couche.")
    
    def initAlgorithm(self, config=None):
        """
        Initialisation de l'algorithme: définition des
        paramètres en entrée et en sortie
        """

        # Données source
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.SOURCE,
                self.tr('Couche d\'intérêt'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        
        # Données superposées
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.SUPERPOSITION,
                self.tr('Couche sur laquelle sera faite le tampon'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
            
        # Distance du tampon
        self.addParameter(
            QgsProcessingParameterDistance(
                'BUFFERDIST',
                self.tr('Distance du tampon'),
                defaultValue = 1000.0,
                # Make distance units match the INPUT layer units:
                parentParameterName='SUPERPOSITION'
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
        source = self.parameterAsSource(parameters, self.SOURCE, context)
        superposition = self.parameterAsSource(parameters, self.SUPERPOSITION, context)
        outputFile = self.parameterAsOutputLayer(parameters,self.OUTPUT, context)
        bufferdist = self.parameterAsDouble(parameters, 'BUFFERDIST', context)

        # Vérification qu'il y a bien deux couches en entrée
        # des erreurs sont levées si une couche est manquante
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SOURCE))
        if superposition is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SUPERPOSITION))

        # Il est possible d'afficher des informations
        # à destination de l'utilisateur
        feedback.pushInfo('Source CRS is {}'.format(source.sourceCrs().authid()))
        feedback.pushInfo('Superposition CRS is {}'.format(superposition.sourceCrs().authid()))

        # Vérification que les couches ont un SRC compatibles
        if source.sourceCrs().authid() != superposition.sourceCrs().authid():
            # Si SRC différents, QGIS lève une exception et arrête l'algorithme.
            raise QgsProcessingException(
                    self.tr('les couches doivent être dans le même système de référence de coordonnées.')
                    )
                    
        # Calcul du tampon            
        tampon = processing.run(
            "native:buffer",{
                'INPUT': parameters['SUPERPOSITION'],
                'DISTANCE' : bufferdist,
                'SEGMENTS' :5,
                'END CAP STYLE' : 0,
                'JOIN STYLE': 0,
                'MITER LIMIT' :2,
                'DISSOLVE' : False,
                'OUTPUT' : 'TEMPORARY_OUTPUT'
                },
            context=context,
            feedback=feedback)
            
        ## Intersection du tampon et de la couche source
        intersection = processing.run(
                "native:intersection", 
                {'INPUT': parameters['SOURCE'],
                'OVERLAY': tampon['OUTPUT'],
                'INPUT_FIELDS':[],
                'OVERLAY_FIELDS':[],
                'OUTPUT':outputFile})['OUTPUT']

        # Return the results of the algorithm. In this case our only result is
        # the intersection.
        return {self.OUTPUT: intersection}
