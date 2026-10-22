
# MAIN FUNCTION TO CALL THE ISM MODULE

from ism.src.ism import ism

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r'C:\\Users\\mbell\\OneDrive\\Escritorio\\EODT\\EODT_Mario\\auxiliary'
indir = r"C:\\Users\\mbell\\OneDrive\\Escritorio\\EODT\\SHARED\\\EODP-TS-E2E\\sgm_out" # small scene
outdir = r"C:\\Users\\mbell\\OneDrive\\Escritorio\\EODT\\SHARED\\\EODP-TS-E2E\\output_Mario"

# Initialise the ISM
myIsm = ism(auxdir, indir, outdir)
myIsm.processModule()
