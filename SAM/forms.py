from django.forms import ModelForm
from models import SAM_Item

class SAM_ItemForm(ModelForm):
	class META:
		model = SAM_Item