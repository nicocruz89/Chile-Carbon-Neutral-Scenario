# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 15:39:51 2020

@author: Nicolas Cruz
"""
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.style.use("ggplot")
import os
os.chdir('C:/Users/nicoc/OneDrive/Desktop/PMR/Escenarios Finales/1/modelo/')

#Lectura nombre escenario
f=open("Nombre_escenario.txt", "r")
nombre_escenario=f.read()

#Lectura de archivo
data_emisiones = pd.read_csv("../data_output/Emisiones_"+nombre_escenario+".csv")
data_offsets = pd.read_csv("../data_output/solucion_offset.csv")
data_input_offsets = pd.read_csv("../data_input/data_offset.csv")
data_costs = pd.read_csv("../data_output/solucion_detalle_costos.csv")

#Offsets 
offsets = pd.DataFrame(columns=['Energy', 'Waste','IPPU','Agriculture','LULUCF','Others'])
data_offsets.set_index('GEI',inplace=True)
results = pd.DataFrame()

waste_offsets = ['offset_compostaje_planta','offset_compostaje_ferias','offset_compostaje_domiciliario']
energy_offsets = ['Hy_usos_motrices','Hy_verde','Hy_usos_termicos_via_gasoductos','Generacion_distribuida','Renovacion_energetica_viviendas',
                  'SST_Residencial_publico','Calefaccion_elec_publico_comercial','Geotermia','RT_Viviendas_vulnerables','Calefaccion_distrital','Ley_eficiencia_energetica',
		          'Energetica','MEPS_Nuevos']
agriculture_offsets = ['offset_mejora_alimen_bovinos','offset_inhibidoresN2_fert','offset_agricultura_organica','offset_secuestro_CO2',
                       'offset_biodigestores','offset_mejor_genetico_veg','offset_secuestro_CO2_organico','offset_ERNC_riego']
lulucf_offsets = ['offset_capturaCO2_bosquenativo','offset_fomento_forestacion']
ippu_offsets = ['Electrificacion_motriz_mineria','Electrificacion_motriz_industria','SST_Industria_mineria','Electrificacion_motriz_cobre', 
		        'Electrificacion_motriz_comercial','Generacion_biogas','Electrificacion_termica']
others_offsets = []
labels = ['IPPU','Energy','Waste','Agriculture','Others', 'LULUCF']

def take_offset(x):
    a= data_offsets.loc["{:<30}".format(x[:30])][['offset','agno']]
    a.set_index('agno', inplace=True)
    return a
def add_offset(x,y):
    offsets.set_index(x)
    offsets[x]= pd.concat([offsets[x],take_offset(y)], axis=1).sum(axis=1)
    return offsets[x]
def loop_offset(y,z):
    for offset in z:
        add_offset(y,offset)
    results[y]=offsets[y].copy()
    results[y]= pd.to_numeric(results[y]).fillna(0)

loop_offset('IPPU',ippu_offsets)
loop_offset('Energy',energy_offsets)
loop_offset('Waste',waste_offsets)
loop_offset('Agriculture',agriculture_offsets)
loop_offset('LULUCF',lulucf_offsets)
loop_offset('Others',others_offsets)

#Emisiones por sector IPCC
emisiones = pd.DataFrame()
emisiones['IPPU']= data_emisiones[["industria y mineria","otras industrias energia","procesos industriales"]].sum(axis=1)
emisiones['Energy']= data_emisiones[["residencial","comercial","publico","transporte","generacion electrica","emisiones fugitivas",]].sum(axis=1)
emisiones['Waste']= data_emisiones[["residuos",]].sum(axis=1)
emisiones['Agriculture']= data_emisiones[["agricultura"]].sum(axis=1)
emisiones['Others']= data_emisiones[["otros sectores"]].sum(axis=1)

#Subtract Offsets
emisiones_final = pd.DataFrame()
emisiones_final['IPPU']= emisiones['IPPU'].subtract(results['IPPU'].reset_index(drop=True, inplace=False), axis=0)
emisiones_final['Energy']= emisiones['Energy'].subtract(results['Energy'].reset_index(drop=True, inplace=False), axis=0)
emisiones_final['Waste']= emisiones['Waste'].subtract(results['Waste'].reset_index(drop=True, inplace=False), axis=0)
emisiones_final['Agriculture']= emisiones['Agriculture'].subtract(results['Agriculture'].reset_index(drop=True, inplace=False), axis=0)
emisiones_final['Others']= emisiones['Others'].subtract(results['Others'].reset_index(drop=True, inplace=False), axis=0)
emisiones_final['LULUCF']= -results['LULUCF'].copy().reset_index(drop=True, inplace=False)

#Plot Sectorial Offsets
plt.plot(results)
#plt.title('Sectorial Emission Reductions Projects')
plt.ylabel('Emission Reductions [MtCO2e]')
plt.xlabel('Year')
plt.legend(['IPPU','Energy','Waste','Agriculture','LULUCF','Others'], fontsize =8)
plt.savefig('Sectorial ERP.png', dpi=300, bbox_inches='tight')
plt.show()

#Grafico de emisiones por periodo
emisiones_final.set_index(data_emisiones['agno'], inplace=True)
def plot_period (a,b,c):
    if a == 2020:
        plt.legend(fontsize=7, loc=1)
        #plt.title('Scenario 1')
        emisiones_periodo = int(emisiones_final.loc[a:b].sum().sum())
        plt.plot([b, b], [c/(b-a+1), 0], color='dimgray', linestyle='-', linewidth=1)
        plt.plot([a, a], [c/(b-a+1), 0], color='dimgray', linestyle='-', linewidth=1)
        plt.plot([a, b], [c/(b-a+1), c/(b-a+1)], color='dimgray', linestyle='-', linewidth=1)
    else:
        emisiones_periodo = int(emisiones_final.loc[a+1:b].sum().sum())
        plt.plot([b, b], [c/(b-a), 0], color='dimgray', linestyle='-', linewidth=1)
        plt.plot([a, a], [c/(b-a), 0], color='dimgray', linestyle='-', linewidth=1)
        plt.plot([a, b], [c/(b-a), c/(b-a)], color='dimgray', linestyle='-', linewidth=1)
    plt.stackplot(range(a,b+1),emisiones_final['IPPU'].loc[a:b], emisiones_final['Energy'].loc[a:b]
                  ,emisiones_final['Waste'].loc[a:b],emisiones_final['Agriculture'].loc[a:b]
                  ,emisiones_final['Others'].loc[a:b], colors=['tab:blue','tab:orange','tab:green','tab:purple','tab:red'], labels = labels)
    plt.stackplot(range(a,b+1), emisiones_final['LULUCF'].loc[a:b],colors='tab:cyan', labels = ['Offsets',])
    plt.text((a+b)/2-2,35,"CB \n"+str(c)+'\nProjection \n'+ str(emisiones_periodo), fontsize=8)
   
    plt.ylim(ymax = 150)
    plt.xlim(xmax = 2050)
    plt.savefig(nombre_escenario+'_CB.png', dpi=300)
    plt.ylabel('Emissions [MtCO2e]')
    if a == 2020:
        plt.legend(fontsize=7, loc=1)
    plt.xlabel('Year')
    
plot_period(2020,2030,1100) #start year, end year and ammount of the budget.  
plot_period(2030,2035, 434)
plot_period(2035,2040,399)
plot_period(2040,2045,354)
plot_period(2045,2050,332)

plt.show()

#Costs
reduction_projects= waste_offsets.copy() + energy_offsets.copy() + ippu_offsets.copy() + agriculture_offsets.copy() + others_offsets.copy() + lulucf_offsets.copy()
data_input_offsets.set_index('Offset', inplace = True)
data_final = pd.DataFrame()
def precio_offset(x):
    j = data_input_offsets.at[x,'Costo']
    l = j*take_offset(x).astype(bool).rename(columns = {'offset':str(x)})
    data_results = pd.DataFrame(l, index = take_offset(x).index)
    return data_results
for x in reduction_projects:
    data_final = pd.concat((data_final,precio_offset(x)), axis=1)

    j = data_input_offsets.at['Ley_eficiencia_energetica','Costo']
    l = j*take_offset(x).astype(bool).rename(columns = {'offset':str(x)})

precio_offset('Ley_eficiencia_energetica')
#Plot Expenses
data_costs = data_costs.drop(['emisiones_otros_sec','emisiones_gen'], axis=1).set_index('agno')
plt.stackplot(data_costs.index, data_costs['costo_inversion'],data_costs['costo_inversion_tx'],data_costs['coma'],
                  data_costs['costo_operacion_otros_sec'],data_costs['costo_operacion_generacion'], 
                  labels = ['CAPEX','CAPEX Transmission', 'OPEX', 'OPEX Others', 'OPEX E. Generation'])
plt.legend(fontsize = 7, loc =2)   
#plt.title('Expenses for the Electricity Generation, Industry and Mining, and Transport Sector')
plt.savefig(nombre_escenario+'_Expenses.png', dpi=300)
plt.show()

def plot_erp(sector):
    sector_plot = pd.DataFrame()
    toplot = pd.DataFrame()
    for x in sector:
        sector_plot = pd.concat((sector_plot,precio_offset(x)), axis=1)        
        toplot = sector_plot.copy()
    plt.stackplot(data_costs.index, toplot.sum(axis=1)) 
    #plt.title('E. Reduction Projects Expenses by Sector')
    plt.legend(['Energy','Waste','Agriculture','LULUCF','IPPU','Others'], loc = 2)
plot_erp(energy_offsets)
plot_erp(waste_offsets)
plot_erp(agriculture_offsets)
plot_erp(lulucf_offsets)
plot_erp(ippu_offsets)
plt.savefig(nombre_escenario+'_Expenses_ERP.png', dpi=300)     