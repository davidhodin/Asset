#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.forms import ModelForm
from django.core.context_processors import csrf
from SAM.models import SAM_Zone, SAM_ZoneForm
from SAM.models import SAM_Country, SAM_CountryForm, SAM_Countries_To_Import, SAM_Countries_Imported, SAM_Countries_ImportedForm
from SAM.models import ImportSoftwareInstall, AnalyseSearch
from SAM.models import SAM_Item, SAM_ItemForm, SAM_Risk, SAM_RiskForm, SAM_Master, SAM_MasterForm
from SAM.models import SAM_IMPORT, SAM_PC_Imported, SAM_Product_To_Import, SAM_Product_To_ImportForm, SAM_PC_Analysed
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.db.models import Avg
import csv

###############################################
# Liens principaux
###############################################

# Administration des donnees -- Page principale
@login_required
def importForm(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		return render(request, 'Risk_Import.html')

# Administration des donnees --- Page principale
@login_required
def adminData(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		return render(request, 'Risk_Admin.html')

# Analyse de risque --- Page principale
@login_required
def risk(request):
	return render(request, 'Risk_Analysis.html')

# Suivi des indicateurs --- Page principale
@login_required
def indicators(request):
	return render(request, 'Risk_Indicators.html')
	
###############################################
# Liens d'administration --- Permet la gestion des "Zones/Pays/Pays importés", des "Softwares importés" et des "Master Softwares + Items de risk"
###############################################

# Vue vers toutes les zones
@login_required
def zone(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		# Teste si la zone 'GROUP' existe, si non, l'ajoute
		try:
			SAM_Zone.objects.get(zone_Name = 'GROUP')
		except:
			newZone = SAM_Zone(zone_Name = 'GROUP')
			newZone.save()
		# Traite le formulaire
		if request.method == "POST":
			form = SAM_ZoneForm(request.POST)
			if form.is_valid():
				form.save()
				form = SAM_ZoneForm()
		else:
			form = SAM_ZoneForm()
		return render(request, 'Risk_Admin_Zone.html', { 'form': form, 'zones': SAM_Zone.objects.all()})

# Vue de gestion des pays d'une zone
@login_required
def countries(request, zone=0):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		if request.method == "POST":
			form = SAM_CountryForm(request.POST)
			if form.is_valid():
				country = form.save(commit = False)
				country.zone = SAM_Zone.objects.get(id = zone)
				country.save()
				modifZone = SAM_Zone.objects.get(zone_Name = country.zone.zone_Name)
				modifZone.zone_Nbre_Pays = modifZone.zone_Nbre_Pays + 1
				modifZone.save()
				form = SAM_CountryForm()
		else:
			form = SAM_CountryForm()
		return render(request, 'Risk_Admin_Country.html', { 'form': form, 'zone_Name' : SAM_Zone.objects.get(id = zone).zone_Name, 'pays': SAM_Country.objects.filter(zone = zone) })

# Vue de gestion d'un pays
@login_required
def countryImport(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		return render(request, 'Risk_Admin_Country_Imported_List.html', { 'pays': SAM_Countries_Imported.objects.all() })

# Vue de gestion d'un pays dont l'assiociation est deja definie
@login_required
def countryLink(request, country=0):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		if request.method == "POST":
			form = SAM_Countries_ImportedForm(request.POST)
			if form.is_valid():
				newCountry = form.save(commit = False)
				newCountry.country_Code = SAM_Country.objects.get(id=country)
				newCountry.save()
				modifImported = newCountry.country_Imported
				modifImported.associated = True
				modifImported.save()
				modifCount = newCountry.country_Code
				modifCount.country_Nbre_Countries_Imported = modifCount.country_Nbre_Countries_Imported + 1
				modifCount.save()
				form = SAM_Countries_ImportedForm()
		else:
			form = SAM_Countries_ImportedForm()
		return render(request, 'Risk_Admin_Country_Imported.html', { 'form': form, 'name': SAM_Country.objects.get(id=country).country_Name , 'pays': SAM_Countries_To_Import.objects.filter(associated=False) })

# Vue de gestion des applications que l'on souhaite gerer
@login_required
def appToStudy(request, app=0):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		a = SAM_Product_To_Import.objects.get(id = app)
		if request.method == "POST":
			form = SAM_Product_To_ImportForm(request.POST, instance=a)
			if form.is_valid():
				assiociation = form.save()
				if assiociation.product_Type == 'Free':
					return redirect('/sam/admin/appAnalysedFREE/')
				elif assiociation.product_Type == 'Forbidden':
					return redirect('/sam/admin/appAnalysedFORBIDDEN/')
				elif assiociation.product_Type == 'Patch':
					return redirect('/sam/admin/appAnalysedPATCH/')
				elif assiociation.product_Type == 'Licenced':
					return redirect('/sam/admin/appAnalysedLICENSED/')
				else:
					return redirect('/sam/admin/appNotAnalysed/')
		else:	
			form = SAM_Product_To_ImportForm(instance=a)
		return render(request, 'Risk_Admin_appToStudy.html', { 'form': form })

# Vue listant toutes les applications non geres
@login_required
def appImported(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		liste = SAM_Product_To_Import.objects.filter(product_Type='Not defined').order_by('product_Imported')[:100]
		return render(request, 'Risk_Admin_AppImport.html', { 'liste' : liste })

# Vue listant toutes les applications FREE
@login_required
def appAnalysedFREE(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		liste = SAM_Product_To_Import.objects.filter(product_Type='Free').order_by('product_Imported')
		return render(request, 'Risk_Admin_appAnalysed_FREE.html', { 'liste' : liste })

# Vue listant toutes les applications PATCH
@login_required
def appAnalysedPATCH(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		liste = SAM_Product_To_Import.objects.filter(product_Type='Patch').order_by('product_Imported')
		return render(request, 'Risk_Admin_appAnalysed_PATCH.html', { 'liste' : liste })

# Vue listant toutes les applications FORBIDDEN
@login_required
def appAnalysedFORBIDDEN(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		liste = SAM_Product_To_Import.objects.filter(product_Type='Forbidden').order_by('product_Imported')
		return render(request, 'Risk_Admin_appAnalysed_FORBIDDEN.html', { 'liste' : liste })

# Vue listant toutes les applications LICENSED
@login_required
def appAnalysedLICENSED(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		liste = SAM_Product_To_Import.objects.filter(product_Type='Licenced').order_by('product_Imported')
		return render(request, 'Risk_Admin_appAnalysed_LICENSED.html', { 'liste' : liste })

# Vue listant toutes les applications non analysées
@login_required
def appNotAnalysed(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		liste = SAM_Product_To_Import.objects.filter(product_Type='Not analysed').order_by('product_Imported')
		return render(request, 'Risk_Admin_appNotAnalysed.html', { 'liste' : liste })

# Gestion des Master Software
@login_required
def riskMasters(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		if request.method == "POST":
			form = SAM_MasterForm(request.POST)
			if form.is_valid():
				form.save()
				form = SAM_MasterForm()
		else:
			form = SAM_MasterForm()
		return render(request, 'Risk_Admin_Master_New.html', { 'form': form, 'masterApps': SAM_Master.objects.all().order_by('supplier_and_product')})

# Gestion d'un Master Software
@login_required
def riskMasterManage(request, masterSW=0):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		# Recupere la liste des SW associes au Master SW ainsi que les SW non associes
		SW_Associes = SAM_Product_To_Import.objects.filter(master_Software = masterSW).order_by('product_Imported')
		SW_Non_Associes = SAM_Product_To_Import.objects.filter(master_Software = None, product_Type = 'Licenced').order_by('product_Imported')
		return render(request, 'Risk_Admin_Master_Manage.html', { 'associes': SW_Associes, 'nonAssocies': SW_Non_Associes, 'masterSW': masterSW})

# Ajout d'un managed software au Master Software selectionne
@login_required
def riskMastedAddSW(request, appSW=0, masterSW=0):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		try:
			# ajout du lien concerne
			aModier = SAM_Product_To_Import.objects.get(id=appSW)
			aModier.master_Software = SAM_Master.objects.get(id=masterSW)
			aModier.save()
		except:
			print 'Erreur de lien'
		return redirect('/sam/admin/masterSW/'+str(masterSW)+'/')

# Suppression d'un managed software au Master Software selectionne
@login_required
def riskMasterRemoveSW(request, appSW=0, masterSW=0):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		try:
			# ajout du lien concerne
			aModier = SAM_Product_To_Import.objects.get(id=appSW)
			aModier.master_Software = None
			aModier.save()
		except:
			print 'Erreur de lien'
		return redirect('/sam/admin/masterSW/'+str(masterSW)+'/')

# Gestion des Items de risque
@login_required
def riskItem(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		if request.method == 'POST': 
			form = SAM_ItemForm(request.POST) 
			if form.is_valid(): 
				form.save()
				form = SAM_ItemForm()
		else:
			form = SAM_ItemForm()	
		return render(request, 'Risk_Admin_Item_New.html', { 'form': form, 'riskItems': SAM_Item.objects.all().order_by('master_Software') })

###############################################
# Liens d'import
###############################################

# Import de fichier 3.2 d'inventaire des SW sur PC
@login_required
def importFilePC(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		resultat = ''
		if request.method == 'POST':
			form = ImportSoftwareInstall(request.POST, request.FILES)
			if form.is_valid():
				resultat = request.POST['month'] + '-' + request.POST['year']
				IdImport = SAM_IMPORT(import_Date = resultat, domain = request.POST['domain'])
				IdImport.save()
				imported = 0
				notImported = 0
				with request.FILES['file'] as csvfile:
					csvReader = csv.reader(csvfile, delimiter=';', quotechar='|')
					line1 = True
					for row in csvReader:
						if line1 == True:
							line1 = False
						else:
							# Analyse des information decrivant le produit
							try:
								productNameData = unicode(row[0], 'utf-8')
							except:
								productNameData = 'ErrorProduct'
							try:
								productVersionData = unicode(row[1], 'utf-8')
							except:
								productVersionData = 'ErrorVersion'
							try:
								productManufacturerData = unicode(row[2], 'utf-8')
							except:
								productManufacturerData = 'ErrorManufacturer'
							# Ajout de l'application 
							try:
									SAM_Product_To_Import.objects.get(product_Imported = productManufacturerData + ' - ' + productNameData + ' - '  + productVersionData)
							except:
									newSW = SAM_Product_To_Import(product_Imported = productManufacturerData + ' - ' + productNameData + ' - '  + productVersionData)
									newSW.save()
							try:
								departmentData = row[3].encode('utf-8')
								# Ajout du pays importe
								try:
									SAM_Countries_To_Import.objects.get(country_Imported = departmentData)
								except:
									newCountry = SAM_Countries_To_Import(country_Imported = departmentData)
									newCountry.save()
							except:
								departmentData = 'ErrorDepartment'
							# Recuperation des informations du nombre d'installation
							try:
								instancesData = int(row[4])
							except:
								instancesData = 0
							# On importe que lignes n'ayant pas d'instances nulles, le reste n'a pas d'importance
							if instancesData <> 0:
								importation = SAM_PC_Imported(product_Imported = productManufacturerData + ' - ' + productNameData + ' - '  + productVersionData, department = departmentData, instances = instancesData, import_Date = resultat, domain = request.POST['domain'], SAM_Import=IdImport)
								print productManufacturerData + ' - ' + productNameData + ' - ' + productVersionData + '---' + 'IMPORTED'
								importation.save()
								imported = imported + 1
							else:
								print productNameData + '---' + 'NOT IMPORTED'
								notImported = notImported + 1
				resultat = 'Success of [' + resultat + '] Import - Sumary >>> [' + str(imported) + '] are IMPORTED' + ' - [' + str(notImported) + '] are NOT IMPORTED'
		else:
			form = ImportSoftwareInstall()
		return render(request, 'Risk_Import_PC_Import.html', { 'form': form, 'resultat' : resultat })

# Administration des donnees
@login_required
def consolidatePC(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		if request.method == 'POST':
			nonAnalyses = 0
			zoneAdded = 0
			ajoutSimple = 0
			ajoutCreation = 0
			# Suppression des lignes de 'Not analysed'
			produitsAsupprimer = SAM_Product_To_Import.objects.filter(product_Type = 'Not analysed')
			for supprime in produitsAsupprimer:
				SAM_PC_Imported.objects.filter(product_Imported = supprime.product_Imported).delete()
				nonAnalyses = nonAnalyses + 1
			#Consolide les zones de l'import
			itemsSansZones = SAM_PC_Imported.objects.filter(zone_Name = '')
			for item in itemsSansZones:
				try:
					itemGere = SAM_Countries_To_Import.objects.get(country_Imported = item.department)
					if itemGere.associated == True:
						item.zone_Name = SAM_Zone.objects.get(id=(SAM_Country.objects.get(id = SAM_Countries_Imported.objects.get(country_Imported = itemGere.id).country_Code.id).zone.id)).zone_Name
						item.save()
						print ':-) >>> association reussie >>> ' + item.department + ' = ' + item.zone_Name
						zoneAdded = zoneAdded + 1
				except:
					print 'Erreur sur le department : ' + item.department
			# Consolications des extractions pour le groupe
			produitsAconsolider = SAM_PC_Imported.objects.filter(group_Done = False)
			for produit in produitsAconsolider:
				try:
					toUpdate = SAM_PC_Analysed.objects.get(managed = (SAM_Product_To_Import.objects.get(product_Imported = produit.product_Imported)), zone = SAM_Zone.objects.get(zone_Name = 'GROUP'), import_Date = produit.import_Date, domain = produit.domain)
					toUpdate.instances = toUpdate.instances + produit.instances
					print 'Inventaire existant = ajout de nouvelles instances'
					ajoutSimple = ajoutSimple + 1
				except:
					toUpdate = SAM_PC_Analysed(managed = (SAM_Product_To_Import.objects.get(product_Imported = produit.product_Imported)),zone = SAM_Zone.objects.get(zone_Name = 'GROUP'), instances = produit.instances, import_Date = produit.import_Date, domain = produit.domain)
					print 'Inventaire non existant = creation d un nouveau soft'
					ajoutCreation = ajoutCreation + 1
				toUpdate.save()
				produit.group_Done = True
				produit.save()
			# Consolications des extractions avec zones renseignees
			produitsAconsolider = SAM_PC_Imported.objects.exclude(zone_Name = '')
			for produit in produitsAconsolider:
				try:
					toUpdate = SAM_PC_Analysed.objects.get(managed = (SAM_Product_To_Import.objects.get(product_Imported = produit.product_Imported)), zone = SAM_Zone.objects.get(zone_Name = produit.zone_Name), import_Date = produit.import_Date, domain = produit.domain)
					toUpdate.instances = toUpdate.instances + produit.instances
					print 'Inventaire existant = ajout de nouvelles instances'
					ajoutSimple = ajoutSimple + 1
				except:
					toUpdate = SAM_PC_Analysed(managed = (SAM_Product_To_Import.objects.get(product_Imported = produit.product_Imported)),zone =  SAM_Zone.objects.get(zone_Name = produit.zone_Name), instances = produit.instances, import_Date = produit.import_Date, domain = produit.domain)
					print 'Inventaire non existant = creation d un nouveau soft'
					ajoutCreation = ajoutCreation + 1
				toUpdate.save()
				produit.delete()
			# Affichage du resultat
			resultat = 'Result... ' + str(nonAnalyses) + ' import deleted (application not analysed), ' + str(zoneAdded) + ' zone consolidate, ' + str(ajoutCreation) + ' application added, ' + str(ajoutSimple) + ' application updated'
		else:
			resultat = 'Click bellow to execute...'
		c = {}
		c.update(csrf(request))
		c.update({'resultat' : resultat})
		return render_to_response('Risk_Import_PC_Consolidate.html', c)



# Administration des donnees sur serveur
def importFileServer(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		return render_to_response('Risk_Import_Server_Import.html')

# Administration des donnees sur serveur
def consolidateServer(request):
	if (request.user.has_perm("SAM.add_SAM_Zone") == False):
		return render(request, 'Access.html')
	else:
		return render_to_response('Risk_Import_Server_Consolidate.html')


###############################################
# Liens d'analyse de risque
###############################################

# Analyse des logiciels Forbidden
@login_required
def analyseForbidden(request):
	if request.method == 'POST': 
		form = AnalyseSearch(request.POST)
		if form.is_valid():
			liste = SAM_PC_Analysed.objects.filter( import_Date = request.POST['month'] + '-' + request.POST['year'], managed__in = SAM_Product_To_Import.objects.filter(product_Type = 'Forbidden'), zone = SAM_Zone.objects.get(zone_Name = request.POST['zone']) ).order_by('-import_Date','-instances')
		try:
			if request.POST['Extract']:
				print 'Extract Forbidden Data'
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="extractForbidden.csv"'
				writer = csv.writer(response)
				for s in liste:
					writer.writerow([s.managed.product_Imported, s.zone, s.domain, s.import_Date, s.instances])
				return response
		except:
			print 'Display only'
	else:
		liste = []
		form = AnalyseSearch()
	zoneList = SAM_Zone.objects.all()
	return render(request, 'Risk_Analysis_Analyses_Forbidden.html', { 'form': form, 'liste' : liste , 'zones' : zoneList})

# Analyse des logiciels Patch
@login_required
def analysePatches(request):
	if request.method == 'POST': 
		form = AnalyseSearch(request.POST)
		if form.is_valid():
			liste = SAM_PC_Analysed.objects.filter( import_Date = request.POST['month'] + '-' + request.POST['year'], managed__in = SAM_Product_To_Import.objects.filter(product_Type = 'Patch'), zone = SAM_Zone.objects.get(zone_Name = request.POST['zone']) ).order_by('-import_Date','-instances')
		try:
			if request.POST['Extract']:
				print 'Extract Forbidden Data'
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="extractPatches.csv"'
				writer = csv.writer(response)
				for s in liste:
					writer.writerow([s.managed.product_Imported, s.zone, s.domain, s.import_Date, s.instances])
				return response
		except:
			print 'Display only'
	else:
		liste = []
		form = AnalyseSearch()
	zoneList = SAM_Zone.objects.all()
	return render(request, 'Risk_Analysis_Analyses_Patch.html', { 'form': form, 'liste' : liste , 'zones' : zoneList})

# Analyse des logiciels Free
@login_required
def analyseFree(request):
	if request.method == 'POST': 
		form = AnalyseSearch(request.POST)
		if form.is_valid():
			liste = SAM_PC_Analysed.objects.filter( import_Date = request.POST['month'] + '-' + request.POST['year'], managed__in = SAM_Product_To_Import.objects.filter(product_Type = 'Free'), zone = SAM_Zone.objects.get(zone_Name = request.POST['zone']) ).order_by('-import_Date','-instances')
		try:
			if request.POST['Extract']:
				print 'Extract Forbidden Data'
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="extractFree.csv"'
				writer = csv.writer(response)
				for s in liste:
					writer.writerow([s.managed.product_Imported, s.zone, s.domain, s.import_Date, s.instances])
				return response
		except:
			print 'Display only'
	else:
		liste = []
		form = AnalyseSearch()
	zoneList = SAM_Zone.objects.all()
	return render(request, 'Risk_Analysis_Analyses_Free.html', { 'form': form, 'liste' : liste , 'zones' : zoneList})

# Analyse des logiciels soumis a licences
@login_required
def analyseLicenced(request):
	if request.method == 'POST': 
		form = AnalyseSearch(request.POST)
		if form.is_valid():
			liste = SAM_PC_Analysed.objects.filter( import_Date = request.POST['month'] + '-' + request.POST['year'], managed__in = SAM_Product_To_Import.objects.filter(product_Type = 'Licenced'), zone = SAM_Zone.objects.get(zone_Name = request.POST['zone']) ).order_by('-import_Date','-instances')
		try:
			if request.POST['Extract']:
				print 'Extract Forbidden Data'
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="extractLicenced.csv"'
				writer = csv.writer(response)
				for s in liste:
					writer.writerow([s.managed.product_Imported, s.zone, s.domain, s.import_Date, s.instances])
				return response
		except:
			print 'Display only'
	else:
		liste = []
		form = AnalyseSearch()
	zoneList = SAM_Zone.objects.all()
	return render(request, 'Risk_Analysis_Analyses_Licenced.html', { 'form': form, 'liste' : liste , 'zones' : zoneList})

# Analyse des Master Softwares
@login_required
def analyseMaster(request):
	if request.method == 'POST': 
		form = AnalyseSearch(request.POST)
		if form.is_valid():
			liste = SAM_PC_Analysed.objects.filter( import_Date = request.POST['month'] + '-' + request.POST['year'], managed__in = SAM_Product_To_Import.objects.filter(master_Software = SAM_Master.objects.get(id = request.POST['master'])), zone = SAM_Zone.objects.get(zone_Name = request.POST['zone']) ).order_by('-import_Date','-instances')
		try:
			if request.POST['Extract']:
				print 'Extract Forbidden Data'
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="extractMaster.csv"'
				writer = csv.writer(response)
				for s in liste:
					writer.writerow([s.managed.product_Imported, s.zone, s.domain, s.import_Date, s.instances])
				return response
		except:
			print 'Display only'
	else:
		liste = []
		form = AnalyseSearch()
	zoneList = SAM_Zone.objects.all()
	masterList = SAM_Master.objects.all()
	return render(request, 'Risk_Analysis_Analyses_Master.html', { 'form': form, 'liste' : liste , 'zones' : zoneList, 'masters' : masterList})

# Liste des Items de risque
@login_required
def risksList(request):
	if request.method == 'POST':
		liste = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = request.POST['zone'])).order_by('-actual_Risk')
	else:
		liste = None
		#liste = SAM_Item.objects.all().order_by('-actual_Risk')
	zoneList = SAM_Zone.objects.all()
	return render(request, 'Risk_Analysis_Risk_List.html', { 'liste': liste, 'zones': zoneList })

# Gestion des Items de risque
@login_required
def riskItemInfo(request, riskID = 0):
	SAM_Item_details = SAM_Item.objects.get(id=riskID)
	SAM_Risk_List = SAM_Risk.objects.filter(item = SAM_Item_details).order_by('-Year_of_the_analyse', '-Month_of_the_analyse')
	SAM_Inventories = SAM_PC_Analysed.objects.filter(zone = SAM_Item_details.zone, managed__in = SAM_Product_To_Import.objects.filter(master_Software = SAM_Item_details.master_Software) ).order_by('-import_Date', '-instances')
	return render(request, 'Risk_Analysis_Risk_Item.html', { 'item': SAM_Item_details, 'riskList': SAM_Risk_List, 'inventoriesList':SAM_Inventories })

# Ajouter une analyse de risque
@login_required
def riskAdd(request, riskID = 0):
	if request.method == 'POST':
		form = SAM_RiskForm(request.POST)
		if form.is_valid():
			try:
				analyse = form.save(commit = False)
				analyse.item = SAM_Item.objects.get(id=riskID)
				# Calcule le niveau de risque et l'affecte
				if analyse.Data_and_Private_Life == 2 or analyse.Knowledge_of_License_rules == 2:
					legal_Risk = 2
				elif analyse.Data_and_Private_Life == 0 and analyse.Knowledge_of_License_rules == 0:
					legal_Risk = 0
				else:
					legal_Risk = 1
				if (analyse.Unit_cost * analyse.Active_Licenses * analyse.Compliance_evaluation) < 10:
					financial_Risk = 0
				elif (analyse.Unit_cost * analyse.Active_Licenses * analyse.Compliance_evaluation) < 30:
					financial_Risk = 1
				else:
					financial_Risk = 2
				if (financial_Risk * analyse.Impact_on_Business) < 2:
					business_Risk = (financial_Risk * analyse.Impact_on_Business)
				else:
					business_Risk = 2
				if analyse.Actors_Identification_and_Training == 2 or analyse.Complexity_of_License_rules == 2 or analyse.Stability_of_License_rules == 2:
					process_Risk = 2
				elif (analyse.Actors_Identification_and_Training + analyse.Complexity_of_License_rules + analyse.Stability_of_License_rules) == 3:
					process_Risk = 2
				elif (analyse.Actors_Identification_and_Training + analyse.Complexity_of_License_rules + analyse.Stability_of_License_rules) == 2:
					process_Risk = 1
				else:
					process_Risk = 0
				analyse.Calculated_risk_level = legal_Risk + financial_Risk + business_Risk + process_Risk
				analyse.save()
				# Si c'est l'analyse active, alors affecte le score à l'item
				if analyse.Analyse_active == True:
					item_Analized = SAM_Item.objects.get(id=riskID)
					# Désactive les anciennes Analyse
					print 'recherche'
					for items in SAM_Risk.objects.filter(item = item_Analized):
						if (items != analyse) and (items.Analyse_active == True) :
							print 'update a faire'
							items.Analyse_active = False
							items.save()
							print 'updateOk'
					# Actualise le score
					item_Analized.actual_Risk = analyse.Calculated_risk_level
					item_Analized.save()
			except:
				print 'Error on adding risk analysis'
			return redirect('/sam/risk/risk/' + riskID)
	else:
		form = SAM_RiskForm()
	return render(request, 'Risk_Analysis_Risk_Add.html', { 'form': form })

# Liste des Items de risque qui n'ont pas d'analyse de risque
@login_required
def risksMaster(request):
	listeDone = []
	for item in SAM_Risk.objects.all():
		listeDone.append(item.item.id) 
	listeMaster = SAM_Item.objects.exclude(id__in = listeDone)
	#listeMaster = SAM_Item.objects.all()
	return render(request, 'Risk_Analysis_Risk_MasterList.html', { 'liste': listeMaster })

###############################################
# Liens des indicateurs
###############################################

# Suivi des indicateurs --- Page principale
@login_required
def indicatorsProcessStatus(request):
	print request.user
	# Compte le nombre de SW
	nbNotDefined = SAM_Product_To_Import.objects.filter(product_Type = 'Not defined').count()
	nbNotAnalysed = SAM_Product_To_Import.objects.filter(product_Type = 'Not analysed').count()
	nbPatch = SAM_Product_To_Import.objects.filter(product_Type = 'Patch').count()
	nbForbidden = SAM_Product_To_Import.objects.filter(product_Type = 'Forbidden').count()
	nbFree = SAM_Product_To_Import.objects.filter(product_Type = 'Free').count()
	nbLicenced = SAM_Product_To_Import.objects.filter(product_Type = 'Licenced').count()
	return render(request, 'Risk_Indicators_Process_StatusSW.html', { 'nbNotDefined': nbNotDefined, 'nbNotAnalysed': nbNotAnalysed, 'nbPatch': nbPatch, 'nbForbidden': nbForbidden, 'nbFree': nbFree, 'nbLicenced': nbLicenced})

# Suivi des indicateurs --- Page principale
@login_required
def indicatorsProcessMaster(request):
	# Compte les master SW ainsi que les Soft à licences
	nbLicenced = SAM_Product_To_Import.objects.filter(product_Type = 'Licenced').count()
	print nbLicenced
	withMaster = SAM_Product_To_Import.objects.filter(master_Software__isnull = False).count()
	print withMaster
	return render(request, 'Risk_Indicators_Process_MasterSW.html', { 'nbLicenced': nbLicenced, 'withMaster': withMaster })

# Suivi des indicateurs --- Page principale
@login_required
def indicatorsProcessStudied(request):
	listeDone = []
	for item in SAM_Risk.objects.all():
		listeDone.append(item.item.id)
	listeGROUP = SAM_Item.objects.exclude(id__in = listeDone).filter(zone = SAM_Zone.objects.get(zone_Name = 'GROUP')).count()
	listeAIM = SAM_Item.objects.exclude(id__in = listeDone).filter(zone = SAM_Zone.objects.get(zone_Name = 'AIM').id).count()
	listeEUR = SAM_Item.objects.exclude(id__in = listeDone).filter(zone = SAM_Zone.objects.get(zone_Name = 'EUR').id).count()
	listeNA = SAM_Item.objects.exclude(id__in = listeDone).filter(zone = SAM_Zone.objects.get(zone_Name = 'NA').id).count()
	listeSA = SAM_Item.objects.exclude(id__in = listeDone).filter(zone = SAM_Zone.objects.get(zone_Name = 'SA').id).count()
	listeAC = SAM_Item.objects.exclude(id__in = listeDone).filter(zone = SAM_Zone.objects.get(zone_Name = 'AC').id).count()
	return render(request, 'Risk_Indicators_Process_StudiedSW.html', { 'listeGROUP': listeGROUP,'listeAIM': listeAIM,'listeEUR': listeEUR,'listeNA': listeNA,'listeSA': listeSA,'listeAC': listeAC})

# Suivi des indicateurs --- Page principale
@login_required
def indicatorsRiskZone(request):
	if request.method == 'POST':
		# Si on reçoit une requête, on récupère l'indicateur de risque pour la zone
		liste0 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = request.POST['zone']), actual_Risk = 0).count()
		liste1 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = request.POST['zone']), actual_Risk = 1).count()
		liste2 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = request.POST['zone']), actual_Risk = 2).count()
		liste3 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = request.POST['zone']), actual_Risk = 3).count()
		liste4 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = request.POST['zone']), actual_Risk = 4).count()
		liste5 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = request.POST['zone']), actual_Risk = 5).count()
		liste6 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = request.POST['zone']), actual_Risk = 6).count()
		liste7 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = request.POST['zone']), actual_Risk = 7).count()
		liste8 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = request.POST['zone']), actual_Risk = 8).count()
		liste9 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = request.POST['zone']), actual_Risk = 9).count()
		liste10 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = request.POST['zone']), actual_Risk = 10).count()
	else:
		# Sinon, c'est un get de la page donc on retourne 0 au niveau des indicateurs
		liste0 = 0
		liste1 = 0
		liste2 = 0
		liste3 = 0
		liste4 = 0
		liste5 = 0
		liste6 = 0
		liste7 = 0
		liste8 = 0
		liste9 = 0
		liste10 = 0
	zoneList = SAM_Zone.objects.all()
	return render(request, 'Risk_Indicators_Risk_Zone.html', { 'Liste0': liste0, 'Liste1': liste1, 'Liste2': liste2, 'Liste3': liste3, 'Liste4': liste4, 'Liste5': liste5, 'Liste6': liste6, 'Liste7': liste7, 'Liste8': liste8, 'Liste9': liste9, 'Liste10': liste10, 'zones': zoneList })

