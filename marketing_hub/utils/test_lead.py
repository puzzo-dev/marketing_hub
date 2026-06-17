import frappe
def test():
    meta = frappe.get_meta("Lead")
    for f in meta.fields:
        if f.reqd:
            print(f.fieldname)
test()
