
# MAIN FUNCTION TO CALL THE L1B MODULE

from l1b.src.l1b import l1b

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r'C:\\Users\\mbell\\OneDrive\\Escritorio\\EODT\\EODT_Mario\\auxiliary'
#indir = r"C:\\Users\\mbell\\OneDrive\\Escritorio\\EODT\\SHARED\\EODP_TER_2021\\EODP-TS-L1B\\input"
indir =r"C:\\Users\\mbell\\OneDrive\\Escritorio\\EODT\\SHARED\\\EODP-TS-E2E\\output_Mario" # Esto es el output de ISM E2E
#outdir = r"C:\\Users\\mbell\\OneDrive\\Escritorio\\EODT\\SHARED\\EODP_TER_2021\\EODP-TS-L1B\\output_Mario_noteq"
outdir = r"C:\\Users\\mbell\\OneDrive\\Escritorio\\EODT\\SHARED\\EODP_TER_2021\\EODP-TS-L1B\\output_E2E"

# Initialise the ISM
myL1b = l1b(auxdir, indir, outdir)
myL1b.processModule()