# Suivi des indicateurs --- Page principale
@login_required
def indicatorsRiskAverage(request):
	# initialisation des variables
	moyenne0 = 0
	somme0 = 0
	item0 = 0
	moyenne1 = 0
	somme1 = 0
	item1 = 0
	moyenne2 = 0
	somme2 = 0
	item2 = 0
	moyenne3 = 0
	somme3 = 0
	item3 = 0
	moyenne4 = 0
	somme4 = 0
	item4 = 0
	moyenne5 = 0
	somme5 = 0
	item5 = 0

	# Calcul de la moyenne par zone
	liste0 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = 'GROUP'))
	for item in liste0:
		print item.actual_Risk
		somme0 = somme0 + item.actual_Risk
		item0 = item0 + 1
	if item0 != 0:
		moyenne0 = somme0 / item0
	liste1 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = 'AIM'))
	for item in liste1:
		print item.actual_Risk
		somme1 = somme1 + item.actual_Risk
		item1 = item1 + 1
	if item1 != 0:
		moyenne1 = somme1 / item1
	liste2 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = 'EUR'))
	for item in liste2:
		print item.actual_Risk
		somme2 = somme2 + item.actual_Risk
		item2 = item2 + 1
	if item2 != 0:
		moyenne2 = somme2 / item2
	liste3 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = 'NA'))
	for item in liste3:
		print item.actual_Risk
		somme3 = somme3 + item.actual_Risk
		item3 = item3 + 1
	if item3 != 0:
		moyenne3 = somme3 / item3
	liste4 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = 'SA'))
	for item in liste4:
		print item.actual_Risk
		somme4 = somme4 + item.actual_Risk
		item4 = item4 + 1
	if item4 != 0:
		moyenne4 = somme4 / item4
	liste5 = SAM_Item.objects.filter(zone = SAM_Zone.objects.get( zone_Name = 'AC'))
	for item in liste5:
		print item.actual_Risk
		somme5 = somme5 + item.actual_Risk
		item5 = item5 + 1
	if item5 != 0:
		moyenne5 = somme5 / item5
	print moyenne0
	print moyenne1
	print moyenne2
	print moyenne3
	print moyenne4
	print moyenne5
	return render(request, 'Risk_Indicators_Risk_Average.html', { 'Liste0': moyenne0, 'Liste1': moyenne1, 'Liste2': moyenne2, 'Liste3': moyenne3, 'Liste4': moyenne4, 'Liste5': moyenne5 })
