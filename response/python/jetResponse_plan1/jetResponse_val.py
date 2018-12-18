''' FWLiteReader - jet-by-jet matching validation
'''
# Standard imports
import os
import logging
import ROOT
import array

#RootTools
from RootTools.core.standard import *

#Helper
import JetMET.tools.helpers as helpers
from math import pi

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel', 
      action='store',
      nargs='?',
      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],
      default='INFO',
      help="Log level for logging"
)

args = argParser.parse_args()
logger = get_logger(args.logLevel, logFile = None)

max_events  = -1  # Process all events
max_files   = 50   # Process all or fewer number of files

#files from Kenichi Feb. 2016
#sample_prefix = "kenichi_private_qcd_"
#/afs/cern.ch/user/d/deguio/public/ForKen/Plan0_10024.0_TTbar_13.txt
#/afs/cern.ch/user/d/deguio/public/ForKen/Plan0_10043.0_QCDForPF_14TeV.txt
#/afs/cern.ch/user/d/deguio/public/ForKen/Plan1_10024.0_TTbar_13.txt
#/afs/cern.ch/user/d/deguio/public/ForKen/Plan1_10043.0_QCDForPF_14TeV.txt
#files_ttbar_plan0   = [ 'root://eoscms.cern.ch/%s'%s.rstrip() for s in open('/afs/cern.ch/user/d/deguio/public/ForKen/Plan0_10024.0_TTbar_13.txt').readlines() if os.path.split(s)[-1].startswith('step3_') ]
#files_ttbar_plan1   = [ 'root://eoscms.cern.ch/%s'%s.rstrip() for s in open('/afs/cern.ch/user/d/deguio/public/ForKen/Plan1_10024.0_TTbar_13.txt').readlines() if os.path.split(s)[-1].startswith('step3_') ]
files_qcd_plan0     = [ 'root://kodiak-se.baylor.edu/%s'%s.rstrip() for s in open('QCD4PF_noPU_ref.txt').readlines() if os.path.split(s)[-1].startswith('step3_') ]
files_qcd_plan1     = [ 'root://kodiak-se.baylor.edu/%s'%s.rstrip() for s in open('QCD4PF_noPU_update.txt').readlines() if os.path.split(s)[-1].startswith('step3_') ]

# files from Federico March 3rd
veto = ['step3_800.root'] # broken files
sample_prefix = "qcd4pf_new_"
dir_qcd_plan0 = "/cms/data/store/user/hatake/crab_outputs/QCDForPF/CMSSW_10_4_0_pre3_Step3_v1/181213_104315/0000/"
dir_qcd_plan1 = "/cms/data/store/user/hatake/crab_outputs/QCDForPF/CMSSW_10_4_0_pre3_Step3_PF_use_rawECAL_for_HadronCalib_v2/181214_170857/0000/"

# Make two list of files 
#files_qcd_plan0 = []
#for f in os.listdir(dir_qcd_plan0):
#    if os.path.isfile(os.path.join(dir_qcd_plan0, f)) and f.startswith('step3_1') and not any(v in f for v in veto):
#        files_qcd_plan0.append( os.path.join(dir_qcd_plan0, f) )

#files_qcd_plan1 = []
#for f in os.listdir(dir_qcd_plan1):
#    if os.path.isfile(os.path.join(dir_qcd_plan1, f)) and f.startswith('step3_1') and not any(v in f for v in veto):
#        files_qcd_plan1.append( os.path.join(dir_qcd_plan1, f) )

plot_directory = "/home/hatake/ana_cms/PF/CMSSW_10_4_0_pre4/src/JetMET/response/python/jetResponse_plan1/plots/" # where your plots go

# Make RootTools sample instance
plan0 = FWLiteSample.fromFiles("plan0", files = files_qcd_plan0, maxN = max_files)
plan1 = FWLiteSample.fromFiles("plan1", files = files_qcd_plan1, maxN = max_files)

plan1RefJet = False  # the reference should be the plan-1 jet
refname = "test" if plan1RefJet else "ref"
#refname = "plan1" if plan1RefJet else "plan0"
pt_threshold = 10
preprefix = "refIs%s_%s_pt%i" % ( refname, sample_prefix, pt_threshold )

# define TProfiles
pt_thresholds = [ 10**(x/10.) for x in range(11,36) ] 

# HEP17 phi boundary +/-0.2
#phi_low  = 310/180.*pi - 0.2 - 2*pi
#phi_high = 330/180.*pi + 0.2 - 2*pi

# book keeping for plots
resp = {}
resp_eta = {}
resp_pt = {}
#resp_eta_HEP17 = {}
#resp_eta_nonHEP17 = {}
resp_eta_phi = {}

