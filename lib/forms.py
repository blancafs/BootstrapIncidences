import pandas as pd
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, PasswordField, RadioField, BooleanField, SelectField, SubmitField, TextAreaField, Form, TextField, TextAreaField, validators
from flask import Flask, render_template, flash, request
from wtforms.validators import DataRequired, Length
from lib.configurator import CUTE_NAMES


# Holds all fields for an incidence filled in online
class WebForm(FlaskForm):
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
    @staticmethod
    def buildFromEntry(entry_df):
        # Get columns of dataframe entry
        cols = entry_df.columns
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
        infoForm = InfoForm()
        #infoForm.setID('(nothing to show)')
        return infoForm