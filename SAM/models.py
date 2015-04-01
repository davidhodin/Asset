#-*- coding: utf-8 -*-
from django.db import models
from django import forms
from django.forms import ModelForm

######################################
# ADMINISTRATION
######################################

# Classe comprenant l'ensemble des zones
class SAM_Zone(models.Model):
	zone_Name = models.CharField(max_length=5, unique = True)
	zone_Nbre_Pays = models.BigIntegerField(default=0)
	def __unicode__(self):
		return self.zone_Name

### Form pour la gestion des zones
class SAM_ZoneForm(ModelForm):
	class Meta:
		model = SAM_Zone
		exclude = ('zone_Nbre_Pays',)
		
# Classe contenant la liste des pays d'une zone
class SAM_Country(models.Model):
	country_Code = models.CharField(max_length=3, unique = True)
	country_Name = models.CharField(max_length=30)
	zone = models.ForeignKey(SAM_Zone)
	country_Nbre_Countries_Imported = models.BigIntegerField(default=0)
	def __unicode__(self):
		return self.country_Code + ' - ' + self.country_Name

### Form pour la gestion des pays
class SAM_CountryForm(ModelForm):
	class Meta:
		model = SAM_Country
		exclude = ('country_Nbre_Countries_Imported', 'zone',)

# Pays a ajouter
class SAM_Countries_To_Import(models.Model):
	country_Imported = models.CharField(max_length=10)
	associated = models.BooleanField(default=False)
	def __unicode__(self):
		return self.country_Imported + ' === Associated ? > ' + str(self.associated)
		
# Pays importes
class SAM_Countries_Imported(models.Model):
	country_Imported = models.ForeignKey(SAM_Countries_To_Import, unique = True)
	country_Code = models.ForeignKey(SAM_Country)
	def __unicode__(self):
		return self.country_Imported.country_Imported + ' - linked to ' + self.country_Code.country_Code
		
### Form pour la gestion des pays
class SAM_Countries_ImportedForm(ModelForm):
	class Meta:
		model = SAM_Countries_Imported
		exclude = ('country_Code',)

######################################
# Form Only
######################################

### Form pour l'import de fichier
class ImportSoftwareInstall(forms.Form):
	file = forms.FileField()
	month = forms.ChoiceField(choices=(('01','January'),('02','February'),('03','March'),('04','April'),('05','May'),('06','June'),('07','July'),('08','August'),('09','September'),('10','October'),('11','November'),('12','December')))
	year = forms.ChoiceField(choices=(('2013','2013'),('2014','2014'),('2015','2015'),('2016','2016'),('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020')), initial = '2014')
	domain = forms.ChoiceField( choices = (('ISIS XP', 'ISIS XP'), ('Go 7', 'Go 7')))
	
### Form pour la recherche dans les analyses
class AnalyseSearch(forms.Form):
	month = forms.ChoiceField(choices=(('01','January'),('02','February'),('03','March'),('04','April'),('05','May'),('06','June'),('07','July'),('08','August'),('09','September'),('10','October'),('11','November'),('12','December')))
	year = forms.ChoiceField(choices=(('2013','2013'),('2014','2014'),('2015','2015'),('2016','2016'),('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020')), initial = '2014')

### Formulaire de connexion
class ConnexionForm(forms.Form):
	username = forms.CharField(label="User Name", max_length=30)
	password = forms.CharField(label="Password", widget=forms.PasswordInput)
	
######################################
# SAM Data Software
######################################

# Identifiant de l'importation
class SAM_IMPORT(models.Model):
	import_Date = models.CharField(max_length=7)
	domain = models.CharField(max_length=7)
	date_Saved = models.DateField(auto_now_add=True)
	def __unicode__(self):
		return 'Import of datas < ' + self.import_Date + ' - ' + self.domain + ' > done the ' + str(self.date_Saved)

# Importation du fichier 3.2 avant traitement --- Pas de saisie possible --- Uniquement import et automatismes
class SAM_PC_Imported(models.Model):
	product_Imported = models.CharField(max_length=210)
	department = models.CharField(max_length=10, blank = True)
	instances = models.BigIntegerField(default = 0)
	import_Date = models.CharField(max_length=7, blank = True)
	zone_Name = models.CharField(max_length=3, blank = True)
	group_Done = models.BooleanField(default = False)
	domain = models.CharField(max_length=7)
	SAM_Import = models.ForeignKey(SAM_IMPORT)
	def __unicode__(self):
		return '[' + self.import_Date + '] ' + self.zone_Name + ' => ' + self.product_Imported

