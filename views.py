from django.shortcuts import render
from django.http import HttpResponse
import math
import numpy as np
import pandas as pd
from pandas import DataFrame
import sys
    
    # Create your views here.

def home(request):
    return render(request,'home.html')

def add(request):

    ws_ = float(request.POST["ws_"])
    z_ = float(request.POST["z_"])
    knee_ = float(request.POST["knee_"])
    pspan_ = float(request.POST["pspan_"])
    pitch_ = float(request.POST["pitch_"])
    len_ = float(request.POST["len_"])
    span_ = float(request.POST["span_"])
        
    con = {'c8075 0': 0.345, 'c8095 0': 0.445, 'b8075 0': 0.535, 'b8095 0': 0.586 }
    
    dl_=0.1
    ll_=0.1
    wl_=(0.6*ws_**2)/1000
    sl_=3*z_*1*1
    #Purlin Design:
    h_=knee_+(pspan_/4*math.tan(pitch_*3.14/180))
    a_=min(0.2*len_,0.2*span_,h_)
    #External pressure coefficient, Cpe

    b1_=-0.9
    b2_=-0.7+(h_/pspan_-0.5)*(-0.3/0.5)
    b3_=0.2
    b4_=-0.3
    b5_=0

    b11_=min((b1_-b4_)*0.9,(b1_-b5_)*0.9)
    b12_=min((b2_-b4_)*0.9,(b2_-b5_)*0.9)
    b13_=min((b3_-b4_)*0.9,(b3_-b5_)*0.9)

    "Load combination (ULS):-"
    w11_=1.35*dl_
    w12_=1.2*dl_+1.5*ll_
    w13_=0.9*dl_+wl_*b11_
    w14_=0.9*dl_+wl_*b12_
    w15_=1.2*dl_+wl_*b13_

    "Moment demand (ULS):"
    bm1_=(w11_*span_**2)/8
    bm2_=(w12_*span_**2)/8
    bm3_=(w13_*span_**2)/8+(0.5*w13_*a_**2)/8
    bm4_=(w14_*span_**2)/8+(0.5*w14_*a_*(span_-a_*0.5))/4
    bm5_=(w15_*span_**2)/8+(0.5*w15_*a_*(span_-a_*0.5))/4
    bm_pur=max(abs(bm1_),abs(bm2_),abs(bm3_),abs(bm4_),abs(bm5_))
    

    "Required Iexx for SLS load combinations:"
    I11_=(0.9765*dl_*(span_*1000)**3)/200000
    I12_=(0.9765*0.814*wl_*b11_*(span_*1000)**3)/200000
    I13_=(0.9765*0.814*wl_*b12_*(span_*1000)**3)/200000
    I14_=(0.9765*0.814*wl_*b13_*(span_*1000)**3)/200000
    I_pur=max(I11_,I12_,I13_,I14_)

    
    df = pd.DataFrame({
    'section' : ['C8075(0)','C8075(1)','C8075(2)','C8095(0)','C8095(1)','C8095(2)','B8075(0)','B8075(1)','B8075(2)','B8095(0)','B8095(1)','B8095(2)'],
    '3m' : ['0.259','0.55','0.78','0.237','0.682','1.11','0.586','1.406','1.74','0.821','2.12','2.58'],
    '3.5m' : ['0.226','0.45','0.71','0.186','0.54','0.97','0.49','1.19','1.65','0.64','1.81','2.54'],
    '4m' : ['0.21','0.42','0.63','0.15','0.45','0.81','0.42','0.99','1.53','0.51','1.47','2.29'],
    'Ieff' : ['92000','92000','92000','119900','119900','119900','184000','184000','184000','239880','239880','239880']
    })

    df['3m'] = pd.to_numeric(df['3m'], downcast='float')
    df['3.5m'] = pd.to_numeric(df['3m'], downcast='float')
    df['4m'] = pd.to_numeric(df['4m'], downcast='float')
    df['Ieff'] = pd.to_numeric(df['4m'], downcast='float')

    if span_==3:
        df['spacing'] = round((df['3m']/(bm_pur/1000)), 0)
    elif span_==4:
        df['spacing'] = round((df['3.5m']/(bm_pur/1000)), 0)
    else:
        df['spacing'] = round((df['4m']/(bm_pur/1000)), 0)
    
    df['spacing1'] = round((df['Ieff']/(I_pur/1000)), 0)

    df.spacing = np.where(df.spacing < df.spacing1, df.spacing1, df.spacing)
    df.spacing = np.where(df.spacing > 1500, 1500, df.spacing)
    
       
    del df['4m']
    del df['3m']
    del df['Ieff']
    del df['spacing1']

    #Sidewall Girt Design:

    #External pressure coefficient, Cpe

    c1_=-0.65
    c2_=0.7

    b21_=min((c1_-b4_)*0.9,(c1_-b5_)*0.9)
    b22_=max((c2_-b4_)*0.9,(c2_-b5_)*0.9)


    #"Load combination (ULS):-"
    w21_=wl_*b21_
    w22_=wl_*b22_

    #"Moment demand (ULS):"
    bm21_=(w21_*span_**2)/8+(0.5*w21_*a_**2)/8
    bm22_=(w22_*span_**2)/8+(0.5*w22_*a_*(span_-a_*0.5))/4
    bm_girt=max(abs(bm21_),abs(bm22_))

    #"Required Iexx for SLS load combinations:"
    I21_=(0.9765*0.814*wl_*b21_*(span_*1000)**3)/200000
    I22_=(0.9765*0.814*wl_*b22_*(span_*1000)**3)/200000
    I_sgirt=max(I21_,I22_)

    df1 = pd.DataFrame({
    'section' : ['C8075(0)','C8075(1)','C8075(2)','C8095(0)','C8095(1)','C8095(2)','B8075(0)','B8075(1)','B8075(2)','B8095(0)','B8095(1)','B8095(2)'],
    '3m' : ['0.259','0.55','0.78','0.237','0.682','1.11','0.586','1.406','1.74','0.821','2.12','2.58'],
    '3.5m' : ['0.226','0.45','0.71','0.186','0.54','0.97','0.49','1.19','1.65','0.64','1.81','2.54'],
    '4m' : ['0.21','0.42','0.63','0.15','0.45','0.81','0.42','0.99','1.53','0.51','1.47','2.29'],
    'Ieff' : ['92000','92000','92000','119900','119900','119900','184000','184000','184000','239880','239880','239880']
    })

    df1['3m'] = pd.to_numeric(df1['3m'], downcast='float')
    df1['3.5m'] = pd.to_numeric(df1['3m'], downcast='float')
    df1['4m'] = pd.to_numeric(df1['4m'], downcast='float')
    df1['Ieff'] = pd.to_numeric(df1['4m'], downcast='float')

    if span_==3:
        df1['spacing'] = round((df1['3m']/(bm_girt/1000)), 0)
    elif span_==4:
        df1['spacing'] = round((df1['3.5m']/(bm_girt/1000)), 0)
    else:
        df1['spacing'] = round((df1['4m']/(bm_girt/1000)), 0)
    
    df1['spacing1'] = round((df1['Ieff']/(I_sgirt/1000)), 0)

    df1.spacing = np.where(df1.spacing < df1.spacing1, df1.spacing1, df1.spacing)
    df1.spacing = np.where(df1.spacing > 1500, 1500, df1.spacing)
    
       
    del df1['4m']
    del df1['3m']
    del df1['Ieff']
    del df1['spacing1']

    #Endwall Girt Design:
    if pspan_/2<=span_:
        leg_=span_
    else:
        leg_=pspan_/4
    #External pressure coefficient, Cpe
    c1_=-0.65
    c2_=0.7

    b31_=min((c1_-b4_)*0.9,(c1_-b5_)*0.9)
    b32_=max((c2_-b4_)*0.9,(c2_-b5_)*0.9)


    #"Load combination (ULS):-"
    w31_=wl_*b31_
    w32_=wl_*b32_

    #"Moment demand (ULS):"
    bm31_=(w31_*leg_**2)/8+(0.5*w31_*a_**2)/8
    bm32_=(w32_*leg_**2)/8+(0.5*w32_*a_*(leg_-a_*0.5))/4
    bm_egirt=max(abs(bm31_),abs(bm32_))

    #"Required Iexx for SLS load combinations:"
    I31_=(0.9765*0.814*wl_*b31_*(leg_*1000)**3)/200000
    I32_=(0.9765*0.814*wl_*b32_*(leg_*1000)**3)/200000
    I_egirt=max(I31_,I32_)

    df2 = pd.DataFrame({
    'section' : ['C8075(0)','C8075(1)','C8075(2)','C8095(0)','C8095(1)','C8095(2)','B8075(0)','B8075(1)','B8075(2)','B8095(0)','B8095(1)','B8095(2)'],
    '3m' : ['0.259','0.55','0.78','0.237','0.682','1.11','0.586','1.406','1.74','0.821','2.12','2.58'],
    '3.5m' : ['0.226','0.45','0.71','0.186','0.54','0.97','0.49','1.19','1.65','0.64','1.81','2.54'],
    '4m' : ['0.21','0.42','0.63','0.15','0.45','0.81','0.42','0.99','1.53','0.51','1.47','2.29'],
    'Ieff' : ['92000','92000','92000','119900','119900','119900','184000','184000','184000','239880','239880','239880']
    })

    df2['3m'] = pd.to_numeric(df2['3m'], downcast='float')
    df2['3.5m'] = pd.to_numeric(df2['3m'], downcast='float')
    df2['4m'] = pd.to_numeric(df2['4m'], downcast='float')
    df2['Ieff'] = pd.to_numeric(df2['4m'], downcast='float')

    if leg_<=3:
        df2['spacing'] = round((df2['3m']/(bm_egirt/1000)), 0)
    elif span_<=3.5:
        df2['spacing'] = round((df2['3.5m']/(bm_egirt/1000)), 0)
    else:
        df2['spacing'] = round((df2['4m']/(bm_egirt/1000)), 0)
    
    df2['spacing1'] = round((df2['Ieff']/(I_egirt/1000)), 0)

    df2.spacing = np.where(df2.spacing < df2.spacing1, df2.spacing1, df2.spacing)
    df2.spacing = np.where(df2.spacing > 1500, 1500, df2.spacing)

               
    return render(request, 'result.html', {'pspan_': pspan_, 'len_': len_, 'span_': span_, 'knee_': knee_, 'pitch_': pitch_, 'purlin_':df, 'sidegirt_':df1, 'endgirt_':df2})
    



       