# 1D Profile inclusive
resp_eta = ROOT.TProfile("resp_eta", "resp_eta", 26, -5.2, 5.2 )
resp_eta.style = styles.lineStyle( ROOT.kBlack )
resp_eta.legendText = "all" 

resp_eta_phi = ROOT.TProfile2D("resp_eta_phi", "resp_eta", 26, -5.2, 5.2, 20,-pi,pi )

met_2D      = ROOT.TH2D("met_2D", "met_2D", 100,0,100,100,0,100 )
met_2D_wide = ROOT.TH2D("met_2D", "met_2D", 500,0,500,500,0,500 )

resp={}
eta_thresholds = [(0,1.1), (1.3,3), (3,5)]
eta_color = {(0,1.1):ROOT.kBlack, (1.3,3):ROOT.kRed, (3,5):ROOT.kBlue}
for i_eta_th, eta_th in enumerate( eta_thresholds ):
    resp[eta_th] = ROOT.TProfile("response", "response", 36, -pi, pi )
    resp[eta_th].style = styles.lineStyle(eta_color[eta_th] )
    resp[eta_th].legendText = "%2.1f #leq #eta < %2.1f"%eta_th

resp_pt={}
eta_color = {(0,1.1):ROOT.kBlack, (1.3,3):ROOT.kRed, (3,5):ROOT.kBlue}
thresholds = [10**(x/10.) for x in range(11,36)] 
for i_eta_th, eta_th in enumerate( eta_thresholds ):
    resp_pt[eta_th] = ROOT.TProfile("response_pt", "response_pt", len(thresholds)-1, array.array('d', thresholds))
    resp_pt[eta_th].style = styles.lineStyle(eta_color[eta_th] )
    resp_pt[eta_th].legendText = "%2.1f #leq #eta < %2.1f"%eta_th

## This is how you define the products which should be read. Structure is {'name1':{'type':'<type1>', 'label':(<label1>)}, etc.}
products = {
    'jets':      {'type': 'vector<reco::PFJet>', 'label':"ak4PFJetsCHS"},
    'met':      {'type':'vector<reco::PFMET>', 'label': "pfMet"},
    #'pfRecHitsHBHE':{ 'label':("particleFlowRecHitHBHE"), 'type':"vector<reco::PFRecHit>"},
    #'caloRecHits':  { 'label':("reducedHcalRecHits"), 'type':'edm::SortedCollection<HBHERecHit,edm::StrictWeakOrdering<HBHERecHit> >'},
    #'clusterHCAL':  {  'label': "particleFlowClusterHCAL", "type":"vector<reco::PFCluster>"},
    #'pf':           { 'label':('particleFlow'), 'type':'vector<reco::PFCandidate>'},
    }

r1 = plan1.fwliteReader( products=products )
r2 = plan0.fwliteReader( products=products )

r1.start()
runs_1 = set()
position_r1 = {}
count=0
while r1.run():
    # FIXME IMPORTANT: Fede/Ken did NOT produce unique event/run/lumi, therefore I need to add the filename to the key since it is needed to uniquely identify an event
    # For any centrally produced sample, use  
    # position_r1[r1.evt] = r1.position-1 

    file_n1 =  int(os.path.split(r1.sample.events._filenames[r1.sample.events.fileIndex()])[-1].split('.')[0].split('_')[1])
    position_r1[(r1.evt, file_n1)] = r1.position-1 
    
    count+=1
    if max_events is not None and max_events>0 and count>=max_events:break

r2.start()
runs_2 = set()
position_r2 = {}
count=0
while r2.run():
    # FIXME IMPORTANT: Fede/Ken did NOT produce unique event/run/lumi, therefore I need to add the filename to the key since it is needed to uniquely identify an event
    # For any centrally produced sample, use  
    # position_r2[r2.evt] = r2.position-1 

    file_n2 =  int(os.path.split(r2.sample.events._filenames[r2.sample.events.fileIndex()])[-1].split('.')[0].split('_')[1])
    position_r2[(r2.evt, file_n2)] = r2.position-1

    count+=1
    if max_events is not None and max_events>0 and count>=max_events:break

logger.info( "Have %i events in first samle and %i in second", len(position_r1), len(position_r2) )

# Fast intersect
intersec = set(position_r1.keys()).intersection(set(position_r2.keys()))
positions = [(position_r1[i], position_r2[i]) for i in intersec]

# Without sorting, there is a jump between files with almost every event -> extremly slow
positions.sort()
logger.info("Have %i events in common.", len(intersec))