# Master Software
class SAM_Master(models.Model):
    # Description du produit suivi
    DOMAIN_TYPE = (
        ('PC', 'Personal Computer'),
        ('Server', 'Server'),
        ('Other', 'Other'),
    )
    # Champs
    supplier_and_product = models.CharField(max_length=200, unique = True)
    domain = models.CharField(max_length=6, choices=DOMAIN_TYPE, default = 'PC')
    def __unicode__(self):
		return self.supplier_and_product + ' - ' + self.domain

class SAM_MasterForm(ModelForm):
	class Meta:
		model = SAM_Master

# Software importes et geres --- Represente les softwares qui existent suite a un import
class SAM_Product_To_Import(models.Model):
	PRODUCT_TYPE = (
        ('Not defined', 'To be defined'),
        ('Not analysed', 'Not analysed'),
        ('Patch', 'Patch'),
        ('Forbidden', 'Forbidden'),
        ('Free', 'Free'),
        ('Licenced', 'Licenced'),
    )	
	product_Imported = models.CharField(max_length=210, unique = True)
	product_Type = models.CharField(max_length=12, choices=PRODUCT_TYPE, default = 'Not defined')
	master_Software = models.ForeignKey(SAM_Master, null = True)
	def __unicode__(self):
		return self.product_Imported + ' >>> ' + self.product_Type

### Form pour les Software importes et geres
class SAM_Product_To_ImportForm(ModelForm):
	class Meta:
		model = SAM_Product_To_Import
		exclude = ('product_Imported','master_Software',)

#  Analyse par produits geres - Issue des donnees de SAM_PC_Import soit le traitement du fichier 3.2
class SAM_PC_Analysed(models.Model):
	managed = models.ForeignKey(SAM_Product_To_Import)
	zone = models.ForeignKey(SAM_Zone, null = True)
	instances = models.BigIntegerField(default = 0)
	import_Date = models.CharField(max_length=7)
	domain = models.CharField(max_length=7)
	def __unicode__(self):
		return self.managed.product_Imported + ' >>> Number of instances = ' + str(self.instances)  + ' >>> Zone = ' + self.zone.zone_Name + ' >>> Imports of ' + self.import_Date + ' >>> Domain = ' + self.domain

# Fiche Software de suivi
class SAM_Item(models.Model):
	GLOBAL_RISK = (
		(0, 'No Risk'),        
		(1, 'No Risk'),
		(2, 'Low Risk'),
		(3, 'Medium Risk'),
		(4, 'High Risk'),
		(5, 'Very High Risk'),
		(6, 'Very High Risk'),
		(7, 'Very High Risk'),
		(8, 'Very High Risk'),
		(9, 'Very High Risk'),
		(10, 'Very High Risk'),        
    )
	master_Software = models.ForeignKey(SAM_Master)
	zone = models.ForeignKey(SAM_Zone)
	comments = models.TextField(blank = True)
	contract_Manager = models.CharField(max_length=200, blank = True)
	actual_Risk = models.BigIntegerField(choices=GLOBAL_RISK, default = 10)
	class Meta:
		unique_together = ('master_Software', 'zone')
	def __unicode__(self):
		return str(self.master_Software) + ' >>> ' + str(self.zone)

# Formlaire de Saisie d'un nouveau software gere
class SAM_ItemForm(ModelForm):
	class Meta:
		model = SAM_Item
		exclude = ('actual_Risk',)

