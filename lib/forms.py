from flask_wtf import FlaskForm
from wtforms import StringField, DateField, PasswordField, RadioField, BooleanField, SelectField, SubmitField, TextAreaField, Form, TextField, TextAreaField, validators
from flask import Flask, render_template, flash, request
from wtforms.validators import DataRequired, Length


# Holds all fields for an incidence filled in online
class WebForm(FlaskForm):
    aviso_calidad = TextField('Aviso de Calidad: ', validators=[DataRequired()])
    codigo_cliente = TextField('Codigo Cliente: ', validators=[DataRequired()])
    fecha_registro = DateField('Fecha Registro: ', validators=[DataRequired()], format='%d/%m/%Y')
    material_afectado = TextField('Material Afectado: ', validators=[DataRequired()])
    fecha_salida = DateField('Fecha Salida: ', format='%d/%m/%Y', validators=[DataRequired()])
    albaran = TextField('Albaran: ', validators=[DataRequired()])
    textoSAP = TextAreaField('Texto SAP: ', validators=[Length(min=0, max=500), DataRequired()])
    analysis_causa = TextAreaField('Analysis de Causas: ', validators=[Length(min=0, max=500), DataRequired()])
    causa_raiz = TextField('Causa Raiz: ', validators=[DataRequired()])
    fecha_finalizacion_investigacion = DateField('Fecha Finalizacion: ', validators=[DataRequired()], format='%d/%m/%Y')
    submit = SubmitField('Submit')
