from django.contrib import admin
from SAM.models import SAM_Zone
from SAM.models import SAM_Country, SAM_Countries_To_Import, SAM_Countries_Imported
from SAM.models import SAM_Item, SAM_Risk, SAM_Master
from SAM.models import SAM_IMPORT, SAM_PC_Imported, SAM_Product_To_Import, SAM_PC_Analysed

admin.site.register(SAM_Zone)

admin.site.register(SAM_Country)
admin.site.register(SAM_Countries_To_Import)
admin.site.register(SAM_Countries_Imported)

admin.site.register(SAM_Item)
admin.site.register(SAM_Risk)
admin.site.register(SAM_Master)

admin.site.register(SAM_IMPORT)
admin.site.register(SAM_PC_Imported)
admin.site.register(SAM_Product_To_Import)
admin.site.register(SAM_PC_Analysed)
