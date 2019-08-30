import pandas as pd
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, PasswordField, RadioField, BooleanField, SelectField, SubmitField, TextAreaField, Form, TextField, TextAreaField, validators
from flask import Flask, render_template, flash, request
from wtforms.validators import DataRequired, Length
from lib.configurator import CUTE_NAMES


# Holds all fields for an incidence filled in online
class WebForm(FlaskForm):
    """
    The Web Form class establishes the fields necessary in the WebForm to fill an incidence, so to change the form these fields must be changed.
    """
    aviso_calidad = TextField('Aviso de Calidad: ', validators=[DataRequired()])
    codigo_cliente = TextField('Codigo Cliente: ', validators=[DataRequired()])
    material_afectado = TextField('Material Afectado: ', validators=[DataRequired()])
    albaran = TextField('Albaran: ', validators=[DataRequired()])
    textoSAP = TextAreaField('Texto SAP: ', validators=[Length(min=0, max=500), DataRequired()])
    analysis_causa = TextAreaField('Analysis de Causas: ', validators=[Length(min=0, max=500), DataRequired()])
    causa_raiz = TextField('Causa Raiz: ', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Classes for holding Incidence information
class InfoForm:
    """
    This class is used to create an Incidence Form , for when an incidence is checked for its category or changed.
    """
    def __init__(self, fields=[]):
        self.id = 0
        self.fields = fields

    def setID(self, id):
        self.id = id

class InfoField:
    def __init__(self, label, data):
        self.label = label
        self.data = data

class FormBuilder:
    """
    This class allows a form to be created from a dataframe, a premade incidence, or an empty form when no incidence is looked up.
    """
    @staticmethod
    def buildFromEntry(entry_df):
        """
        This methods creates an Information form from a given dataframe, giving it the fields necessary.

        Args:
          entry_df: the dataframe of the incidence to show on the form
        Returns:
          The web form to display with the searched incidence
        """
        # Get columns of dataframe entry
        #cols = entry_df.columns
        labels = CUTE_NAMES

        # Get values of entry, or if empty then return empty form
        if(entry_df.shape[0] == 1):
            vals = list(entry_df.loc[0])
        else:
            return FormBuilder.buildEmptyForm()

        # Make fields
        fields = [InfoField(pair[0], pair[1]) for pair in list(zip(labels,vals))]

        # Return a form object from the constructed fields
        return InfoForm(fields=fields)

    @staticmethod
    def buildEmptyForm():
        """
        This method returns a simple Info form with no filled fields.
        Returns:
            Simple empty information form
        """
        infoForm = InfoForm()
        #infoForm.setID('(nothing to show)')
        return infoForm