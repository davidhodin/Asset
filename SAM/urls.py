from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^admin/$', 'SAM.views.adminData'),
	url(r'^import/$', 'SAM.views.importForm'),
	url(r'^risk/$', 'SAM.views.risk'),
	url(r'^indicators/$', 'SAM.views.indicators'),
	### Zoom on import management
	url(r'^import/PcSW/$', 'SAM.views.importFilePC'),
	url(r'^import/AddPcSW/$', 'SAM.views.consolidatePC'),
	url(r'^import/ServerSW/$', 'SAM.views.importFileServer'),
	url(r'^import/AddServerSW/$', 'SAM.views.consolidateServer'),
	### Zoom on admin management
	url(r'^admin/zone/$', 'SAM.views.zone'),
	url(r'^admin/zone/(?P<zone>\d+)/$', 'SAM.views.countries'),
	url(r'^admin/countries/$', 'SAM.views.countryImport'),
	url(r'^admin/countries/(?P<country>\d+)/$', 'SAM.views.countryLink'),
	#
	url(r'^admin/appToStudy/(?P<app>\d+)/$', 'SAM.views.appToStudy'),
	url(r'^admin/appImported/$', 'SAM.views.appImported'),
	url(r'^admin/appAnalysedFREE/$', 'SAM.views.appAnalysedFREE'),
	url(r'^admin/appAnalysedPATCH/$', 'SAM.views.appAnalysedPATCH'),
	url(r'^admin/appAnalysedFORBIDDEN/$', 'SAM.views.appAnalysedFORBIDDEN'),
	url(r'^admin/appAnalysedLICENSED/$', 'SAM.views.appAnalysedLICENSED'),
	url(r'^admin/appNotAnalysed/$', 'SAM.views.appNotAnalysed'),
	#
	url(r'^admin/masterSW/$', 'SAM.views.riskMasters'),
	url(r'^admin/masterSW/(?P<masterSW>\d+)/$', 'SAM.views.riskMasterManage'),
	url(r'^admin/masterSW/add/(?P<masterSW>\d+)/(?P<appSW>\d+)/$', 'SAM.views.riskMastedAddSW'),
	url(r'^admin/masterSW/del/(?P<masterSW>\d+)/(?P<appSW>\d+)/$', 'SAM.views.riskMasterRemoveSW'),
	url(r'^admin/item/$', 'SAM.views.riskItem'),
	### Zoom on risk management
	url(r'^risk/analyseForbidden/$', 'SAM.views.analyseForbidden'),
	url(r'^risk/analysePatches/$', 'SAM.views.analysePatches'),
	url(r'^risk/analyseFree/$', 'SAM.views.analyseFree'),
	url(r'^risk/analyseLicenced/$', 'SAM.views.analyseLicenced'),
	url(r'^risk/analyseMaster/$', 'SAM.views.analyseMaster'),
	url(r'^risk/risk/List/$', 'SAM.views.risksList'),
	url(r'^risk/risk/(?P<riskID>\d+)/$', 'SAM.views.riskItemInfo'),
	url(r'^risk/risk/add/(?P<riskID>\d+)/$', 'SAM.views.riskAdd'),
	url(r'^risk/risk/ListMaster/$', 'SAM.views.risksMaster'),
	### Zoom on indicators
	url(r'^indicators/Process/Status/$', 'SAM.views.indicatorsProcessStatus'),
	url(r'^indicators/Process/Master/$', 'SAM.views.indicatorsProcessMaster'),
	url(r'^indicators/Process/Studied/$', 'SAM.views.indicatorsProcessStudied'),
	url(r'^indicators/Risk/Zone/$', 'SAM.views.indicatorsRiskZone'),
	url(r'^indicators/Risk/Average/$', 'SAM.views.indicatorsRiskAverage')
	)