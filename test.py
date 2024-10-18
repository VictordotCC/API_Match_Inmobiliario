import json

with open('json', 'r') as file:
    data = json.load(file)
    print('area_total: '+ str(data['attributes'][7]['value_struct']['number'])) #1
    #print(str(data['?????'])) #2
    print('habitaciones: ' + str(data['attributes'][5]['value_name'])) #3
    print('precio_uf:' + str(data['sale_price']['amount'])) #4
    print('currency: ' + str(data['sale_price']['currency_id'])) #tipo de precio 
    #print(str(data['?????'])) #5
    #print(str(data['?????'])) #6
    #print(str(data['?????'])) #7
    print('tipo_vivienda: '+str(data['attributes'][13]['value_name'])) #8 pasar a integer
    print('nombre_vivienda: '+str(data['title'])) #9
    print('descripcion: ' + str(data['location']['address_line'])) #10 direccion como parte de descripcion?
    print('condicion: '+str(data['attributes'][0]['value_name'])) #11
    print('tipo_operacion: '+str(data['attributes'][12]['value_name'])) #12 pasar a boolean
    print('banos: '+str(data['attributes'][4]['value_name'])) #13
    print('area_construida: '+str(data['attributes'][6]['value_struct']['number'])) #14
    print('latitud : '+ str(data['location']['latitude'])) #15
    print('longitud : ' +str(data['location']['longitude'])) #16
    #print(str(data['?????'])) #17 se calcula, no consulta
    #print(str(data['?????'])) #18
    #print(str(data['?????'])) #19 Colocar fecha por defecto
    print('links contacto: '+str(data['permalink'])) #20
    print('vecindario: ' +str(data['location']['neighborhood']['name'])) #21 tratar
    print('comuna: ' +str(data['location']['city']['name'])) #22 tratar
    #print(str(data['?????'])) #23 tratar
    print('region: ' + str(data['location']['state']['name'])) #24 tratar
    print('imagen: ' + str(data['thumbnail'])) #IMAGEN