# Historique des analyses de risque
class SAM_Risk(models.Model):
	MONTH_ANALYSE = (
		('01','January'),
		('02','February'),
		('03','March'),
		('04','April'),
		('05','May'),
		('06','June'),
		('07','July'),
		('08','August'),
		('09','September'),
		('10','October'),
		('11','November'),
		('12','December'),
	)
	YEAR_ANALYSE = (
		('2013','2013'),
		('2014','2014'),
		('2015','2015'),
		('2016','2016'),
		('2017','2017'),
		('2018','2018'),
		('2019','2019'),
		('2020','2020')
	)
	LEGAL_DATA = (
        (0, 'License analyse or usage do not implie Personal user information'),
        (0, 'Licence analyse or usage implie Personal user information and action are defined to put this on control'),
        (1, 'Licence analyse or usage implie Personal user information and not all is under control'),
        (2, 'Licence analyse or usage implie Personal user information and nothing is under control'),
    )
	LEGAL_LICENCE = (
        (0, 'The licenses terms are knowed and understand by all the actors'),
        (1, 'The licenses terms are knowed but not understand by all the actors'),
        (2, 'The licenses terms are not knowed'),
    )
	FINANCIAL_COST = (
        (1, 'Less than 50 EUROS'),
        (2, 'Less than 300 EUROS'),
        (3, 'Less than 1 000 EUROS'),
        (4, 'Less than 3 000 EUROS'),
        (5, 'More than 3 000 EUROS'),
    )
	FINANCIAL_ACTIVE = (
        (1, 'Less than 10'),
        (2, 'Less than 100'),
        (3, 'Less than 1 000'),
        (4, 'Less than 10 000'),
        (5, 'More than 10 000'),
    )
	FINANCIAL_COMPLIANT = (
        (0, 'Full compliant'),
        (1, 'Risk less than 1 % non compliant'),
        (2, 'Risk less than 5 % non compliant'),
        (3, 'Risk less than 10 % non compliant'),
        (4, 'Risk more than 10 % non compliant'),
    )
	FINANCIAL_BUSINESS = (
        (0, 'Non compliance have no impact on the business'),
        (1, 'Non compliance can have impact on the Business'),
        (2, 'Non compliance stop the business'),
    )
	PROCESSUS_ACTORS = (
        (0, 'The actors are identified and trained'),
        (1, 'The actors are identified and not trained'),
        (2, 'The actors are not well identified'),
    )
	PROCESSUS_COMPLEXITY = (
        (0, 'Rules are simple and no depends on moving criteria'),
        (1, 'Rules are simple but depends on moving criteria (like rules depending of the country)'),
        (2, 'Rules are complex and no depends on moving criteria'),
        (3, 'Rules are complex but depends on moving criteria (like server physical where run the server virtual)'),
    )
	PROCESSUS_STABILITY = (
        (0, 'Rules have never change'),
        (1, 'There is an potential risk of change on the rules in the next 12 month'),
        (2, 'Rules have already change or will change in the next 12 month'),
    )
    # Item associe 
	item = models.ForeignKey(SAM_Item)
	Month_of_the_analyse = models.CharField(max_length=2, choices=MONTH_ANALYSE, default = '01')
	Year_of_the_analyse = models.CharField(max_length=4, choices=YEAR_ANALYSE, default = '2014')
	# Liste des risques a evaluer
	Data_and_Private_Life = models.BigIntegerField(choices=LEGAL_DATA, default = 0)
	Knowledge_of_License_rules = models.BigIntegerField(choices=LEGAL_LICENCE, default = 0)
	Unit_cost = models.BigIntegerField(choices=FINANCIAL_COST, default = 1)
	Active_Licenses = models.BigIntegerField(choices=FINANCIAL_ACTIVE, default = 1)
	Compliance_evaluation = models.BigIntegerField(choices=FINANCIAL_COMPLIANT, default = 0)
	Impact_on_Business = models.BigIntegerField(choices=FINANCIAL_BUSINESS, default = 0)
	Actors_Identification_and_Training = models.BigIntegerField(choices=PROCESSUS_ACTORS, default = 0)
	Complexity_of_License_rules = models.BigIntegerField(choices=PROCESSUS_COMPLEXITY, default = 0)
	Stability_of_License_rules = models.BigIntegerField(choices=PROCESSUS_STABILITY, default = 0)
	# Definit si il s'agit de l'analyse active
	Calculated_risk_level = models.BigIntegerField(default=0)
	Analyse_active = models.BooleanField(default = False)
	class Meta:
		unique_together = ('Month_of_the_analyse', 'Year_of_the_analyse', 'item')
	def __unicode__(self):
		return self.item

# Formlaire de Saisie d'un nouveau software gere
class SAM_RiskForm(ModelForm):
	class Meta:
		model = SAM_Risk
		exclude = ('item', 'Calculated_risk_level',)
