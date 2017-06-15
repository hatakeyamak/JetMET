# 1D spike cleaning
thr = [
( -2.650, -2.500,  -1.35, -1.05 ),
( -2.964, -2.650,  -1.10, -0.80 ),
( -2.964, -2.650,  -0.25, 0.1 ),
( -2.964, -2.650,  -3.14159, -2.8 ),
( -2.964, -2.650,  2.9, 3.14159 ),
( 2.650, 2.964,  -2., -1.6 ),
( 2.650, 3.139,  0, 0.25 ),
]

e = "Jet_eta[probe_jet_index]"
p = "Jet_phi[probe_jet_index]"

jet_spike_cleaning = '(!('+"||".join( [ "%s>%4.3f&&%s<%4.3f&&%s>%4.3f&&%s<%4.3f" % ( e, th[0], e, th[1], p, th[2], p, th[3] ) for th in thr ] ) + '))'

# Mikko cleaning
jet_cleaning = "Sum$(Jet_pt*Jet_isHot)<20"
