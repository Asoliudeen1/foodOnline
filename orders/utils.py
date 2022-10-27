import datetime
from vendors.models import Vendor
import simplejson as json


def generate_order_number(pk):
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H')
    order_number = current_datetime + str(pk)
    return order_number


 # Get Total data for each Vendor
def get_total_by_vendor(order, vendor_id):
    subtotal = 0
    tax = 0
    tax_dict = {}
    total_data = json.loads(order.total_data)
    data = total_data.get(str(vendor_id))
    
        
    for key, val in data.items():
        subtotal += float(key)
        val = val.replace("'", '"')
        val = json.loads(val)
        tax_dict.update(val)

        # Calculate the tax
        #{'CGST': {'9.00': '6.03'}, 'GST': {'7.00': '4.69'}}
        for i in val:
            for j in val[i]:
                tax += float(val[i][j])
    grand_total = float(subtotal) + float(tax)
    context = {
        'subtotal': subtotal,
        'tax_dict': tax_dict,
        'grand_total': grand_total
    }
    return context