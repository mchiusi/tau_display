import argparse
import uproot
import numpy as np
import matplotlib.pyplot as plt

def define_datasets():
    filename = "/data_CMS/cms/motta/CaloL1calibraton/L1NTuples/Muon__Run2022G-PromptReco-v1__AOD__GT124XdataRun3Promptv10_CaloParams2022v33newCalib_data_reco_json/GoodNtuples/Ntuple_1157.root"
    tower_tree_name = "l1CaloTowerEmuTree/L1CaloTowerTree"
    l1_tree_name    = "l1UpgradeEmuTree/L1UpgradeTree"
    
    tower_tree  = uproot.open(filename)[tower_tree_name]
    tower_ds    = tower_tree.arrays(['ieta','iphi','iet'], entry_stop=50)
    
    l1_tree = uproot.open(filename)[l1_tree_name]
    l1_ds   = l1_tree.arrays(['tauIEta','tauIPhi','nTaus','tauIEt'], entry_stop=50)

    return tower_ds, l1_ds

def skim_towers(seed_eta, seed_phi, towers):
    # Define the ranges
    ieta_range = range(seed_eta - 2, seed_eta + 3)
    iphi_range = range(seed_phi - 4, seed_phi + 4)
   
    # Create a boolean mask for the specified conditions
    mask = np.logical_and.reduce([
        np.isin(towers['ieta'], np.array(ieta_range)),
        np.isin(towers['iphi'], np.array(iphi_range))
    ])
    
    # Apply the mask to select the entries
    selected_data = {
        'ieta': np.array(towers['ieta'])[mask],
        'iphi': np.array(towers['iphi'])[mask],
        'iet':  np.array(towers['iet'])[mask]
    }
    return selected_data

def plot_event(event, args, seed_eta=0, seed_phi=0):
    grid = np.zeros((6, 9))
   
    # Fill the grid with iet values
    for i, (ieta_val, iphi_val, iet_val) in enumerate(zip(event['ieta'], event['iphi'], event['iet'])):
        grid_row = (ieta_val - seed_eta) - 2
        grid_col = (iphi_val - seed_phi) + 4
        grid[grid_row, grid_col] = iet_val

    print(grid)
    
    # Plot the heat map
    plt.imshow(grid)
    plt.yticks(np.arange(5), np.flip(np.array(range(seed_eta-2, seed_eta+3))))
    plt.xticks(np.arange(8), np.array(range(seed_phi-4, seed_phi+4)))

    plt.colorbar(label='iet')
    plt.title('Grid Plot based on Tau energy')
    plt.savefig('example_plot.pdf')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A script that chooses between --channel and --module.")
    parser.add_argument("--full_event", action="store_true", help="Display the full CMS tower view")
    args = parser.parse_args()

    tower_ds, l1_ds = define_datasets()
    
    # selecting the first event
    ev_0 = l1_ds[1]

    print("For this event, found {} taus".format(ev_0['nTaus']))
    for i_tau in range(ev_0['nTaus']):
        seed_eta = ev_0['tauIEta'][i_tau]
        seed_phi = ev_0['tauIPhi'][i_tau]
        if seed_phi > 72: continue

        print(seed_eta, seed_phi)
        skimmed_event = skim_towers(seed_eta, seed_phi, tower_ds[1])
        if len(skimmed_event['ieta']) > 2: 
            plot_event(skimmed_event, args, seed_eta, seed_phi)
            break