#Looping over common events
for i, p in enumerate(positions):
    # Set the readers to common positions 
    p1,p2 = p
    r1.goToPosition(p1)
    r2.goToPosition(p2)
    if i%100==0: logger.info("At %i/%i of common events.", i, len(positions))

    # Fill per-event histos
    met_2D.Fill( r2.products['met'][0].pt(), r1.products['met'][0].pt() )
    met_2D_wide.Fill( r2.products['met'][0].pt(), r1.products['met'][0].pt() )

    # get the jets
    jets1_ = [ j for j in r1.products['jets'] ] #if helpers.jetID( j )]
    jets2_ = [ j for j in r2.products['jets'] ] #if helpers.jetID( j )]

    # for convinience, make dictionaries from the jets
    jets1 = [{'pt':j.pt(), 'eta':j.eta(), 'phi':j.phi(), 'j':j } for j in jets1_] 
    jets2 = [{'pt':j.pt(), 'eta':j.eta(), 'phi':j.phi(), 'j':j } for j in jets2_]

    # zip & match jets
    for c in zip(jets1, jets2):
        if helpers.deltaR2(*c)<0.2**2:

            r = c[0]['pt']/c[1]['pt']
            
            ref_jet = c[0] if plan1RefJet else c[1]
            # r1=plan1 -> jets1 -> c[0]
            # r2=plan0 -> jets2 -> c[1]
            # r=plan1/plan0=update/ref
            
            if not ref_jet['pt']>pt_threshold: continue
            if not ( helpers.jetID(c[0]['j']) and helpers.jetID(c[1]['j']) ): continue

            # 2D eta, phi
            resp_eta_phi.Fill( ref_jet['eta'], ref_jet['phi'], r )

            # inclusive eta
            resp_eta.Fill( ref_jet['eta'], r )

            for eta_th in eta_thresholds:
                if ref_jet['eta']>=eta_th[0] and ref_jet['eta']<eta_th[1]:
                    resp[eta_th].Fill( ref_jet['phi'], r )
                    break

            for eta_th in eta_thresholds:
                if ref_jet['eta']>=eta_th[0] and ref_jet['eta']<eta_th[1]:
                    resp_pt[eta_th].Fill( ref_jet['pt'], r )
                    break

# Make plots
prefix = preprefix + "_" + plan1.name + ("_max_events_%s_"%max_events if max_events is not None and max_events>0 else "" )

# Make TH2F from TProfiles
profiles = [resp[t] for t in eta_thresholds]
histos = [ [h.ProjectionX()] for h in profiles ]
for i, h in enumerate(histos):
    h[0].__dict__.update(profiles[i].__dict__)

jetResponsePlot = Plot.fromHisto(name = prefix+"jetResponseRatio_relval", histos = histos, texX = "%s Jet #phi"%refname , texY = "response ratio update/ref" )
plotting.draw(jetResponsePlot, plot_directory = plot_directory, ratio = None, logY = False, logX = False, yRange=(0.7,1.2))

profiles = [resp_pt[t] for t in eta_thresholds]
histos = [ [h.ProjectionX()] for h in profiles ]
for i, h in enumerate(histos):
    h[0].__dict__.update(profiles[i].__dict__)

jetResponsePlot_pt = Plot.fromHisto(name = prefix+"jetResponseRatio_relval_pt", histos = histos, texX = "%s Jet pt"%refname , texY = "response ratio update/ref" )
plotting.draw(jetResponsePlot_pt, plot_directory = plot_directory, ratio = None, logY = False, logX = False, yRange=(0.7,1.2))

profiles = [resp_eta]
histos = [ [h.ProjectionX()] for h in profiles ]
for i, h in enumerate(histos):
    h[0].__dict__.update(profiles[i].__dict__)

jetResponsePlot_eta = Plot.fromHisto(name = prefix+"jetResponseRatio_relVal_eta", histos = histos, texX = "%s Jet #eta"%refname , texY = "response ratio update/ref" )
plotting.draw(jetResponsePlot_eta, plot_directory = plot_directory, ratio = None, logY = False, logX = False, yRange=(0.7,1.2))

h2d = resp_eta_phi.ProjectionXY()
plotting.draw2D(
    plot = Plot2D.fromHisto(name = prefix+"jetResponseRatio_2D", histos = [[h2d]], texX = "%s jet #eta"%refname, texY = "%s jet #phi"%refname),
    plot_directory = plot_directory,
    logX = False, logY = False, logZ = False, zRange = (0.95,1.05),
)

plotting.draw2D(
    plot = Plot2D.fromHisto(name = prefix+"met_2D", histos = [[met_2D]], texX = "ref PF E_{T}^{miss}", texY = "update PF E_{T}^{miss}"),
    plot_directory = plot_directory,
    logX = False, logY = False, logZ = False,
)

plotting.draw2D(
    plot = Plot2D.fromHisto(name = prefix+"met_2D_wide", histos = [[met_2D_wide]], texX = "ref PF E_{T}^{miss}", texY = "update PF E_{T}^{miss}"),
    plot_directory = plot_directory,
    logX = False, logY = False, logZ = False,
)
