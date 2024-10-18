import json

with open('json', 'r') as file:
    data = json.load(file)
    print('precio_uf:' + str(data['sale_price']['amount'])) #4
    print('currency: ' + str(data['sale_price']['currency_id'])) #tipo de precio 
    print('nombre_vivienda: '+str(data['title'])) #9
    
    print('descripcion: ' + str(data['location']['address_line'])) #10 direccion como parte de descripcion?   TODO: Scrapping 
    
    print('latitud : '+ str(data['location']['latitude'])) #15
    print('longitud : ' +str(data['location']['longitude'])) #16
    print('links contacto: '+str(data['permalink'])) #20
    print('vecindario: ' +str(data['location']['neighborhood']['name'])) #21 tratar
    print('comuna: ' +str(data['location']['city']['name'])) #22 tratar
    #print(str(data['?????'])) #23 tratar
    print('region: ' + str(data['location']['state']['name'])) #24 tratar
    print('imagen: ' + str(data['thumbnail'])) #IMAGEN TODO: Scrapping

    for attrib in data['attributes']:
        if attrib['id'] == 'MAX_TOTAL_AREA' or attrib['id'] == 'TOTAL_AREA':
            print('area_total: '+ str(attrib['value_struct']['number'])) #1
        if attrib['id'] == 'MAX_BEDROOMS' or attrib['id'] == 'BEDROOMS':
            print('habitaciones: ' + str(attrib['value_name'])) #3
        if attrib['id'] == 'PROPERTY_TYPE':
            print('tipo_vivienda: '+str(attrib['value_name'])) #8 pasar a integer Casa = 1, Departamento = 0
        if attrib['id'] == 'ITEM_CONDITION':
            print('condicion: '+str(attrib['value_name'])) #11 Nuevo, Usado
        if attrib['id'] == 'OPERATION':
            print('tipo_operacion: '+str(attrib['value_name'])) #12 pasar a boolean Venta = 0, Arriendo = 1
        if attrib['id'] == 'FULL_BATHROOMS' or attrib['id'] == 'MAX_BATHROOMS':
            print('banos: '+str(attrib['value_name'])) #13
        if attrib['id'] == 'COVERED_AREA' or attrib['id'] == 'MAX_COVERED_AREA':
            print('area_construida: '+str(attrib['value_struct']['number'])) #14
    
    """#print(str(data['?????'])) #2
    #print(str(data['?????'])) #5
    #print(str(data['?????'])) #6
    #print(str(data['?????'])) #7
    #print(str(data['?????'])) #17 se calcula, no consulta
    #print(str(data['?????'])) #18
    #print(str(data['?????'])) #19 Colocar fecha por defecto"""



